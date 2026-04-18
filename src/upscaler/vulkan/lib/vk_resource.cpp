/**
 * @file vk_resource.cpp
 * @brief Vulkan resource methods: upload, download, copy, and batch texture upload.
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

    // Constructor
    PyBufferGuard() = default;

    // Move constructor
    PyBufferGuard(PyBufferGuard&& other) noexcept
        : view(other.view), owned(other.owned) {
        other.owned = false;
    }

    // Move assignment
    PyBufferGuard& operator=(PyBufferGuard&& other) noexcept {
        if (this != &other) {
            release();
            view = other.view;
            owned = other.owned;
            other.owned = false;
        }
        return *this;
    }

    // Disable copying
    PyBufferGuard(const PyBufferGuard&) = delete;
    PyBufferGuard& operator=(const PyBufferGuard&) = delete;

    ~PyBufferGuard() { if (owned) PyBuffer_Release(&view); }

    bool acquire(PyObject *obj, int flags = PyBUF_SIMPLE) {
        if (PyObject_GetBuffer(obj, &view, flags) < 0) return false;
        owned = true;
        return true;
    }

    void release() {
        if (owned) {
            PyBuffer_Release(&view);
            owned = false;
        }
    }
};

/* ----------------------------------------------------------------------------
   Helper: Execute a temporary command buffer and wait
   ------------------------------------------------------------------------- */
template<typename RecordFunc>
static VkResult execute_commands(vk_Device *dev, RecordFunc &&record) {
    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to allocate temporary command buffer");
        return VK_ERROR_OUT_OF_DEVICE_MEMORY;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);
    record(cmd);
    VkResult res = vkEndCommandBuffer(cmd);
    if (res != VK_SUCCESS) {
        vk_free_temp_cmd(dev, cmd);
        return res;
    }

    VkFenceCreateInfo finfo = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    VkFence fence;
    vkCreateFence(dev->device, &finfo, nullptr, &fence);

    VkSubmitInfo submit = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
    submit.commandBufferCount = 1;
    submit.pCommandBuffers = &cmd;
    res = vkQueueSubmit(dev->queue, 1, &submit, fence);
    if (res != VK_SUCCESS) {
        vkDestroyFence(dev->device, fence, nullptr);
        vk_free_temp_cmd(dev, cmd);
        return res;
    }

    // Wait with timeout (5 seconds)
    res = vkWaitForFences(dev->device, 1, &fence, VK_TRUE, 5'000'000'000);
    vkDestroyFence(dev->device, fence, nullptr);
    vk_free_temp_cmd(dev, cmd);

    if (res == VK_TIMEOUT) {
        PyErr_SetString(PyExc_TimeoutError, "Vulkan command timed out after 5 seconds");
        return VK_TIMEOUT;
    }
    return res;
}

/* ----------------------------------------------------------------------------
   Helper: Acquire staging buffer, call user, then release
   ------------------------------------------------------------------------- */
template<typename UserFunc>
static bool with_staging_buffer(vk_Device *dev, VkDeviceSize size, UserFunc &&user) {
    VkBuffer staging_buffer;
    VkDeviceMemory staging_memory;
    void *mapped;
    bool used_pool;
    if (!vk_staging_buffer_acquire(dev, size, &staging_buffer, &staging_memory,
                                   &mapped, &used_pool))
        return false;

    user(staging_buffer, staging_memory, mapped, used_pool);
    vkUnmapMemory(dev->device, staging_memory);
    vk_staging_buffer_release(dev, staging_buffer, staging_memory, used_pool);
    return true;
}

/* ----------------------------------------------------------------------------
   Helper: Insert an image memory barrier (simplifies repeated calls)
   ------------------------------------------------------------------------- */
static void cmd_image_barrier(VkCommandBuffer cmd, VkImage image,
                              VkImageLayout oldLayout, VkImageLayout newLayout,
                              VkPipelineStageFlags srcStage, VkPipelineStageFlags dstStage,
                              VkAccessFlags srcAccess, VkAccessFlags dstAccess,
                              uint32_t baseMip = 0, uint32_t levelCount = 1,
                              uint32_t baseLayer = 0, uint32_t layerCount = 1) {
    VkImageMemoryBarrier barrier = { VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER };
    barrier.srcAccessMask = srcAccess;
    barrier.dstAccessMask = dstAccess;
    barrier.oldLayout = oldLayout;
    barrier.newLayout = newLayout;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.image = image;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.baseMipLevel = baseMip;
    barrier.subresourceRange.levelCount = levelCount;
    barrier.subresourceRange.baseArrayLayer = baseLayer;
    barrier.subresourceRange.layerCount = layerCount;
    vkCmdPipelineBarrier(cmd, srcStage, dstStage, 0, 0, nullptr, 0, nullptr, 1, &barrier);
}

