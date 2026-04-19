/**
 * @file vk_resource.cpp
 * @brief Vulkan resource methods: upload, download, copy, and batch texture upload.
 *
 * This file implements the vk.Resource Python type, which represents a Vulkan
 * buffer or image. It provides methods for data transfer between host and device,
 * as well as resource-to-resource copies.
 */

#include "vk_resource.h"
#include "vk_utils.h"
#include <cstring>
#include <functional>

/* ----------------------------------------------------------------------------
   RAII wrapper for Python buffer objects
   ------------------------------------------------------------------------- */
struct PyBufferGuard {
    Py_buffer view;
    bool owned = false;

    PyBufferGuard() = default;
    ~PyBufferGuard() { if (owned) PyBuffer_Release(&view); }

    // Disable copy
    PyBufferGuard(const PyBufferGuard&) = delete;
    PyBufferGuard& operator=(const PyBufferGuard&) = delete;

    // Enable move
    PyBufferGuard(PyBufferGuard&& other) noexcept
        : view(other.view), owned(other.owned) {
        other.owned = false;
    }
    PyBufferGuard& operator=(PyBufferGuard&& other) noexcept {
        if (this != &other) {
            if (owned) PyBuffer_Release(&view);
            view = other.view;
            owned = other.owned;
            other.owned = false;
        }
        return *this;
    }

    bool acquire(PyObject *obj, int flags = PyBUF_SIMPLE) {
        if (PyObject_GetBuffer(obj, &view, flags) < 0) return false;
        owned = true;
        return true;
    }

    void release() { if (owned) { PyBuffer_Release(&view); owned = false; } }
};

/* ----------------------------------------------------------------------------
   Resource deallocator
   ------------------------------------------------------------------------- */
void vk_Resource_dealloc(vk_Resource *self) {
    if (self->py_device) {
        VkDevice dev = self->py_device->device;
        if (self->image_view)   vkDestroyImageView(dev, self->image_view, nullptr);
        if (self->buffer_view)  vkDestroyBufferView(dev, self->buffer_view, nullptr);
        // Free memory only if not suballocated from a heap
        if (!self->py_heap && self->memory) vkFreeMemory(dev, self->memory, nullptr);
        if (self->image)        vkDestroyImage(dev, self->image, nullptr);
        if (self->buffer)       vkDestroyBuffer(dev, self->buffer, nullptr);
        Py_DECREF(self->py_device);
    }
    Py_XDECREF(self->py_heap);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/* ----------------------------------------------------------------------------
   upload - upload data to a buffer resource
   ------------------------------------------------------------------------- */
/**
 * Upload data from a Python bytes-like object into a buffer resource.
 *
 * Args:
 *     data (bytes): data to upload.
 *     offset (int, optional): destination offset in bytes (default 0).
 */
PyObject *vk_Resource_upload(vk_Resource *self, PyObject *args) {
    Py_buffer view;
    uint64_t offset = 0;
    if (!PyArg_ParseTuple(args, "y*|K", &view, &offset))
        return nullptr;

    if (!self->buffer || !self->memory) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
        return nullptr;
    }

    if (offset + view.len > self->size) {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_ValueError,
                     "Upload size %zd exceeds buffer size (offset %llu + %zd > %llu)",
                     view.len, offset, view.len, self->size);
        return nullptr;
    }

    void *mapped = vk_map_memory(self->py_device, self->memory,
                                 self->heap_offset + offset, view.len);
    if (!mapped) {
        PyBuffer_Release(&view);
        return nullptr; // error already set by vk_map_memory
    }

    memcpy(mapped, view.buf, view.len);
    vkUnmapMemory(self->py_device->device, self->memory);
    PyBuffer_Release(&view);
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   upload_subresources - batch upload of rectangles to a texture
   ------------------------------------------------------------------------- */
/**
 * Batch upload of multiple rectangular regions into a texture resource.
 *
 * Args:
 *     rects (list): list of 5‑tuples (data, x, y, width, height).
 */
