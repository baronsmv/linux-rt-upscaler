/**
 * @file vk_resource.cpp
 * @brief Vulkan resource (buffer / image) data-transfer methods.
 *
 * The `vk.Resource` Python type represents a Vulkan buffer or image.
 * This file implements the methods that move data between host and device:
 *
 *   - `upload()`               - host to device (buffer only).
 *   - `upload_subresources()`  - host to device (texture rectangles).
 *   - `download()`             - device to host (texture only).
 *   - `copy_to()`              - device to device (buffer or image).
 *   - `batch_copy_to_array()`  - copy tiles to Texture2DArray slices.
 *   - `clear_color()`          - fill an image with a solid RGBA colour.
 *
 * All methods are **synchronous**: they record, submit, and wait for a
 * command buffer, so Python execution blocks until the GPU operation
 * finishes. Timely completion is guaranteed by either mapping host-visible
 * memory or using a temporary fence.
 *
 * The resource object also keeps pre-filled `VkDescriptorBufferInfo` /
 * `VkDescriptorImageInfo` structures that are used when the resource is
 * bound to a compute pipeline via the descriptor set helpers in
 * `vk_utils.cpp`.
 */

#include "vk_resource.h"
#include "vk_utils.h"
#include <cstring>
#include <functional>

// =============================================================================
//  Lifecycle - deallocation
// =============================================================================

/**
 * Destroy all Vulkan objects owned by the resource.
 * If the resource was sub-allocated from a heap, the memory is **not**
 * freed here - that belongs to the heap itself.
 */