/* ----------------------------------------------------------------------------
   Resource deallocator
   ------------------------------------------------------------------------- */
void vk_Resource_dealloc(vk_Resource *self) {
    if (self->py_device) {
        VkDevice dev = self->py_device->device;
        if (self->image_view) vkDestroyImageView(dev, self->image_view, nullptr);
        if (self->buffer_view) vkDestroyBufferView(dev, self->buffer_view, nullptr);
        if (!self->py_heap && self->memory) vkFreeMemory(dev, self->memory, nullptr);
        if (self->image) vkDestroyImage(dev, self->image, nullptr);
        if (self->buffer) vkDestroyBuffer(dev, self->buffer, nullptr);
        Py_DECREF(self->py_device);
    }
    Py_XDECREF(self->py_heap);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/* ----------------------------------------------------------------------------
   Helper: map buffer memory (with GIL safety)
   ------------------------------------------------------------------------- */
static void *map_buffer_memory(vk_Device *dev, VkDeviceMemory memory,
                               VkDeviceSize offset, VkDeviceSize size) {
    void *mapped = nullptr;
    VkResult res = vkMapMemory(dev->device, memory, offset, size, 0, &mapped);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Failed to map memory (error %d)", res);
        return nullptr;
    }
    return mapped;
}

/* ----------------------------------------------------------------------------
   upload - buffer only
   ------------------------------------------------------------------------- */
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

    void *mapped = map_buffer_memory(self->py_device, self->memory,
                                     self->heap_offset + offset, view.len);
    if (!mapped) {
        PyBuffer_Release(&view);
        return nullptr;
    }

    memcpy(mapped, view.buf, view.len);
    vkUnmapMemory(self->py_device->device, self->memory);
    PyBuffer_Release(&view);
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   upload_subresources - batch upload of rectangles to a texture
   ------------------------------------------------------------------------- */
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
    };
    std::vector<RectUpload> rects;
    rects.reserve(num_rects);
    VkDeviceSize total_size = 0;

    for (Py_ssize_t i = 0; i < num_rects; ++i) {
        PyObject *tuple = PyList_GetItem(rects_list, i);
        if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
            PyErr_Format(PyExc_TypeError,
                         "Item %zd must be a 5‑tuple (data, x, y, width, height)", i);
            return nullptr;
        }

        RectUpload r = {};
        PyObject *data_obj = nullptr;
        if (!PyArg_ParseTuple(tuple, "OIIII", &data_obj, &r.x, &r.y, &r.w, &r.h))
            return nullptr;
        if (!r.buffer.acquire(data_obj, PyBUF_SIMPLE))
            return nullptr;

        if (r.w == 0 || r.h == 0)
            continue;

        if (r.x + r.w > self->image_extent.width || r.y + r.h > self->image_extent.height) {
            PyErr_Format(PyExc_ValueError,
                         "Rectangle (%u,%u %ux%u) exceeds texture dimensions (%ux%u)",
                         r.x, r.y, r.w, r.h, self->image_extent.width, self->image_extent.height);
            return nullptr;
        }

        VkDeviceSize sz = r.w * r.h * 4;
        r.offset = total_size;
        total_size += sz;
        rects.push_back(std::move(r));
    }

    if (rects.empty())
        Py_RETURN_NONE;

    // Use staging buffer to gather all rectangles
    bool success = with_staging_buffer(dev, total_size, [&](VkBuffer staging_buffer, VkDeviceMemory,
                                                            void *mapped, bool /*used_pool*/) {
        uint8_t *dst = static_cast<uint8_t *>(mapped);
        for (auto &r : rects) {
            memcpy(dst + r.offset, r.buffer.view.buf, r.buffer.view.len);
        }

        // Execute copy commands
        VkResult res = execute_commands(dev, [&](VkCommandBuffer cmd) {
            cmd_image_barrier(cmd, self->image,
                              VK_IMAGE_LAYOUT_GENERAL, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                              VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT,
                              VK_ACCESS_SHADER_WRITE_BIT, VK_ACCESS_TRANSFER_WRITE_BIT,
                              0, 1, 0, 1);

            for (const auto &r : rects) {
                VkBufferImageCopy region = {};
                region.bufferOffset = r.offset;
                region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
                region.imageSubresource.layerCount = 1;
                region.imageOffset = { static_cast<int32_t>(r.x), static_cast<int32_t>(r.y), 0 };
                region.imageExtent = { r.w, r.h, 1 };
                vkCmdCopyBufferToImage(cmd, staging_buffer, self->image,
                                       VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
            }

            cmd_image_barrier(cmd, self->image,
                              VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL,
                              VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                              VK_ACCESS_TRANSFER_WRITE_BIT, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                              0, 1, 0, 1);
        });

        if (res != VK_SUCCESS) {
            PyErr_Format(PyExc_RuntimeError, "Upload submission failed (error %d)", res);
        }
    });

    if (!success) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to acquire staging buffer");
        return nullptr;
    }

    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   download - entire texture to bytes
   ------------------------------------------------------------------------- */