PyObject *vk_Resource_upload_subresources(vk_Resource *self, PyObject *args) {
    PyObject *rects_list;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &rects_list))
        return nullptr;

    if (!self->image) {
        PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
        return nullptr;
    }

    Py_ssize_t num_rects = PyList_Size(rects_list);
    if (num_rects == 0)
        Py_RETURN_NONE;

    vk_Device *dev = self->py_device;

    // First pass: validate rectangles and compute total staging size
    struct RectUpload {
        uint32_t x, y, w, h;
        PyBufferGuard buffer;
        VkDeviceSize offset;
        uint32_t slice;
    };
    std::vector<RectUpload> rects;
    rects.reserve(num_rects);
    VkDeviceSize total_size = 0;

    for (Py_ssize_t i = 0; i < num_rects; ++i) {
        PyObject *tuple = PyList_GetItem(rects_list, i);
        if (!PyTuple_Check(tuple)) {
            PyErr_Format(PyExc_TypeError, "Item %zd must be a tuple", i);
            return nullptr;
        }
        Py_ssize_t tsize = PyTuple_Size(tuple);
        if (tsize != 5 && tsize != 6) {
            PyErr_Format(PyExc_TypeError,
                         "Item %zd must be a 5‑ or 6‑tuple (data, x, y, width, height[, slice])", i);
            return nullptr;
        }

        RectUpload r = {};
        PyObject *data_obj = nullptr;
        uint32_t slice = 0;

        if (tsize == 5) {
            if (!PyArg_ParseTuple(tuple, "OIIII", &data_obj, &r.x, &r.y, &r.w, &r.h))
                return nullptr;
        } else {
            if (!PyArg_ParseTuple(tuple, "OIIIII", &data_obj, &r.x, &r.y, &r.w, &r.h, &slice))
                return nullptr;
        }
        r.slice = slice;

        if (r.slice >= self->slices) {
            PyErr_Format(PyExc_ValueError,
                         "Slice %u out of range (max %u)", r.slice, self->slices - 1);
            return nullptr;
        }

        if (!r.buffer.acquire(data_obj, PyBUF_SIMPLE))
            return nullptr;

        if (r.buffer.view.len < (size_t)(r.w * r.h * 4)) {
            PyErr_Format(PyExc_ValueError,
                "Data size %zd too small for %ux%u rectangle (need %u bytes)",
                r.buffer.view.len, r.w, r.h, r.w * r.h * 4);
            return nullptr;
        }

        if (r.w == 0 || r.h == 0)
            continue;

        if (r.x + r.w > self->image_extent.width || r.y + r.h > self->image_extent.height) {
            PyErr_Format(PyExc_ValueError,
                         "Rectangle (%u,%u %ux%u) exceeds texture dimensions (%ux%u)",
                         r.x, r.y, r.w, r.h,
                         self->image_extent.width, self->image_extent.height);
            return nullptr;
        }

        VkDeviceSize sz = r.w * r.h * 4; // assume 4 bytes per pixel (RGBA8)
        r.offset = total_size;
        total_size += sz;
        rects.push_back(std::move(r));
    }

    if (rects.empty())
        Py_RETURN_NONE;

    // Use RAII staging buffer to gather all rectangles
    ScopedStagingBuffer staging(dev, total_size);
    if (!staging.valid()) {
        // error already set by ScopedStagingBuffer constructor
        return nullptr;
    }

    // Copy all rectangles into the staging buffer
    uint8_t *dst = static_cast<uint8_t *>(staging.mapped());
    for (auto &r : rects) {
        memcpy(dst + r.offset, r.buffer.view.buf, r.buffer.view.len);
    }

    // Execute copy commands using one‑time command buffer
    bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        // Transition texture to transfer destination
        vk_cmd_transition_for_copy_dst(cmd, self->image, 0, self->slices);

        // Issue copy commands for each rectangle
        for (const auto &r : rects) {
            VkBufferImageCopy region = {};
            region.bufferOffset = r.offset;
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.baseArrayLayer = r.slice;
            region.imageSubresource.layerCount = 1;
            region.imageOffset = { static_cast<int32_t>(r.x), static_cast<int32_t>(r.y), 0 };
            region.imageExtent = { r.w, r.h, 1 };
            vkCmdCopyBufferToImage(cmd, staging.buffer(), self->image,
                                   VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
        }

        // Transition back to GENERAL layout for compute shader access
        vk_cmd_transition_for_compute(cmd, self->image, 0, self->slices);
    });

    if (!ok) {
        // error already set by vk_execute_one_time_commands
        return nullptr;
    }

    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   download - download entire texture to bytes
   ------------------------------------------------------------------------- */
/**
 * Download the entire texture resource into a bytes object.
 *
 * Returns:
 *     bytes: raw pixel data (row‑major, RGBA).
 */