void vk_Resource_dealloc(vk_Resource *self) {
  if (self->py_device) {
    VkDevice dev = self->py_device->device;
    if (self->image_view)
      vkDestroyImageView(dev, self->image_view, nullptr);
    if (self->buffer_view)
      vkDestroyBufferView(dev, self->buffer_view, nullptr);
    if (!self->py_heap && self->memory)
      vkFreeMemory(dev, self->memory, nullptr);
    if (self->image)
      vkDestroyImage(dev, self->image, nullptr);
    if (self->buffer)
      vkDestroyBuffer(dev, self->buffer, nullptr);
    Py_DECREF(self->py_device);
  }
  Py_XDECREF(self->py_heap);
  Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

// =============================================================================
//  Data upload (host to device)
// =============================================================================

/**
 * Upload raw bytes to a buffer.
 *
 * The destination buffer must be host-visible (created with `HEAP_UPLOAD`
 * or bound to an upload heap). The function maps the memory, copies the
 * data, and unmaps.
 *
 * Args:
 *   data (bytes, bytearray, memoryview): source data.
 *   offset (int, optional): byte offset in the buffer (default 0).
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
                 "Upload of %zd bytes at offset %llu exceeds "
                 "buffer size %llu",
                 view.len, offset, self->size);
    return nullptr;
  }

  void *mapped = vk_map_memory(self->py_device, self->memory,
                               self->heap_offset + offset, view.len);
  if (!mapped) {
    PyBuffer_Release(&view);
    return nullptr; // exception already set by vk_map_memory
  }

  memcpy(mapped, view.buf, view.len);
  vkUnmapMemory(self->py_device->device, self->memory);
  PyBuffer_Release(&view);
  Py_RETURN_NONE;
}

// =============================================================================
//  Texture rectangle upload
// =============================================================================

/**
 * Batch upload multiple rectangular regions to a texture.
 *
 * All rectangles are gathered into a single staging buffer and then copied
 * to the image via one command buffer submission. This is far more
 * efficient than many small uploads.
 *
 * Args:
 *   rects (list of tuples): each tuple is either
 *       (data, x, y, width, height)           or
 *       (data, x, y, width, height, slice)
 *     where `data` is a bytes-like object and (x,y) is the top-left corner
 *     of the region in the texture.
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

  // -----------------------------------------------------------------
  // 1. Validate all rectangles and compute total staging size
  // -----------------------------------------------------------------
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
                   "Item %zd must be a 5- or 6-tuple "
                   "(data, x, y, width, height [, slice])",
                   i);
      return nullptr;
    }

    RectUpload r = {};
    PyObject *data_obj = nullptr;
    uint32_t slice = 0;
    if (tsize == 5) {
      if (!PyArg_ParseTuple(tuple, "OIIII", &data_obj, &r.x, &r.y, &r.w, &r.h))
        return nullptr;
    } else {
      if (!PyArg_ParseTuple(tuple, "OIIIII", &data_obj, &r.x, &r.y, &r.w, &r.h,
                            &slice))
        return nullptr;
    }
    r.slice = slice;

    if (r.slice >= self->slices) {
      PyErr_Format(PyExc_ValueError, "Slice %u out of range (max %u)", r.slice,
                   self->slices - 1);
      return nullptr;
    }
    if (!r.buffer.acquire(data_obj, PyBUF_SIMPLE))
      return nullptr;
    if (r.buffer.view.len < (size_t)(r.w * r.h * 4)) {
      PyErr_Format(PyExc_ValueError,
                   "Data size %zd too small for %ux%u rectangle "
                   "(need %u bytes)",
                   r.buffer.view.len, r.w, r.h, r.w * r.h * 4);
      return nullptr;
    }
    if (r.w == 0 || r.h == 0)
      continue;
    if (r.x + r.w > self->image_extent.width ||
        r.y + r.h > self->image_extent.height) {
      PyErr_Format(PyExc_ValueError,
                   "Rectangle (%u,%u %ux%u) exceeds texture "
                   "dimensions (%ux%u)",
                   r.x, r.y, r.w, r.h, self->image_extent.width,
                   self->image_extent.height);
      return nullptr;
    }

    VkDeviceSize sz = r.w * r.h * 4; // RGBA8
    r.offset = total_size;
    total_size += sz;
    rects.push_back(std::move(r));
  }

  if (rects.empty())
    Py_RETURN_NONE;

  // -----------------------------------------------------------------
  // 2. Gather all pixel data into a single staging buffer
  // -----------------------------------------------------------------
  ScopedStagingBuffer staging(dev, total_size);
  if (!staging.valid())
    return nullptr; // exception already set

  uint8_t *dst = static_cast<uint8_t *>(staging.mapped());
  for (auto &r : rects)
    memcpy(dst + r.offset, r.buffer.view.buf, r.buffer.view.len);

  // -----------------------------------------------------------------
  // 3. Record and submit the copy command buffer
  // -----------------------------------------------------------------
  bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
    vk_cmd_transition_for_copy_dst(cmd, self->image, 0, self->slices);

    for (const auto &r : rects) {
      VkBufferImageCopy region = {};
      region.bufferOffset = r.offset;
      region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
      region.imageSubresource.baseArrayLayer = r.slice;
      region.imageSubresource.layerCount = 1;
      region.imageOffset = {static_cast<int32_t>(r.x),
                            static_cast<int32_t>(r.y), 0};
      region.imageExtent = {r.w, r.h, 1};
      vkCmdCopyBufferToImage(cmd, staging.buffer(), self->image,
                             VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
    }

    vk_cmd_transition_for_compute(cmd, self->image, 0, self->slices);
  });

  return ok ? Py_None : nullptr;
}

// =============================================================================
//  Data download (device to host)
// =============================================================================

/**
 * Download the entire texture as a row-major RGBA `bytes` object.
 *
 * The process is:
 *   1. Copy the image to a temporary device-local buffer.
 *   2. Copy that buffer to a host-visible staging buffer.
 *   3. Read the staging buffer into a Python bytes object.
 *
 * Temporary Vulkan objects are destroyed before returning.
 *
 * Only textures are supported - buffers use `HEAP_READBACK` and a simple map.
 */
PyObject *vk_Resource_download(vk_Resource *self, PyObject * /*ignored*/) {
  if (!self->image) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
    return nullptr;
  }

  vk_Device *dev = self->py_device;
  VkDeviceSize buf_size = self->size;

  // --- Temporary device-local buffer ---
  VkBuffer device_buffer;
  VkDeviceMemory device_memory;
  VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
  binfo.size = buf_size;
  binfo.usage =
      VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT;
  VK_CHECK_OR_RETURN_NULL(
      vkCreateBuffer(dev->device, &binfo, nullptr, &device_buffer),
      PyExc_RuntimeError, "Failed to create device buffer");

  VkMemoryRequirements mem_req;
  vkGetBufferMemoryRequirements(dev->device, device_buffer, &mem_req);
  VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
  alloc.allocationSize = mem_req.size;
  alloc.memoryTypeIndex = vk_find_memory_type_index(
      &dev->mem_props, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
  VkResult res = vkAllocateMemory(dev->device, &alloc, nullptr, &device_memory);
  if (res != VK_SUCCESS) {
    vkDestroyBuffer(dev->device, device_buffer, nullptr);
    PyErr_Format(PyExc_RuntimeError,
                 "Failed to allocate device memory (error %d)", res);
    return nullptr;
  }
  vkBindBufferMemory(dev->device, device_buffer, device_memory, 0);

  // --- Host-visible staging buffer ---
  ScopedStagingBuffer staging(dev, buf_size);
  if (!staging.valid()) {
    vkDestroyBuffer(dev->device, device_buffer, nullptr);
    vkFreeMemory(dev->device, device_memory, nullptr);
    return nullptr;
  }

  // --- Execute the copy chain ---
  bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
    vk_cmd_transition_for_copy_src(cmd, self->image, 0, 1);

    VkBufferImageCopy region = {};
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.layerCount = 1;
    region.imageExtent = self->image_extent;
    vkCmdCopyImageToBuffer(cmd, self->image,
                           VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, device_buffer,
                           1, &region);

    // Make device buffer visible for subsequent copy
    VkBufferMemoryBarrier buf_barrier = {
        VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER};
    buf_barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    buf_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    buf_barrier.buffer = device_buffer;
    buf_barrier.size = buf_size;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, nullptr, 1,
                         &buf_barrier, 0, nullptr);

    VkBufferCopy copy = {0, 0, buf_size};
    vkCmdCopyBuffer(cmd, device_buffer, staging.buffer(), 1, &copy);

    vk_cmd_transition_for_compute(cmd, self->image, 0, 1);
  });

  // Destroy temporary device-local resources
  vkDestroyBuffer(dev->device, device_buffer, nullptr);
  vkFreeMemory(dev->device, device_memory, nullptr);

  if (!ok)
    return nullptr;

  // Staging buffer is already mapped - extract the data
  PyObject *result = PyBytes_FromStringAndSize(
      static_cast<char *>(staging.mapped()), buf_size);
  if (!result)
    PyErr_NoMemory();
  return result;
}

