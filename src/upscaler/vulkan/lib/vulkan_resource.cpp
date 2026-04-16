#include "vulkan_common.h"

/* ----------------------------------------------------------------------------
   Forward declarations
   ------------------------------------------------------------------------- */
static void vulkan_Resource_dealloc(vulkan_Resource *self);
static void vulkan_Heap_dealloc(vulkan_Heap *self);

/* ----------------------------------------------------------------------------
   Resource Type
   ------------------------------------------------------------------------- */
static PyMemberDef vulkan_Resource_members[] = {
    {"size", T_ULONGLONG, offsetof(vulkan_Resource, size), 0, "resource size"},
    {"width", T_UINT,
     offsetof(vulkan_Resource, image_extent) + offsetof(VkExtent3D, width), 0,
     "resource width"},
    {"height", T_UINT,
     offsetof(vulkan_Resource, image_extent) + offsetof(VkExtent3D, height), 0,
     "resource height"},
    {"depth", T_UINT,
     offsetof(vulkan_Resource, image_extent) + offsetof(VkExtent3D, depth), 0,
     "resource depth"},
    {"row_pitch", T_ULONGLONG, offsetof(vulkan_Resource, row_pitch), 0,
     "resource row pitch"},
    {"slices", T_UINT, offsetof(vulkan_Resource, slices), 0,
     "resource number of slices"},
    {"heap_size", T_ULONGLONG, offsetof(vulkan_Resource, heap_size), 0,
     "resource heap size"},
    {"heap_type", T_INT, offsetof(vulkan_Resource, heap_type), 0,
     "resource heap type"},
    {NULL}};

PyTypeObject vulkan_Resource_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Resource",
    .tp_basicsize = sizeof(vulkan_Resource),
    .tp_dealloc = (destructor)vulkan_Resource_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = vulkan_Resource_members,
};

/* ----------------------------------------------------------------------------
   Heap Type
   ------------------------------------------------------------------------- */
static PyMemberDef vulkan_Heap_members[] = {
    {"size", T_ULONGLONG, offsetof(vulkan_Heap, size), 0, "heap size"},
    {"heap_type", T_INT, offsetof(vulkan_Heap, heap_type), 0, "heap type"},
    {NULL}};

PyTypeObject vulkan_Heap_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Heap",
    .tp_basicsize = sizeof(vulkan_Heap),
    .tp_dealloc = (destructor)vulkan_Heap_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = vulkan_Heap_members,
};

/* ----------------------------------------------------------------------------
   Deallocators
   ------------------------------------------------------------------------- */