PyObject *vk_Resource_download(vk_Resource *self, PyObject *ignored) {
    if (!self->image) {
        PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
        return nullptr;
    }

    vk_Device *dev = self->py_device;
    VkDeviceSize buf_size = self->size;

    // Create temporary device-local buffer for the image data
    VkBuffer device_buffer;
    VkDeviceMemory device_memory;
    VkBufferCreateInfo binfo = { VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO };
    binfo.size = buf_size;
    binfo.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT;
    VK_CHECK_OR_RETURN_NULL(
        vkCreateBuffer(dev->device, &binfo, nullptr, &device_buffer),
        PyExc_RuntimeError, "Failed to create device buffer"
    );

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(dev->device, device_buffer, &mem_req);
    VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
    alloc.allocationSize = mem_req.size;
    alloc.memoryTypeIndex = vk_find_memory_type_index(&dev->mem_props,
                                                       VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    VkResult res = vkAllocateMemory(dev->device, &alloc, nullptr, &device_memory);
    if (res != VK_SUCCESS) {
        vkDestroyBuffer(dev->device, device_buffer, nullptr);
        PyErr_Format(PyExc_RuntimeError, "Failed to allocate device memory (error %d)", res);
        return nullptr;
    }
    vkBindBufferMemory(dev->device, device_buffer, device_memory, 0);

    // Use RAII staging buffer for host‑visible download
    ScopedStagingBuffer staging(dev, buf_size);
    if (!staging.valid()) {
        vkDestroyBuffer(dev->device, device_buffer, nullptr);
        vkFreeMemory(dev->device, device_memory, nullptr);
        return nullptr;
    }

    // Execute copy: image → device buffer → staging buffer
    bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        // Transition texture to transfer source
        vk_cmd_transition_for_copy_src(cmd, self->image, 0, 1);

        VkBufferImageCopy region = {};
        region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        region.imageSubresource.layerCount = 1;
        region.imageExtent = self->image_extent;
        vkCmdCopyImageToBuffer(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                               device_buffer, 1, &region);

        // Barrier to make device buffer visible for subsequent copy
        VkBufferMemoryBarrier buf_barrier = { VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER };
        buf_barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
        buf_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
        buf_barrier.buffer = device_buffer;
        buf_barrier.size = buf_size;
        vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                             VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                             0, nullptr, 1, &buf_barrier, 0, nullptr);

        // Copy to staging buffer
        VkBufferCopy copy = { 0, 0, buf_size };
        vkCmdCopyBuffer(cmd, device_buffer, staging.buffer(), 1, &copy);

        // Transition texture back to GENERAL
        vk_cmd_transition_for_compute(cmd, self->image, 0, 1);
    });

    // Clean up temporary device buffer regardless of success
    vkDestroyBuffer(dev->device, device_buffer, nullptr);
    vkFreeMemory(dev->device, device_memory, nullptr);

    if (!ok) {
        return nullptr; // error already set
    }

    // ScopedStagingBuffer already mapped the memory; use it directly
    PyObject *result_bytes = PyBytes_FromStringAndSize(static_cast<char *>(staging.mapped()), buf_size);
    if (!result_bytes) {
        PyErr_NoMemory();
        return nullptr;
    }

    return result_bytes;
}

/* ----------------------------------------------------------------------------
   copy_to - copy between resources
   ------------------------------------------------------------------------- */
/**
 * Copy data from this resource to another resource.
 * Supports buffer‑to‑buffer, buffer‑to‑texture, texture‑to‑buffer,
 * and texture‑to‑texture.
 *
 * Args:
 *     dst (vk.Resource): destination resource.
 *     size (int, optional): number of bytes to copy (buffer‑to‑buffer only).
 *     src_offset (int, optional): source offset (buffer only).
 *     dst_offset (int, optional): destination offset (buffer only).
 *     width (int, optional): copy width (texture only, default full).
 *     height (int, optional): copy height (texture only, default full).
 *     depth (int, optional): copy depth (texture only, default 1).
 *     src_x, src_y, src_z (int, optional): source offsets.
 *     dst_x, dst_y, dst_z (int, optional): destination offsets.
 *     src_slice (int, optional): source array layer.
 *     dst_slice (int, optional): destination array layer.
 */