// =============================================================================
//  Device-to-device copy
// =============================================================================

/**
 * Copy data between two resources (buffer to buffer, buffer to image, image
 * to buffer or image to image). The copy region may be a sub-rectangle or
 * sub-buffer range.
 *
 * Args (see Python docstring for the full list):
 *   dst         - destination resource.
 *   size        - byte count (buffer to buffer only).
 *   src_offset  - source byte offset (buffer only).
 *   dst_offset  - destination byte offset (buffer only).
 *   width, height, depth - image copy extent.
 *   src_x/y/z, dst_x/y/z - image offsets.
 *   src_slice, dst_slice - array layers.
 */
PyObject *vk_Resource_copy_to(vk_Resource *self, PyObject *args) {
  PyObject *dst_obj;
  uint64_t size = 0;
  uint64_t src_offset = 0, dst_offset = 0;
  uint32_t width = 0, height = 0, depth = 0;
  uint32_t src_x = 0, src_y = 0, src_z = 0;
  uint32_t dst_x = 0, dst_y = 0, dst_z = 0;
  uint32_t src_slice = 0, dst_slice = 0;

  if (!PyArg_ParseTuple(args, "O|KKKIIIIIIIIIII", &dst_obj, &size, &src_offset,
                        &dst_offset, &width, &height, &depth, &src_x, &src_y,
                        &src_z, &dst_x, &dst_y, &dst_z, &src_slice, &dst_slice))
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
    if (size == 0)
      size = self->size;
    if (src_offset + size > self->size || dst_offset + size > dst->size) {
      PyErr_Format(PyExc_ValueError, "Copy out of bounds");
      return nullptr;
    }
  } else if (!src_is_buf && !dst_is_buf) {
    if (width == 0)
      width = self->image_extent.width;
    if (height == 0)
      height = self->image_extent.height;
    if (depth == 0)
      depth = 1;
    if (src_x + width > self->image_extent.width ||
        src_y + height > self->image_extent.height ||
        dst_x + width > dst->image_extent.width ||
        dst_y + height > dst->image_extent.height ||
        src_slice >= self->slices || dst_slice >= dst->slices) {
      PyErr_Format(PyExc_ValueError, "Copy out of bounds");
      return nullptr;
    }
  }

  // Record and execute the copy via a one-time command buffer
  bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
    if (src_is_buf && dst_is_buf) {
      VkBufferCopy region = {src_offset, dst_offset, size};
      vkCmdCopyBuffer(cmd, self->buffer, dst->buffer, 1, &region);
    } else if (src_is_buf && !dst_is_buf) {
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
    } else if (!src_is_buf && dst_is_buf) {
      vk_cmd_transition_for_copy_src(cmd, self->image, src_slice, 1);
      VkBufferImageCopy region = {};
      region.bufferOffset = dst_offset;
      region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
      region.imageSubresource.baseArrayLayer = src_slice;
      region.imageSubresource.layerCount = 1;
      region.imageExtent = self->image_extent;
      vkCmdCopyImageToBuffer(cmd, self->image,
                             VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, dst->buffer,
                             1, &region);
      vk_cmd_transition_for_compute(cmd, self->image, src_slice, 1);
    } else { /* image to image */
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
                           VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, nullptr, 0,
                           nullptr, 2, barriers);

      VkImageCopy region = {};
      region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
      region.srcSubresource.baseArrayLayer = src_slice;
      region.srcSubresource.layerCount = 1;
      region.srcOffset = {static_cast<int32_t>(src_x),
                          static_cast<int32_t>(src_y),
                          static_cast<int32_t>(src_z)};
      region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
      region.dstSubresource.baseArrayLayer = dst_slice;
      region.dstSubresource.layerCount = 1;
      region.dstOffset = {static_cast<int32_t>(dst_x),
                          static_cast<int32_t>(dst_y),
                          static_cast<int32_t>(dst_z)};
      region.extent = {width, height, depth};
      vkCmdCopyImage(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                     dst->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1,
                     &region);

      // Transition back to GENERAL
      barriers[0].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
      barriers[0].newLayout = VK_IMAGE_LAYOUT_GENERAL;
      barriers[0].srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
      barriers[0].dstAccessMask =
          VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
      barriers[1].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
      barriers[1].newLayout = VK_IMAGE_LAYOUT_GENERAL;
      barriers[1].srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
      barriers[1].dstAccessMask =
          VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
      vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                           VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, nullptr,
                           0, nullptr, 2, barriers);
    }
  });

  return ok ? Py_None : nullptr;
}