PyObject *vk_Resource_download(vk_Resource *self, PyObject *ignored) {
    if (!self->image) {
        PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
        return nullptr;
    }

    vk_Device *dev = self->py_device;
    VkDeviceSize buf_size = self->size;

    // Create temporary device-local buffer
    VkBuffer device_buffer;
    VkDeviceMemory device_memory;
    VkBufferCreateInfo binfo = { VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO };
    binfo.size = buf_size;
    binfo.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT;
    if (vkCreateBuffer(dev->device, &binfo, nullptr, &device_buffer) != VK_SUCCESS) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create device buffer");
        return nullptr;
    }

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(dev->device, device_buffer, &mem_req);
    VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
    alloc.allocationSize = mem_req.size;
    alloc.memoryTypeIndex = vk_find_memory_type_index(&dev->mem_props, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (vkAllocateMemory(dev->device, &alloc, nullptr, &device_memory) != VK_SUCCESS) {
        vkDestroyBuffer(dev->device, device_buffer, nullptr);
        PyErr_SetString(PyExc_RuntimeError, "Failed to allocate device memory");
        return nullptr;
    }
    vkBindBufferMemory(dev->device, device_buffer, device_memory, 0);

    PyObject *result_bytes = nullptr;

    bool success = with_staging_buffer(dev, buf_size, [&](VkBuffer staging_buffer, VkDeviceMemory staging_memory,
                                                          void *mapped, bool used_pool) {
        VkResult res = execute_commands(dev, [&](VkCommandBuffer cmd) {
            // Transition texture to TRANSFER_SRC_OPTIMAL
            cmd_image_barrier(cmd, self->image,
                              VK_IMAGE_LAYOUT_GENERAL, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                              VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT,
                              VK_ACCESS_SHADER_WRITE_BIT, VK_ACCESS_TRANSFER_READ_BIT,
                              0, 1, 0, 1);

            VkBufferImageCopy region = {};
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.layerCount = 1;
            region.imageExtent = self->image_extent;
            vkCmdCopyImageToBuffer(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                                   device_buffer, 1, &region);

            VkBufferMemoryBarrier buf_barrier = { VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER };
            buf_barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
            buf_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
            buf_barrier.buffer = device_buffer;
            buf_barrier.size = buf_size;
            vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                                 VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                                 0, nullptr, 1, &buf_barrier, 0, nullptr);

            VkBufferCopy copy = { 0, 0, buf_size };
            vkCmdCopyBuffer(cmd, device_buffer, staging_buffer, 1, &copy);

            // Transition texture back
            cmd_image_barrier(cmd, self->image,
                              VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL,
                              VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                              VK_ACCESS_TRANSFER_READ_BIT, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                              0, 1, 0, 1);
        });

        if (res != VK_SUCCESS) {
            PyErr_Format(PyExc_RuntimeError, "Download submission failed (error %d)", res);
            return;
        }

        // Map staging and copy to Python bytes
        void *mapped_data = map_buffer_memory(dev, staging_memory, 0, buf_size);
        if (!mapped_data) return;

        result_bytes = PyBytes_FromStringAndSize(static_cast<char *>(mapped_data), buf_size);
        vkUnmapMemory(dev->device, staging_memory);
    });

    // Cleanup temporary device buffer
    vkDestroyBuffer(dev->device, device_buffer, nullptr);
    vkFreeMemory(dev->device, device_memory, nullptr);

    if (!success) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to acquire staging buffer");
        return nullptr;
    }
    if (!result_bytes) {
        // Error already set by map_buffer_memory or PyBytes_FromStringAndSize
        return nullptr;
    }
    return result_bytes;
}