static void vulkan_Resource_dealloc(vulkan_Resource *self) {
  if (self->py_device) {
    VkDevice device = self->py_device->device;
    if (self->image_view)
      vkDestroyImageView(device, self->image_view, NULL);
    if (self->buffer_view)
      vkDestroyBufferView(device, self->buffer_view, NULL);
    if (!self->py_heap && self->memory)
      vkFreeMemory(device, self->memory, NULL);
    if (self->image)
      vkDestroyImage(device, self->image, NULL);
    if (self->buffer)
      vkDestroyBuffer(device, self->buffer, NULL);
    Py_DECREF(self->py_device);
  }
  Py_XDECREF(self->py_heap);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static void vulkan_Heap_dealloc(vulkan_Heap *self) {
  if (self->py_device && self->memory)
    vkFreeMemory(self->py_device->device, self->memory, NULL);
  Py_XDECREF(self->py_device);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* ----------------------------------------------------------------------------
   Helper: submit and wait
   ------------------------------------------------------------------------- */
static VkResult submit_and_wait(vulkan_Device *dev, VkCommandBuffer cmd) {
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  VkResult res = vkQueueSubmit(dev->queue, 1, &submit, VK_NULL_HANDLE);
  if (res != VK_SUCCESS)
    return res;

  Py_BEGIN_ALLOW_THREADS;
  vkQueueWaitIdle(dev->queue);
  Py_END_ALLOW_THREADS;
  return VK_SUCCESS;
}

/* ----------------------------------------------------------------------------
   upload
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_upload(vulkan_Resource *self, PyObject *args) {
  Py_buffer view;
  uint64_t offset = 0;
  if (!PyArg_ParseTuple(args, "y*|K", &view, &offset))
    return NULL;

  if (offset + view.len > self->size) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_ValueError,
                        "supplied buffer is bigger than resource size: (offset "
                        "%llu) %llu (expected no more than %llu)",
                        offset, (uint64_t)view.len, self->size);
  }

  if (!self->buffer || !self->memory) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_TypeError, "Resource is not a buffer");
  }

  void *mapped;
  VkResult res = vkMapMemory(self->py_device->device, self->memory,
                             self->heap_offset + offset, view.len, 0, &mapped);
  if (res != VK_SUCCESS) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_RuntimeError, "Failed to map buffer");
  }
  memcpy(mapped, view.buf, view.len);
  vkUnmapMemory(self->py_device->device, self->memory);
  PyBuffer_Release(&view);
  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   upload2d
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_upload2d(vulkan_Resource *self, PyObject *args) {
  Py_buffer view;
  uint32_t pitch, width, height, bpp;
  if (!PyArg_ParseTuple(args, "y*IIII", &view, &pitch, &width, &height, &bpp))
    return NULL;

  if (!self->buffer || !self->memory) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_TypeError, "Resource is not a buffer");
  }

  void *mapped;
  VkResult res = vkMapMemory(self->py_device->device, self->memory,
                             self->heap_offset, self->size, 0, &mapped);
  if (res != VK_SUCCESS) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_RuntimeError, "Failed to map buffer");
  }

  uint8_t *dst = (uint8_t *)mapped;
  const uint8_t *src = (const uint8_t *)view.buf;
  for (uint32_t y = 0; y < height; y++) {
    memcpy(dst + y * pitch, src + y * width * bpp, width * bpp);
  }

  vkUnmapMemory(self->py_device->device, self->memory);
  PyBuffer_Release(&view);
  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   copy_to (buffer → texture, texture → buffer, texture → texture)
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_copy_to(vulkan_Resource *self, PyObject *args) {
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
    return NULL;

  if (!PyObject_TypeCheck(dst_obj, &vulkan_Resource_Type))
    return PyErr_Format(PyExc_TypeError, "Expected a Resource object");

  vulkan_Resource *dst = (vulkan_Resource *)dst_obj;
  vulkan_Device *dev = self->py_device;

  if (dst->py_device != dev)
    return PyErr_Format(PyExc_ValueError,
                        "Resources belong to different devices");

  if (size == 0)
    size = self->size;

  // Validate copy parameters (simplified)
  if (self->buffer && dst->buffer) {
    if (src_offset + size > self->size || dst_offset + size > dst->size)
      return PyErr_Format(PyExc_ValueError, "Copy out of bounds");
  }

  VkCommandBuffer cmd = dev->command_buffer;
  VkResult res = vkResetCommandBuffer(cmd, 0);
  if (res != VK_SUCCESS) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to reset command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  if (self->buffer && dst->buffer) {
    VkBufferCopy region = {src_offset, dst_offset, size};
    vkCmdCopyBuffer(cmd, self->buffer, dst->buffer, 1, &region);
  } else if (self->buffer && dst->image) {
    if (src_offset + size > self->size) {
      vkEndCommandBuffer(cmd);
      return PyErr_Format(PyExc_ValueError, "Source buffer read out of bounds");
    }
    VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
    barrier.image = dst->image;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.baseArrayLayer = dst_slice;
    barrier.subresourceRange.layerCount = 1;
    barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                         &barrier);

    VkBufferImageCopy region = {0};
    region.bufferOffset = src_offset;
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.baseArrayLayer = dst_slice;
    region.imageSubresource.layerCount = 1;
    region.imageExtent = dst->image_extent;
    vkCmdCopyBufferToImage(cmd, self->buffer, dst->image,
                           VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

    barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.dstAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                         NULL, 1, &barrier);
  } else if (self->image && dst->buffer) {
    VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
    barrier.image = self->image;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.baseArrayLayer = src_slice;
    barrier.subresourceRange.layerCount = 1;
    barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                         &barrier);

    VkBufferImageCopy region = {0};
    region.bufferOffset = dst_offset;
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.baseArrayLayer = src_slice;
    region.imageSubresource.layerCount = 1;
    region.imageExtent = self->image_extent;
    vkCmdCopyImageToBuffer(cmd, self->image,
                           VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, dst->buffer, 1,
                           &region);

    barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    barrier.dstAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                         NULL, 1, &barrier);
  } else if (self->image && dst->image) {
    VkImageMemoryBarrier barriers[2] = {};
    barriers[0].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barriers[1].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
    barriers[0].image = self->image;
    barriers[0].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barriers[0].subresourceRange.levelCount = 1;
    barriers[0].subresourceRange.baseArrayLayer = src_slice;
    barriers[0].subresourceRange.layerCount = 1;
    barriers[0].oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    barriers[0].newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    barriers[0].srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    barriers[0].dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;

    barriers[1].image = dst->image;
    barriers[1].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barriers[1].subresourceRange.levelCount = 1;
    barriers[1].subresourceRange.baseArrayLayer = dst_slice;
    barriers[1].subresourceRange.layerCount = 1;
    barriers[1].oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    barriers[1].newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barriers[1].srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    barriers[1].dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;

    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 2,
                         barriers);

    VkImageCopy region = {0};
    region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.srcSubresource.baseArrayLayer = src_slice;
    region.srcSubresource.layerCount = 1;
    region.srcOffset = {(int32_t)src_x, (int32_t)src_y, (int32_t)src_z};
    region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.dstSubresource.baseArrayLayer = dst_slice;
    region.dstSubresource.layerCount = 1;
    region.dstOffset = {(int32_t)dst_x, (int32_t)dst_y, (int32_t)dst_z};
    region.extent = {width ? width : self->image_extent.width,
                     height ? height : self->image_extent.height,
                     depth ? depth : 1};

    vkCmdCopyImage(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   dst->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1,
                   &region);

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
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                         NULL, 2, barriers);
  } else {
    vkEndCommandBuffer(cmd);
    return PyErr_Format(PyExc_TypeError, "Unsupported copy combination");
  }

  vkEndCommandBuffer(cmd);
  res = submit_and_wait(dev, cmd);
  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError, "Copy submission failed: %d", res);

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   readback (buffer → bytes)
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_readback(vulkan_Resource *self, PyObject *args) {
  uint64_t size = 0, offset = 0;
  if (!PyArg_ParseTuple(args, "|KK", &size, &offset))
    return NULL;

  if (size == 0)
    size = self->size - offset;
  if (offset + size > self->size)
    return PyErr_Format(PyExc_ValueError, "Readback out of bounds");

  if (!self->buffer || !self->memory)
    return PyErr_Format(PyExc_TypeError, "Resource is not a buffer");

  void *mapped;
  VkResult res = vkMapMemory(self->py_device->device, self->memory,
                             self->heap_offset + offset, size, 0, &mapped);
  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError, "Failed to map buffer");

  PyObject *bytes = PyBytes_FromStringAndSize((char *)mapped, size);
  vkUnmapMemory(self->py_device->device, self->memory);
  return bytes;
}

/* ----------------------------------------------------------------------------
   download_texture (texture → bytes)
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_download_texture(vulkan_Resource *self,
                                           PyObject *ignored) {
  if (!self->image) {
    PyErr_SetString(PyExc_TypeError,
                    "download() can only be called on a Texture object");
    return NULL;
  }

  vulkan_Device *dev = self->py_device;
  VkDeviceSize buf_size = self->size;

  // Create device-local buffer
  VkBuffer device_buffer;
  VkDeviceMemory device_memory;
  VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
  binfo.size = buf_size;
  binfo.usage =
      VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT;
  if (vkCreateBuffer(dev->device, &binfo, NULL, &device_buffer) != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError, "Failed to create device buffer");

  VkMemoryRequirements mem_req;
  vkGetBufferMemoryRequirements(dev->device, device_buffer, &mem_req);
  VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
  alloc.allocationSize = mem_req.size;
  alloc.memoryTypeIndex = vulkan_get_memory_type_index_by_flag(
      &dev->mem_props, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
  if (vkAllocateMemory(dev->device, &alloc, NULL, &device_memory) !=
      VK_SUCCESS) {
    vkDestroyBuffer(dev->device, device_buffer, NULL);
    return PyErr_Format(PyExc_RuntimeError, "Failed to allocate device memory");
  }
  vkBindBufferMemory(dev->device, device_buffer, device_memory, 0);

  // Create staging buffer
  VkBuffer staging_buffer;
  VkDeviceMemory staging_memory;
  binfo.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;
  if (vkCreateBuffer(dev->device, &binfo, NULL, &staging_buffer) !=
      VK_SUCCESS) {
    vkDestroyBuffer(dev->device, device_buffer, NULL);
    vkFreeMemory(dev->device, device_memory, NULL);
    return PyErr_Format(PyExc_RuntimeError, "Failed to create staging buffer");
  }

  vkGetBufferMemoryRequirements(dev->device, staging_buffer, &mem_req);
  alloc.allocationSize = mem_req.size;
  alloc.memoryTypeIndex = vulkan_get_memory_type_index_by_flag(
      &dev->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                           VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
  if (vkAllocateMemory(dev->device, &alloc, NULL, &staging_memory) !=
      VK_SUCCESS) {
    vkDestroyBuffer(dev->device, device_buffer, NULL);
    vkFreeMemory(dev->device, device_memory, NULL);
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    return PyErr_Format(PyExc_RuntimeError,
                        "Failed to allocate staging memory");
  }
  vkBindBufferMemory(dev->device, staging_buffer, staging_memory, 0);

  // Record commands
  VkCommandBuffer cmd = dev->command_buffer;
  VkResult res = vkResetCommandBuffer(cmd, 0);
  if (res != VK_SUCCESS) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to reset command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  barrier.image = self->image;
  barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barrier.subresourceRange.levelCount = 1;
  barrier.subresourceRange.layerCount = 1;
  barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  VkBufferImageCopy region = {0};
  region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  region.imageSubresource.layerCount = 1;
  region.imageExtent = self->image_extent;
  vkCmdCopyImageToBuffer(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                         device_buffer, 1, &region);

  VkBufferMemoryBarrier buf_barrier = {VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER};
  buf_barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  buf_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  buf_barrier.buffer = device_buffer;
  buf_barrier.size = buf_size;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 1,
                       &buf_barrier, 0, NULL);

  VkBufferCopy copy = {0, 0, buf_size};
  vkCmdCopyBuffer(cmd, device_buffer, staging_buffer, 1, &copy);

  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  res = submit_and_wait(dev, cmd);
  if (res != VK_SUCCESS) {
    vkDestroyBuffer(dev->device, device_buffer, NULL);
    vkFreeMemory(dev->device, device_memory, NULL);
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    vkFreeMemory(dev->device, staging_memory, NULL);
    return PyErr_Format(PyExc_RuntimeError, "Download submission failed");
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_memory, 0, buf_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    vkDestroyBuffer(dev->device, device_buffer, NULL);
    vkFreeMemory(dev->device, device_memory, NULL);
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    vkFreeMemory(dev->device, staging_memory, NULL);
    return PyErr_Format(PyExc_RuntimeError, "Failed to map staging memory");
  }

  PyObject *bytes = PyBytes_FromStringAndSize((char *)mapped, buf_size);
  vkUnmapMemory(dev->device, staging_memory);

  vkDestroyBuffer(dev->device, device_buffer, NULL);
  vkFreeMemory(dev->device, device_memory, NULL);
  vkDestroyBuffer(dev->device, staging_buffer, NULL);
  vkFreeMemory(dev->device, staging_memory, NULL);

  return bytes;
}

/* ----------------------------------------------------------------------------
   vulkan_Resource_download_regions
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_download_regions(vulkan_Resource *self,
                                           PyObject *args) {
  PyObject *regions_list;
  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &regions_list))
    return NULL;

  if (!self->image) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
    return NULL;
  }

  Py_ssize_t num_regions = PyList_Size(regions_list);
  if (num_regions == 0) {
    return PyList_New(0);
  }

  vulkan_Device *dev = self->py_device;

  // First pass: validate regions and compute total buffer size
  struct Region {
    uint32_t x, y, w, h;
    VkDeviceSize offset;
    VkDeviceSize size;
  };
  std::vector<Region> regions;
  regions.reserve(num_regions);
  VkDeviceSize total_size = 0;

  for (Py_ssize_t i = 0; i < num_regions; i++) {
    PyObject *tuple = PyList_GetItem(regions_list, i);
    Region r = {0};
    if (!PyArg_ParseTuple(tuple, "IIII", &r.x, &r.y, &r.w, &r.h)) {
      return NULL;
    }
    if (r.w == 0 || r.h == 0) {
      PyErr_Format(PyExc_ValueError, "Region %zd has zero size", i);
      return NULL;
    }
    if (r.x + r.w > self->image_extent.width ||
        r.y + r.h > self->image_extent.height) {
      PyErr_Format(
          PyExc_ValueError,
          "Region %zd (%u,%u %ux%u) exceeds texture dimensions (%ux%u)", i, r.x,
          r.y, r.w, r.h, self->image_extent.width, self->image_extent.height);
      return NULL;
    }
    r.size = r.w * r.h * 4;
    r.offset = total_size;
    total_size += r.size;
    regions.push_back(r);
  }

  // Create a staging buffer (use device's pool if available and large enough)
  VkBuffer staging_buffer = VK_NULL_HANDLE;
  VkDeviceMemory staging_memory = VK_NULL_HANDLE;
  int used_pool = 0;

  if (dev->staging_pool.count > 0 &&
      total_size <= dev->staging_pool.sizes[dev->staging_pool.next]) {
    int idx = dev->staging_pool.next;
    dev->staging_pool.next = (idx + 1) % dev->staging_pool.count;
    staging_buffer = dev->staging_pool.buffers[idx];
    staging_memory = dev->staging_pool.memories[idx];
    used_pool = 1;
  } else {
    VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    binfo.size = total_size;
    binfo.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    if (vkCreateBuffer(dev->device, &binfo, NULL, &staging_buffer) !=
        VK_SUCCESS) {
      return PyErr_Format(PyExc_RuntimeError,
                          "Failed to create staging buffer");
    }

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(dev->device, staging_buffer, &mem_req);
    VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc.allocationSize = mem_req.size;
    alloc.memoryTypeIndex = vulkan_get_memory_type_index_by_flag(
        &dev->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                             VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    if (vkAllocateMemory(dev->device, &alloc, NULL, &staging_memory) !=
        VK_SUCCESS) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      return PyErr_Format(PyExc_RuntimeError,
                          "Failed to allocate staging memory");
    }
    vkBindBufferMemory(dev->device, staging_buffer, staging_memory, 0);
  }

  // Record command buffer
  VkCommandBuffer cmd = dev->command_buffer;
  VkResult res = vkResetCommandBuffer(cmd, 0);
  if (res != VK_SUCCESS) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to reset command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  // Transition source texture to TRANSFER_SRC_OPTIMAL
  VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  barrier.image = self->image;
  barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barrier.subresourceRange.levelCount = 1;
  barrier.subresourceRange.layerCount = 1;
  barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  // Copy each region
  for (const auto &r : regions) {
    VkBufferImageCopy region = {0};
    region.bufferOffset = r.offset;
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.layerCount = 1;
    region.imageOffset = {(int32_t)r.x, (int32_t)r.y, 0};
    region.imageExtent = {r.w, r.h, 1};

    vkCmdCopyImageToBuffer(cmd, self->image,
                           VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, staging_buffer,
                           1, &region);
  }

  // Transition back to GENERAL
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  // Submit and wait
  res = submit_and_wait(dev, cmd);
  if (res != VK_SUCCESS) {
    if (!used_pool) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      vkFreeMemory(dev->device, staging_memory, NULL);
    }
    return PyErr_Format(PyExc_RuntimeError, "Download submission failed: %d",
                        res);
  }

  // Map staging buffer and extract data
  void *mapped;
  res = vkMapMemory(dev->device, staging_memory, 0, total_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    if (!used_pool) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      vkFreeMemory(dev->device, staging_memory, NULL);
    }
    return PyErr_Format(PyExc_RuntimeError, "Failed to map staging memory");
  }

  PyObject *result_list = PyList_New(num_regions);
  uint8_t *base = (uint8_t *)mapped;
  for (size_t i = 0; i < regions.size(); i++) {
    PyObject *bytes = PyBytes_FromStringAndSize(
        (char *)(base + regions[i].offset), regions[i].size);
    if (!bytes) {
      vkUnmapMemory(dev->device, staging_memory);
      Py_DECREF(result_list);
      if (!used_pool) {
        vkDestroyBuffer(dev->device, staging_buffer, NULL);
        vkFreeMemory(dev->device, staging_memory, NULL);
      }
      return PyErr_NoMemory();
    }
    PyList_SetItem(result_list, i, bytes);
  }

  vkUnmapMemory(dev->device, staging_memory);

  if (!used_pool) {
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    vkFreeMemory(dev->device, staging_memory, NULL);
  }

  return result_list;
}

/* ----------------------------------------------------------------------------
   upload_subresource
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_upload_subresource(vulkan_Resource *self,
                                             PyObject *args) {
  Py_buffer view;
  uint32_t x, y, width, height;
  if (!PyArg_ParseTuple(args, "y*IIII", &view, &x, &y, &width, &height))
    return NULL;

  if (!self->image) {
    PyBuffer_Release(&view);
    PyErr_SetString(PyExc_TypeError,
                    "upload_subresource only supported for textures");
    return NULL;
  }

  if (width == 0 || height == 0) {
    PyBuffer_Release(&view);
    Py_RETURN_NONE;
  }

  if (x + width > self->image_extent.width ||
      y + height > self->image_extent.height) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_ValueError,
                        "Subresource rectangle (%u,%u %ux%u) exceeds texture "
                        "dimensions (%ux%u)",
                        x, y, width, height, self->image_extent.width,
                        self->image_extent.height);
  }

  vulkan_Device *dev = self->py_device;
  VkDeviceSize buf_size = width * height * 4;

  VkBuffer staging_buffer = VK_NULL_HANDLE;
  VkDeviceMemory staging_memory = VK_NULL_HANDLE;
  int used_pool = 0;

  if (dev->staging_pool.count > 0 &&
      buf_size <= dev->staging_pool.sizes[dev->staging_pool.next]) {
    int idx = dev->staging_pool.next;
    dev->staging_pool.next = (idx + 1) % dev->staging_pool.count;
    staging_buffer = dev->staging_pool.buffers[idx];
    staging_memory = dev->staging_pool.memories[idx];
    used_pool = 1;
  } else {
    VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    binfo.size = buf_size;
    binfo.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT;
    if (vkCreateBuffer(dev->device, &binfo, NULL, &staging_buffer) !=
        VK_SUCCESS) {
      PyBuffer_Release(&view);
      return PyErr_Format(PyExc_RuntimeError,
                          "Failed to create staging buffer");
    }

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(dev->device, staging_buffer, &mem_req);
    VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc.allocationSize = mem_req.size;
    alloc.memoryTypeIndex = vulkan_get_memory_type_index_by_flag(
        &dev->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                             VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    if (vkAllocateMemory(dev->device, &alloc, NULL, &staging_memory) !=
        VK_SUCCESS) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      PyBuffer_Release(&view);
      return PyErr_Format(PyExc_RuntimeError,
                          "Failed to allocate staging memory");
    }
    vkBindBufferMemory(dev->device, staging_buffer, staging_memory, 0);
  }

  void *mapped;
  VkResult res =
      vkMapMemory(dev->device, staging_memory, 0, buf_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    vkFreeMemory(dev->device, staging_memory, NULL);
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_RuntimeError, "Failed to map staging memory");
  }
  memcpy(mapped, view.buf, view.len);
  vkUnmapMemory(dev->device, staging_memory);
  PyBuffer_Release(&view);

  VkCommandBuffer cmd = dev->command_buffer;
  res = vkResetCommandBuffer(cmd, 0);
  if (res != VK_SUCCESS) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to reset command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  barrier.image = self->image;
  barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barrier.subresourceRange.levelCount = 1;
  barrier.subresourceRange.layerCount = 1;
  barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  VkBufferImageCopy region = {0};
  region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  region.imageSubresource.layerCount = 1;
  region.imageOffset = {(int32_t)x, (int32_t)y, 0};
  region.imageExtent = {width, height, 1};
  vkCmdCopyBufferToImage(cmd, staging_buffer, self->image,
                         VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  res = submit_and_wait(dev, cmd);
  if (!used_pool) {
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    vkFreeMemory(dev->device, staging_memory, NULL);
  }

  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError, "Upload submission failed");

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   upload_subresources – batch upload of multiple rectangles
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_upload_subresources(vulkan_Resource *self,
                                              PyObject *args) {
  PyObject *rects_list;
  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &rects_list))
    return NULL;

  if (!self->image) {
    PyErr_SetString(PyExc_TypeError,
                    "upload_subresources only supported for textures");
    return NULL;
  }

  Py_ssize_t num_rects = PyList_Size(rects_list);
  if (num_rects == 0) {
    Py_RETURN_NONE;
  }

  vulkan_Device *dev = self->py_device;

  // First pass: validate all rectangles and calculate total size
  struct RectInfo {
    uint32_t x, y, w, h;
    Py_buffer view;      // will hold the buffer temporarily
    VkDeviceSize offset; // offset in the combined staging buffer
  };
  std::vector<RectInfo> rects;
  rects.reserve(num_rects);
  VkDeviceSize total_size = 0;

  for (Py_ssize_t i = 0; i < num_rects; i++) {
    PyObject *tuple = PyList_GetItem(rects_list, i);
    if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
      PyErr_Format(PyExc_TypeError,
                   "Item %zd must be a 5-tuple (data, x, y, width, height)", i);
      return NULL;
    }

    RectInfo info = {0};
    if (!PyArg_ParseTuple(tuple, "y*IIII", &info.view, &info.x, &info.y,
                          &info.w, &info.h)) {
      return NULL;
    }

    if (info.w == 0 || info.h == 0) {
      PyBuffer_Release(&info.view);
      continue;
    }

    if (info.x + info.w > self->image_extent.width ||
        info.y + info.h > self->image_extent.height) {
      PyBuffer_Release(&info.view);
      PyErr_Format(PyExc_ValueError,
                   "Rectangle (%u,%u %ux%u) exceeds texture dimensions (%ux%u)",
                   info.x, info.y, info.w, info.h, self->image_extent.width,
                   self->image_extent.height);
      // Cleanup previously acquired buffers
      for (auto &r : rects)
        PyBuffer_Release(&r.view);
      return NULL;
    }

    VkDeviceSize data_size = info.w * info.h * 4;
    info.offset = total_size;
    total_size += data_size;
    rects.push_back(info);
  }

  if (rects.empty()) {
    Py_RETURN_NONE;
  }

  // Allocate or reuse a staging buffer large enough for all data
  VkBuffer staging_buffer = VK_NULL_HANDLE;
  VkDeviceMemory staging_memory = VK_NULL_HANDLE;
  int used_pool = 0;

  if (dev->staging_pool.count > 0 &&
      total_size <= dev->staging_pool.sizes[dev->staging_pool.next]) {
    int idx = dev->staging_pool.next;
    dev->staging_pool.next = (idx + 1) % dev->staging_pool.count;
    staging_buffer = dev->staging_pool.buffers[idx];
    staging_memory = dev->staging_pool.memories[idx];
    used_pool = 1;
  } else {
    VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    binfo.size = total_size;
    binfo.usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    if (vkCreateBuffer(dev->device, &binfo, NULL, &staging_buffer) !=
        VK_SUCCESS) {
      for (auto &r : rects)
        PyBuffer_Release(&r.view);
      return PyErr_Format(PyExc_RuntimeError,
                          "Failed to create staging buffer");
    }

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(dev->device, staging_buffer, &mem_req);
    VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc.allocationSize = mem_req.size;
    alloc.memoryTypeIndex = vulkan_get_memory_type_index_by_flag(
        &dev->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                             VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    if (vkAllocateMemory(dev->device, &alloc, NULL, &staging_memory) !=
        VK_SUCCESS) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      for (auto &r : rects)
        PyBuffer_Release(&r.view);
      return PyErr_Format(PyExc_RuntimeError,
                          "Failed to allocate staging memory");
    }
    vkBindBufferMemory(dev->device, staging_buffer, staging_memory, 0);
  }

  // Map the staging buffer and copy all rectangle data into it
  void *mapped;
  VkResult res =
      vkMapMemory(dev->device, staging_memory, 0, total_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    if (!used_pool) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      vkFreeMemory(dev->device, staging_memory, NULL);
    }
    for (auto &r : rects)
      PyBuffer_Release(&r.view);
    return PyErr_Format(PyExc_RuntimeError, "Failed to map staging memory");
  }

  uint8_t *dst = (uint8_t *)mapped;
  for (auto &r : rects) {
    memcpy(dst + r.offset, r.view.buf, r.view.len);
    PyBuffer_Release(&r.view);
  }
  vkUnmapMemory(dev->device, staging_memory);

  // Record command buffer with all copy commands
  VkCommandBuffer cmd = dev->command_buffer;
  res = vkResetCommandBuffer(cmd, 0);
  if (res != VK_SUCCESS) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to reset command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  // Transition destination image to TRANSFER_DST_OPTIMAL
  VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  barrier.image = self->image;
  barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barrier.subresourceRange.levelCount = 1;
  barrier.subresourceRange.layerCount = 1;
  barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.srcAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  // Issue all copy commands
  for (auto &r : rects) {
    VkBufferImageCopy region = {0};
    region.bufferOffset = r.offset;
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.layerCount = 1;
    region.imageOffset = {(int32_t)r.x, (int32_t)r.y, 0};
    region.imageExtent = {r.w, r.h, 1};

    vkCmdCopyBufferToImage(cmd, staging_buffer, self->image,
                           VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
  }

  // Transition back to GENERAL
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  // Submit and wait
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  res = vkQueueSubmit(dev->queue, 1, &submit, VK_NULL_HANDLE);
  if (res != VK_SUCCESS) {
    if (!used_pool) {
      vkDestroyBuffer(dev->device, staging_buffer, NULL);
      vkFreeMemory(dev->device, staging_memory, NULL);
    }
    return PyErr_Format(PyExc_RuntimeError, "Queue submission failed: %d", res);
  }

  Py_BEGIN_ALLOW_THREADS;
  vkQueueWaitIdle(dev->queue);
  Py_END_ALLOW_THREADS;

  if (!used_pool) {
    vkDestroyBuffer(dev->device, staging_buffer, NULL);
    vkFreeMemory(dev->device, staging_memory, NULL);
  }

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Method table
   ------------------------------------------------------------------------- */
PyMethodDef vulkan_Resource_methods[] = {
    {"upload", (PyCFunction)vulkan_Resource_upload, METH_VARARGS, NULL},
    {"upload2d", (PyCFunction)vulkan_Resource_upload2d, METH_VARARGS, NULL},
    {"copy_to", (PyCFunction)vulkan_Resource_copy_to, METH_VARARGS, NULL},
    {"readback", (PyCFunction)vulkan_Resource_readback, METH_VARARGS, NULL},
    {"download", (PyCFunction)vulkan_Resource_download_texture, METH_NOARGS,
     NULL},
    {"download_regions", (PyCFunction)vulkan_Resource_download_regions,
     METH_VARARGS, "Download multiple rectangular regions from a texture"},
    {"upload_subresource", (PyCFunction)vulkan_Resource_upload_subresource,
     METH_VARARGS, NULL},
    {"upload_subresources", (PyCFunction)vulkan_Resource_upload_subresources,
     METH_VARARGS,
     "Upload multiple subresource rectangles to a texture in one submission"},
    {NULL}};