/**
 * Copy a list of rectangular regions from this image to slices of a 2D array.
 *
 * The source image must be a 2D image (single slice) in
 * VK_IMAGE_LAYOUT_GENERAL. The destination must be a 2D array image. All
 * copies are executed in a single command buffer with appropriate image layout
 * transitions.
 *
 * Args (Python):
 *   dst (vk_Resource): Target 2D array image.
 *   regions (list of 5‑tuples): Each tuple is (src_x, src_y, dst_slice,
 *                                 copy_width, copy_height).
 *
 * Returns: None on success, or raises an exception.
 */
PyObject *vk_Resource_batch_copy_to_array(vk_Resource *self, PyObject *args) {
  PyObject *dst_obj;
  PyObject *regions_list;
  if (!PyArg_ParseTuple(args, "OO!", &dst_obj, &PyList_Type, &regions_list))
    return nullptr;

  // Validate destination
  if (!PyObject_TypeCheck(dst_obj, &vk_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "dst must be a Resource");
    return nullptr;
  }
  vk_Resource *dst = reinterpret_cast<vk_Resource *>(dst_obj);
  vk_Device *dev = self->py_device;
  if (dst->py_device != dev) {
    PyErr_SetString(vk_ResourceError, "Resources belong to different devices");
    return nullptr;
  }
  if (!self->image || !dst->image) {
    PyErr_SetString(vk_ResourceError,
                    "Both source and destination must be images");
    return nullptr;
  }
  if (self->slices != 1) {
    PyErr_SetString(vk_ResourceError, "Source image must be a single 2D image");
    return nullptr;
  }
  uint32_t dst_slice_count = dst->slices;
  if (dst_slice_count < 1) {
    PyErr_SetString(vk_ResourceError, "Destination image has no slices");
    return nullptr;
  }

  // Parse the region list
  Py_ssize_t num_regions = PyList_Size(regions_list);
  if (num_regions == 0) {
    Py_RETURN_NONE; // nothing to do
  }

  std::vector<VkImageCopy> copies;
  copies.reserve(num_regions);

  for (Py_ssize_t i = 0; i < num_regions; ++i) {
    PyObject *tuple = PyList_GetItem(regions_list, i);
    if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
      PyErr_Format(PyExc_ValueError, "Region %zd must be a 5‑tuple", i);
      return nullptr;
    }

    uint32_t src_x, src_y, dst_slice, width, height;
    if (!PyArg_ParseTuple(tuple, "IIIII", &src_x, &src_y, &dst_slice, &width,
                          &height))
      return nullptr;

    if (dst_slice >= dst_slice_count) {
      PyErr_Format(PyExc_ValueError,
                   "Region %zd: dst_slice %u exceeds maximum %u", i, dst_slice,
                   dst_slice_count);
      return nullptr;
    }
    if (width == 0 || height == 0)
      continue;

    VkImageCopy region = {};
    region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.srcSubresource.mipLevel = 0;
    region.srcSubresource.baseArrayLayer = 0;
    region.srcSubresource.layerCount = 1;
    region.srcOffset = {static_cast<int32_t>(src_x),
                        static_cast<int32_t>(src_y), 0};
    region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.dstSubresource.mipLevel = 0;
    region.dstSubresource.baseArrayLayer = dst_slice;
    region.dstSubresource.layerCount = 1;
    region.dstOffset = {0, 0, 0};
    region.extent = {width, height, 1};

    copies.push_back(region);
  }

  // Execute with a single command buffer
  bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
    // --- Transition source to TRANSFER_SRC_OPTIMAL ---
    // (Need VkImageMemoryBarrier; use the existing utility)
    vk_image_barrier(cmd, self->image, VK_IMAGE_LAYOUT_GENERAL,
                     VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                     VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                     VK_PIPELINE_STAGE_TRANSFER_BIT, VK_ACCESS_SHADER_WRITE_BIT,
                     VK_ACCESS_TRANSFER_READ_BIT, 0, 1, 0, 1);

    // --- Transition destination (all layers) to TRANSFER_DST_OPTIMAL ---
    vk_image_barrier(cmd, dst->image, VK_IMAGE_LAYOUT_GENERAL,
                     VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                     VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                     VK_PIPELINE_STAGE_TRANSFER_BIT, VK_ACCESS_SHADER_WRITE_BIT,
                     VK_ACCESS_TRANSFER_WRITE_BIT, 0, 1, 0, dst_slice_count);

    // --- Record all copies ---
    vkCmdCopyImage(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   dst->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   static_cast<uint32_t>(copies.size()), copies.data());

    // --- Transition images back to GENERAL ---
    vk_image_barrier(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                     VK_IMAGE_LAYOUT_GENERAL, VK_PIPELINE_STAGE_TRANSFER_BIT,
                     VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                     VK_ACCESS_TRANSFER_READ_BIT, VK_ACCESS_SHADER_WRITE_BIT, 0,
                     1, 0, 1);

    vk_image_barrier(cmd, dst->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                     VK_IMAGE_LAYOUT_GENERAL, VK_PIPELINE_STAGE_TRANSFER_BIT,
                     VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                     VK_ACCESS_TRANSFER_WRITE_BIT, VK_ACCESS_SHADER_WRITE_BIT,
                     0, 1, 0, dst_slice_count);
  });

  return ok ? Py_None : nullptr;
}