/* ----------------------------------------------------------------------------
   copy_to - buffer-buffer, buffer-texture, texture-texture
   ------------------------------------------------------------------------- */
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

    // Determine copy type and set default extents
    bool src_is_buf = (self->buffer != VK_NULL_HANDLE);
    bool dst_is_buf = (dst->buffer != VK_NULL_HANDLE);

    // Validate parameters
    if (src_is_buf && dst_is_buf) {
        if (size == 0) size = self->size;
        if (src_offset + size > self->size || dst_offset + size > dst->size) {
            PyErr_Format(PyExc_ValueError, "Copy out of bounds");
            return nullptr;
        }
    } else if (!src_is_buf && !dst_is_buf) {
        // Texture to texture
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

    VkResult res = execute_commands(dev, [&](VkCommandBuffer cmd) {
        if (src_is_buf && dst_is_buf) {
            VkBufferCopy region = { src_offset, dst_offset, size };
            vkCmdCopyBuffer(cmd, self->buffer, dst->buffer, 1, &region);
        }
        else if (src_is_buf && !dst_is_buf) {
            // Determine if this is the first upload to this texture
            bool first_use = (dst->image_view == VK_NULL_HANDLE);
            VkImageLayout srcLayout = first_use ? VK_IMAGE_LAYOUT_UNDEFINED : VK_IMAGE_LAYOUT_GENERAL;
            VkAccessFlags srcAccess = first_use ? 0 : VK_ACCESS_SHADER_WRITE_BIT;
            VkPipelineStageFlags srcStage = first_use ? VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT
                                                      : VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT;

            cmd_image_barrier(cmd, dst->image,
                              srcLayout, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                              srcStage, VK_PIPELINE_STAGE_TRANSFER_BIT,
                              srcAccess, VK_ACCESS_TRANSFER_WRITE_BIT,
                              0, 1, dst_slice, 1);

            VkBufferImageCopy region = {};
            region.bufferOffset = src_offset;
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.baseArrayLayer = dst_slice;
            region.imageSubresource.layerCount = 1;
            region.imageExtent = dst->image_extent;
            vkCmdCopyBufferToImage(cmd, self->buffer, dst->image,
                                   VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

            cmd_image_barrier(cmd, dst->image,
                              VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL,
                              VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                              VK_ACCESS_TRANSFER_WRITE_BIT, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                              0, 1, dst_slice, 1);
        }
        else if (!src_is_buf && dst_is_buf) {
            cmd_image_barrier(cmd, self->image,
                              VK_IMAGE_LAYOUT_GENERAL, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                              VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT,
                              VK_ACCESS_SHADER_WRITE_BIT, VK_ACCESS_TRANSFER_READ_BIT,
                              0, 1, src_slice, 1);

            VkBufferImageCopy region = {};
            region.bufferOffset = dst_offset;
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.baseArrayLayer = src_slice;
            region.imageSubresource.layerCount = 1;
            region.imageExtent = self->image_extent;
            vkCmdCopyImageToBuffer(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                                   dst->buffer, 1, &region);

            cmd_image_barrier(cmd, self->image,
                              VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL,
                              VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                              VK_ACCESS_TRANSFER_READ_BIT, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                              0, 1, src_slice, 1);
        }
        else /* !src_is_buf && !dst_is_buf */ {
            VkImageMemoryBarrier barriers[2] = {};
            barriers[0].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
            barriers[0].image = self->image;
            barriers[0].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            barriers[0].subresourceRange.baseArrayLayer = src_slice;
            barriers[0].subresourceRange.layerCount = 1;
            barriers[0].oldLayout = VK_IMAGE_LAYOUT_GENERAL;
            barriers[0].newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
            barriers[0].srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
            barriers[0].dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;

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

    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Copy submission failed (error %d)", res);
        return nullptr;
    }
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
    {"upload", (PyCFunction)vk_Resource_upload, METH_VARARGS, "Upload data to a buffer."},
    {"upload_subresources", (PyCFunction)vk_Resource_upload_subresources, METH_VARARGS, "Batch upload rectangles to a texture."},
    {"download", (PyCFunction)vk_Resource_download, METH_NOARGS, "Download entire texture as bytes."},
    {"copy_to", (PyCFunction)vk_Resource_copy_to, METH_VARARGS, "Copy to another resource."},
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