PyObject *vk_Resource_copy_to(vk_Resource *self, PyObject *args) {
    PyObject *dst_obj;
    uint64_t size = 0;
    uint64_t src_offset = 0, dst_offset = 0;
    uint32_t width = 0, height = 0, depth = 0;
    uint32_t src_x = 0, src_y = 0, src_z = 0;
    uint32_t dst_x = 0, dst_y = 0, dst_z = 0;
    uint32_t src_slice = 0, dst_slice = 0;

    if (!PyArg_ParseTuple(args, "O|KKKIIIIIIIIIII", &dst_obj,
                          &size, &src_offset, &dst_offset,
                          &width, &height, &depth,
                          &src_x, &src_y, &src_z,
                          &dst_x, &dst_y, &dst_z,
                          &src_slice, &dst_slice))
        return nullptr;

    if (!PyObject_TypeCheck(dst_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Destination must be a Resource");
        return nullptr;
    }

    vk_Resource *dst = reinterpret_cast<vk_Resource *>(dst_obj);
    vk_Device *dev = self->py_device;
    if (dst->py_device != dev) {
        PyErr_SetString(PyExc_ValueError, "Resources belong to different devices");
        return nullptr;
    }

    bool src_is_buf = (self->buffer != VK_NULL_HANDLE);
    bool dst_is_buf = (dst->buffer != VK_NULL_HANDLE);

    // Validate extents
    if (src_is_buf && dst_is_buf) {
        if (size == 0) size = self->size;
        if (src_offset + size > self->size || dst_offset + size > dst->size) {
            PyErr_Format(PyExc_ValueError, "Copy out of bounds");
            return nullptr;
        }
    } else if (!src_is_buf && !dst_is_buf) {
        if (width == 0) width = self->image_extent.width;
        if (height == 0) height = self->image_extent.height;
        if (depth == 0) depth = 1;
        if (src_x + width > self->image_extent.width ||
            src_y + height > self->image_extent.height ||
            dst_x + width > dst->image_extent.width ||
            dst_y + height > dst->image_extent.height ||
            src_slice >= self->slices || dst_slice >= dst->slices) {
            PyErr_Format(PyExc_ValueError, "Copy out of bounds");
            return nullptr;
        }
    }

    // Execute copy using one‑time command buffer
    bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        if (src_is_buf && dst_is_buf) {
            VkBufferCopy region = { src_offset, dst_offset, size };
            vkCmdCopyBuffer(cmd, self->buffer, dst->buffer, 1, &region);
        }
        else if (src_is_buf && !dst_is_buf) {
            vk_cmd_transition_for_copy_dst(cmd, dst->image, dst_slice, 1);

            VkBufferImageCopy region = {};
            region.bufferOffset = src_offset;
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.baseArrayLayer = dst_slice;
            region.imageSubresource.layerCount = 1;
            region.imageExtent = dst->image_extent;
            vkCmdCopyBufferToImage(cmd, self->buffer, dst->image,
                                   VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

            vk_cmd_transition_for_compute(cmd, dst->image, dst_slice, 1);
        }
        else if (!src_is_buf && dst_is_buf) {
            vk_cmd_transition_for_copy_src(cmd, self->image, src_slice, 1);

            VkBufferImageCopy region = {};
            region.bufferOffset = dst_offset;
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.baseArrayLayer = src_slice;
            region.imageSubresource.layerCount = 1;
            region.imageExtent = self->image_extent;
            vkCmdCopyImageToBuffer(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                                   dst->buffer, 1, &region);

            vk_cmd_transition_for_compute(cmd, self->image, src_slice, 1);
        }
        else /* !src_is_buf && !dst_is_buf */ {
            VkImageMemoryBarrier barriers[2] = {};
            // Source image: GENERAL → TRANSFER_SRC_OPTIMAL
            barriers[0].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
            barriers[0].image = self->image;
            barriers[0].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            barriers[0].subresourceRange.baseArrayLayer = src_slice;
            barriers[0].subresourceRange.layerCount = 1;
            barriers[0].oldLayout = VK_IMAGE_LAYOUT_GENERAL;
            barriers[0].newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
            barriers[0].srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
            barriers[0].dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;

            // Destination image: GENERAL → TRANSFER_DST_OPTIMAL
            barriers[1].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
            barriers[1].image = dst->image;
            barriers[1].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            barriers[1].subresourceRange.baseArrayLayer = dst_slice;
            barriers[1].subresourceRange.layerCount = 1;
            barriers[1].oldLayout = VK_IMAGE_LAYOUT_GENERAL;
            barriers[1].newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
            barriers[1].srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
            barriers[1].dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;

            vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                                 VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                                 0, nullptr, 0, nullptr, 2, barriers);

            VkImageCopy region = {};
            region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.srcSubresource.baseArrayLayer = src_slice;
            region.srcSubresource.layerCount = 1;
            region.srcOffset = { static_cast<int32_t>(src_x), static_cast<int32_t>(src_y), static_cast<int32_t>(src_z) };
            region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.dstSubresource.baseArrayLayer = dst_slice;
            region.dstSubresource.layerCount = 1;
            region.dstOffset = { static_cast<int32_t>(dst_x), static_cast<int32_t>(dst_y), static_cast<int32_t>(dst_z) };
            region.extent = { width, height, depth };

            vkCmdCopyImage(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                           dst->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

            // Transition back to GENERAL
            barriers[0].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
            barriers[0].newLayout = VK_IMAGE_LAYOUT_GENERAL;
            barriers[0].srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
            barriers[0].dstAccessMask = VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

            barriers[1].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
            barriers[1].newLayout = VK_IMAGE_LAYOUT_GENERAL;
            barriers[1].srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
            barriers[1].dstAccessMask = VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

            vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                                 VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0,
                                 0, nullptr, 0, nullptr, 2, barriers);
        }
    });

    if (!ok) {
        return nullptr; // error already set
    }

    Py_RETURN_NONE;
}