// =============================================================================
//  Clear colour
// =============================================================================

/**
 * Fill the entire image with a constant RGBA colour.
 *
 * The image is temporarily transitioned to `TRANSFER_DST_OPTIMAL`,
 * cleared, and returned to `GENERAL` layout.
 */
PyObject *vk_Resource_clear_color(vk_Resource *self, PyObject *args) {
  float r, g, b, a;
  if (!PyArg_ParseTuple(args, "ffff", &r, &g, &b, &a))
    return nullptr;

  if (!self->image) {
    PyErr_SetString(PyExc_TypeError, "Resource is not an image");
    return nullptr;
  }

  vk_Device *dev = self->py_device;
  VkClearColorValue clear_value = {r, g, b, a};
  VkImageSubresourceRange range = {
      VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1 // one mip, one layer
  };

  bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
    vk_cmd_transition_for_copy_dst(cmd, self->image, 0, self->slices);
    vkCmdClearColorImage(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                         &clear_value, 1, &range);
    vk_cmd_transition_for_compute(cmd, self->image, 0, 1);
  });

  return ok ? Py_None : nullptr;
}

// =============================================================================
//  Type definition
// =============================================================================

static PyMemberDef vk_Resource_members[] = {
    {"size", T_ULONGLONG, offsetof(vk_Resource, size), 0,
     "Total size of the resource in bytes."},
    {"width", T_UINT,
     offsetof(vk_Resource, image_extent) + offsetof(VkExtent3D, width), 0,
     "Image width in pixels (0 for buffers)."},
    {"height", T_UINT,
     offsetof(vk_Resource, image_extent) + offsetof(VkExtent3D, height), 0,
     "Image height in pixels."},
    {"depth", T_UINT,
     offsetof(vk_Resource, image_extent) + offsetof(VkExtent3D, depth), 0,
     "Image depth (1 for 2D)."},
    {"row_pitch", T_ULONGLONG, offsetof(vk_Resource, row_pitch), 0,
     "Row pitch in bytes (0 for buffers)."},
    {"slices", T_UINT, offsetof(vk_Resource, slices), 0,
     "Number of array layers."},
    {"heap_size", T_ULONGLONG, offsetof(vk_Resource, heap_size), 0,
     "Actual size of the underlying memory allocation."},
    {"heap_type", T_INT, offsetof(vk_Resource, heap_type), 0,
     "Memory type: 0=HEAP_DEFAULT, 1=HEAP_UPLOAD, 2=HEAP_READBACK."},
    {nullptr}};