PyObject* vk_Resource_clear_color(vk_Resource* self, PyObject* args) {
    float r, g, b, a;
    if (!PyArg_ParseTuple(args, "ffff", &r, &g, &b, &a))
        return nullptr;

    if (!self->image) {
        PyErr_SetString(PyExc_TypeError, "Resource is not an image");
        return nullptr;
    }

    vk_Device* dev = self->py_device;
    VkClearColorValue clear_value = { r, g, b, a };
    VkImageSubresourceRange range = {
        VK_IMAGE_ASPECT_COLOR_BIT,
        0, 1,  // baseMipLevel, levelCount
        0, 1   // baseArrayLayer, layerCount
    };

    bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        vk_cmd_transition_for_copy_dst(cmd, self->image, 0, self->slices);
        vkCmdClearColorImage(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                             &clear_value, 1, &range);
        vk_cmd_transition_for_compute(cmd, self->image, 0, 1);
    });

    if (!ok) return nullptr;
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Resource type definition
   ------------------------------------------------------------------------- */
static PyMemberDef vk_Resource_members[] = {
    {"size", T_ULONGLONG, offsetof(vk_Resource, size), 0, "Size in bytes"},
    {"width", T_UINT, offsetof(vk_Resource, image_extent) + offsetof(VkExtent3D, width), 0, "Width in pixels"},
    {"height", T_UINT, offsetof(vk_Resource, image_extent) + offsetof(VkExtent3D, height), 0, "Height in pixels"},
    {"depth", T_UINT, offsetof(vk_Resource, image_extent) + offsetof(VkExtent3D, depth), 0, "Depth in pixels"},
    {"row_pitch", T_ULONGLONG, offsetof(vk_Resource, row_pitch), 0, "Row pitch in bytes"},
    {"slices", T_UINT, offsetof(vk_Resource, slices), 0, "Number of array slices"},
    {"heap_size", T_ULONGLONG, offsetof(vk_Resource, heap_size), 0, "Size of underlying memory allocation"},
    {"heap_type", T_INT, offsetof(vk_Resource, heap_type), 0, "Heap type (0=DEFAULT,1=UPLOAD,2=READBACK)"},
    {nullptr}
};

static PyMethodDef vk_Resource_methods[] = {
    {"upload", (PyCFunction)vk_Resource_upload, METH_VARARGS,
     "Upload data to a buffer."},
    {"upload_subresources", (PyCFunction)vk_Resource_upload_subresources, METH_VARARGS,
     "Batch upload rectangles to a texture."},
    {"download", (PyCFunction)vk_Resource_download, METH_NOARGS,
     "Download entire texture as bytes."},
    {"copy_to", (PyCFunction)vk_Resource_copy_to, METH_VARARGS,
     "Copy to another resource."},
    {"clear_color", (PyCFunction)vk_Resource_clear_color, METH_VARARGS,
     "Clear the entire image to a solid color."},
    {nullptr, nullptr, 0, nullptr}
};

PyTypeObject vk_Resource_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Resource",
    .tp_basicsize = sizeof(vk_Resource),
    .tp_dealloc = (destructor)vk_Resource_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Resource_methods,
    .tp_members = vk_Resource_members,
};