static PyMethodDef vk_Resource_methods[] = {
    {"upload", (PyCFunction)vk_Resource_upload, METH_VARARGS,
     "Upload data to a buffer.\n\n"
     "Args: data (bytes), offset (int, default 0)."},

    {"upload_subresources", (PyCFunction)vk_Resource_upload_subresources,
     METH_VARARGS,
     "Batch upload rectangles to a texture.\n\n"
     "Args: rects (list of 5- or 6-tuples "
     "(data, x, y, width, height [, slice]))."},

    {"download", (PyCFunction)vk_Resource_download, METH_NOARGS,
     "Download an entire texture as a Python bytes object (RGBA)."},

    {"copy_to", (PyCFunction)vk_Resource_copy_to, METH_VARARGS,
     "Copy between resources (buffer ↔ buffer, buffer ↔ image, "
     "image ↔ image).\n\n"
     "Args:\n"
     "  dst (Resource)\n"
     "  size, src_offset, dst_offset (ints, buffer copies)\n"
     "  width, height, depth, src_x/y/z, dst_x/y/z, src_slice, dst_slice"},

    {"batch_copy_to_array", (PyCFunction)vk_Resource_batch_copy_to_array,
     METH_VARARGS,
     "Copy multiple rectangular regions from this 2D image to slices of dst "
     "array.\n"
     "Args: dst (vk.Resource array image), regions (list of "
     "(src_x,src_y,dst_slice,w,h))"},

    {"clear_color", (PyCFunction)vk_Resource_clear_color, METH_VARARGS,
     "Clear the entire image to a solid RGBA colour.\n\n"
     "Args: r, g, b, a (floats, 0.0-1.0)."},

    {nullptr, nullptr, 0, nullptr}};

PyTypeObject vk_Resource_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0).tp_name = "vulkan.Resource",
    .tp_basicsize = sizeof(vk_Resource),
    .tp_dealloc = (destructor)vk_Resource_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Resource_methods,
    .tp_members = vk_Resource_members,
};