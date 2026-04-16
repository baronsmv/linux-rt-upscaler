/**
 * @file vulkan_resource.c
 * @brief Implementation of Vulkan resource (buffer/texture) Python type.
 *
 * This module provides methods for uploading data, copying between resources,
 * reading back data, downloading textures, and managing sparse tile binding.
 */

#include "vulkan_resource.h"
#include "vulkan_device.h"
#include "vulkan_utils.h"
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------------------------------
   Forward declarations of static helpers
   ------------------------------------------------------------------------- */
static VkResult copy_buffer_to_buffer(VkComp_Resource *src,
                                      VkComp_Resource *dst, uint64_t size,
                                      uint64_t src_offset, uint64_t dst_offset);
static VkResult copy_buffer_to_texture(VkComp_Resource *src,
                                       VkComp_Resource *dst, uint64_t size,
                                       uint64_t src_offset, uint32_t dst_slice);
static VkResult copy_texture_to_buffer(VkComp_Resource *src,
                                       VkComp_Resource *dst, uint64_t size,
                                       uint64_t dst_offset, uint32_t src_slice);
static VkResult copy_texture_to_texture(VkComp_Resource *src,
                                        VkComp_Resource *dst, uint32_t src_x,
                                        uint32_t src_y, uint32_t src_z,
                                        uint32_t dst_x, uint32_t dst_y,
                                        uint32_t dst_z, uint32_t width,
                                        uint32_t height, uint32_t depth,
                                        uint32_t src_slice, uint32_t dst_slice);

/* -------------------------------------------------------------------------
   Python type definition
   ------------------------------------------------------------------------- */
static PyMemberDef VkComp_Resource_members[] = {
    {"size", Py_T_ULONGLONG, offsetof(VkComp_Resource, size), 0,
     "Resource size in bytes"},
    {"width", Py_T_UINT, offsetof(VkComp_Resource, image_extent.width), 0,
     "Texture width"},
    {"height", Py_T_UINT, offsetof(VkComp_Resource, image_extent.height), 0,
     "Texture height"},
    {"depth", Py_T_UINT, offsetof(VkComp_Resource, image_extent.depth), 0,
     "Texture depth"},
    {"row_pitch", Py_T_ULONGLONG, offsetof(VkComp_Resource, row_pitch), 0,
     "Row pitch in bytes"},
    {"slices", Py_T_UINT, offsetof(VkComp_Resource, slices), 0,
     "Number of array slices"},
    {"heap_size", Py_T_ULONGLONG, offsetof(VkComp_Resource, heap_size), 0,
     "Actual memory size allocated"},
    {"heap_type", Py_T_INT, offsetof(VkComp_Resource, heap_type), 0,
     "Heap type (0=DEFAULT,1=UPLOAD,2=READBACK)"},
    {"tiles_x", Py_T_UINT, offsetof(VkComp_Resource, tiles_x), 0,
     "Number of tiles in X (sparse)"},
    {"tiles_y", Py_T_UINT, offsetof(VkComp_Resource, tiles_y), 0,
     "Number of tiles in Y (sparse)"},
    {"tiles_z", Py_T_UINT, offsetof(VkComp_Resource, tiles_z), 0,
     "Number of tiles in Z (sparse)"},
    {"tile_width", Py_T_UINT, offsetof(VkComp_Resource, tile_width), 0,
     "Tile width in pixels (sparse)"},
    {"tile_height", Py_T_UINT, offsetof(VkComp_Resource, tile_height), 0,
     "Tile height in pixels (sparse)"},
    {"tile_depth", Py_T_UINT, offsetof(VkComp_Resource, tile_depth), 0,
     "Tile depth in pixels (sparse)"},
    {NULL}};

static PyMethodDef VkComp_Resource_methods[] = {
    {"upload", (PyCFunction)VkComp_Resource_Upload, METH_VARARGS,
     "Upload data to a buffer at the given offset."},
    {"upload2d", (PyCFunction)VkComp_Resource_Upload2D, METH_VARARGS,
     "Upload 2D data with custom pitch to a buffer."},
    {"copy_to", (PyCFunction)VkComp_Resource_CopyTo, METH_VARARGS,
     "Copy data to another resource (buffer or texture)."},
    {"readback", (PyCFunction)VkComp_Resource_Readback, METH_VARARGS,
     "Read back buffer data into a Python bytes object."},
    {"download", (PyCFunction)VkComp_Resource_Download, METH_NOARGS,
     "Download texture contents as RGBA8 bytes."},
    {"download_regions", (PyCFunction)VkComp_Resource_DownloadRegions,
     METH_VARARGS, "Download multiple rectangular regions from a texture."},
    {"upload_subresource", (PyCFunction)VkComp_Resource_UploadSubresource,
     METH_VARARGS, "Upload data to a rectangular region of a texture."},
    {"upload_subresources", (PyCFunction)VkComp_Resource_UploadSubresources,
     METH_VARARGS, "Upload multiple subresource rectangles in one submission."},
    {"bind_tile", (PyCFunction)VkComp_Resource_BindTile, METH_VARARGS,
     "Bind a heap to a sparse tile."},
    {NULL, NULL, 0, NULL}};

PyTypeObject VkComp_Resource_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Resource",
    .tp_basicsize = sizeof(VkComp_Resource),
    .tp_dealloc = (destructor)VkComp_Resource_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = VkComp_Resource_methods,
    .tp_members = VkComp_Resource_members,
};

/* -------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
void VkComp_Resource_Dealloc(VkComp_Resource *self) {
  if (self->device && self->device->device) {
    VkDevice dev = self->device->device;
    if (self->image_view)
      vkDestroyImageView(dev, self->image_view, NULL);
    if (self->buffer_view)
      vkDestroyBufferView(dev, self->buffer_view, NULL);
    if (self->image)
      vkDestroyImage(dev, self->image, NULL);
    if (self->buffer)
      vkDestroyBuffer(dev, self->buffer, NULL);
    if (self->memory && !self->heap) {
      vkFreeMemory(dev, self->memory, NULL);
    }
    Py_DECREF(self->device);
  }
  Py_XDECREF(self->heap);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* -------------------------------------------------------------------------
   upload(data, offset=0)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_Upload(VkComp_Resource *self, PyObject *args) {
  Py_buffer view;
  unsigned long long offset = 0;
  if (!PyArg_ParseTuple(args, "y*|K", &view, &offset))
    return NULL;

  if (!VkComp_Resource_IsBuffer(self)) {
    PyBuffer_Release(&view);
    PyErr_SetString(PyExc_TypeError, "upload() only supported for buffers");
    return NULL;
  }

  if (offset + view.len > self->size) {
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_ValueError,
                 "Upload size %zd at offset %llu exceeds buffer size %llu",
                 view.len, offset, self->size);
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev) {
    PyBuffer_Release(&view);
    return NULL;
  }

  /* Map memory directly if host-visible */
  vkGetPhysicalDeviceMemoryProperties(dev->physical_device, &dev->mem_props);
  /* Simplified: assume UPLOAD/READBACK heaps are host-visible */
  if (self->heap_type == 1 || self->heap_type == 2) {
    void *mapped;
    VkResult res =
        vkMapMemory(dev->device, self->memory, self->heap_offset + offset,
                    view.len, 0, &mapped);
    if (res != VK_SUCCESS) {
      PyBuffer_Release(&view);
      PyErr_Format(PyExc_RuntimeError, "Failed to map buffer memory: %d", res);
      return NULL;
    }
    memcpy(mapped, view.buf, view.len);
    vkUnmapMemory(dev->device, self->memory);
    PyBuffer_Release(&view);
    Py_RETURN_NONE;
  }

  /* Otherwise, use staging buffer */
  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(dev, view.len, &staging_buf,
                                                    &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, view.len, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }
  memcpy(mapped, view.buf, view.len);
  vkUnmapMemory(dev->device, staging_mem);
  PyBuffer_Release(&view);

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkBufferCopy copy_region = {
      .srcOffset = 0,
      .dstOffset = offset,
      .size = view.len,
  };
  vkCmdCopyBuffer(cmd, staging_buf, self->buffer, 1, &copy_region);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Upload submission failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   upload2d(data, pitch, width, height, bytes_per_pixel)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_Upload2D(VkComp_Resource *self, PyObject *args) {
  Py_buffer view;
  unsigned int pitch, width, height, bpp;
  if (!PyArg_ParseTuple(args, "y*IIII", &view, &pitch, &width, &height, &bpp))
    return NULL;

  if (!VkComp_Resource_IsBuffer(self)) {
    PyBuffer_Release(&view);
    PyErr_SetString(PyExc_TypeError, "upload2d() only supported for buffers");
    return NULL;
  }

  if (pitch < width * bpp) {
    PyBuffer_Release(&view);
    PyErr_SetString(PyExc_ValueError,
                    "Pitch must be at least width * bytes_per_pixel");
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev) {
    PyBuffer_Release(&view);
    return NULL;
  }

  /* If buffer is host-visible, upload directly row-by-row */
  if (self->heap_type == 1 || self->heap_type == 2) {
    void *mapped;
    VkResult res = vkMapMemory(dev->device, self->memory, self->heap_offset,
                               self->size, 0, &mapped);
    if (res != VK_SUCCESS) {
      PyBuffer_Release(&view);
      PyErr_Format(PyExc_RuntimeError, "Failed to map buffer: %d", res);
      return NULL;
    }
    uint8_t *dst = (uint8_t *)mapped;
    const uint8_t *src = (const uint8_t *)view.buf;
    for (unsigned int y = 0; y < height; y++) {
      memcpy(dst + y * pitch, src + y * width * bpp, width * bpp);
    }
    vkUnmapMemory(dev->device, self->memory);
    PyBuffer_Release(&view);
    Py_RETURN_NONE;
  }

  /* Staging buffer approach */
  VkDeviceSize upload_size = pitch * height;
  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(
      dev, upload_size, &staging_buf, &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, upload_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }
  uint8_t *dst = (uint8_t *)mapped;
  const uint8_t *src = (const uint8_t *)view.buf;
  for (unsigned int y = 0; y < height; y++) {
    memcpy(dst + y * pitch, src + y * width * bpp, width * bpp);
  }
  vkUnmapMemory(dev->device, staging_mem);
  PyBuffer_Release(&view);

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkBufferCopy copy_region = {
      .srcOffset = 0,
      .dstOffset = 0,
      .size = upload_size,
  };
  vkCmdCopyBuffer(cmd, staging_buf, self->buffer, 1, &copy_region);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Upload submission failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   copy_to(destination, ...)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_CopyTo(VkComp_Resource *self, PyObject *args) {
  PyObject *dst_obj;
  unsigned long long size = 0, src_offset = 0, dst_offset = 0;
  unsigned int width = 0, height = 0, depth = 0;
  unsigned int src_x = 0, src_y = 0, src_z = 0;
  unsigned int dst_x = 0, dst_y = 0, dst_z = 0;
  unsigned int src_slice = 0, dst_slice = 0;

  if (!PyArg_ParseTuple(args, "O|KKKIIIIIIIIIII", &dst_obj, &size, &src_offset,
                        &dst_offset, &width, &height, &depth, &src_x, &src_y,
                        &src_z, &dst_x, &dst_y, &dst_z, &src_slice, &dst_slice))
    return NULL;

  if (!PyObject_TypeCheck(dst_obj, &VkComp_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Destination must be a Resource");
    return NULL;
  }

  VkComp_Resource *dst = (VkComp_Resource *)dst_obj;
  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;
  if (dst->device != self->device) {
    PyErr_SetString(PyExc_ValueError, "Resources belong to different devices");
    return NULL;
  }

  bool src_is_buf = VkComp_Resource_IsBuffer(self);
  bool dst_is_buf = VkComp_Resource_IsBuffer(dst);

  if (size == 0 && src_is_buf)
    size = self->size;

  /* Validate copy parameters */
  if (!vkcomp_check_copy_to(
          src_is_buf, dst_is_buf, size, src_offset, dst_offset, self->size,
          dst->size, src_x, src_y, src_z, src_slice, self->slices, dst_slice,
          dst->slices, self->image_extent.width, self->image_extent.height,
          self->image_extent.depth, dst->image_extent.width,
          dst->image_extent.height, dst->image_extent.depth, &dst_x, &dst_y,
          &dst_z, &width, &height, &depth)) {
    return NULL;
  }

  VkResult res = VK_SUCCESS;
  if (src_is_buf && dst_is_buf) {
    res = copy_buffer_to_buffer(self, dst, size, src_offset, dst_offset);
  } else if (src_is_buf && !dst_is_buf) {
    res = copy_buffer_to_texture(self, dst, size, src_offset, dst_slice);
  } else if (!src_is_buf && dst_is_buf) {
    res = copy_texture_to_buffer(self, dst, size, dst_offset, src_slice);
  } else {
    res = copy_texture_to_texture(self, dst, src_x, src_y, src_z, dst_x, dst_y,
                                  dst_z, width, height, depth, src_slice,
                                  dst_slice);
  }

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Copy operation failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   readback(size=0, offset=0) -> bytes
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_Readback(VkComp_Resource *self, PyObject *args) {
  unsigned long long size = 0, offset = 0;
  if (!PyArg_ParseTuple(args, "|KK", &size, &offset))
    return NULL;

  if (!VkComp_Resource_IsBuffer(self)) {
    PyErr_SetString(PyExc_TypeError, "readback() only supported for buffers");
    return NULL;
  }

  if (size == 0)
    size = self->size - offset;
  if (offset + size > self->size) {
    PyErr_Format(PyExc_ValueError,
                 "Readback out of bounds: offset=%llu, size=%llu, max=%llu",
                 offset, size, self->size);
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  /* If buffer is host-visible, read directly */
  if (self->heap_type == 1 || self->heap_type == 2) {
    void *mapped;
    VkResult res = vkMapMemory(dev->device, self->memory,
                               self->heap_offset + offset, size, 0, &mapped);
    if (res != VK_SUCCESS) {
      PyErr_Format(PyExc_RuntimeError, "Failed to map buffer: %d", res);
      return NULL;
    }
    PyObject *bytes =
        PyBytes_FromStringAndSize((char *)mapped, (Py_ssize_t)size);
    vkUnmapMemory(dev->device, self->memory);
    return bytes;
  }

  /* Use staging buffer for device-local buffers */
  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(dev, size, &staging_buf,
                                                    &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkBufferCopy copy_region = {
      .srcOffset = offset,
      .dstOffset = 0,
      .size = size,
  };
  vkCmdCopyBuffer(cmd, self->buffer, staging_buf, 1, &copy_region);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Readback submission failed: %d", res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, size, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }
  PyObject *bytes = PyBytes_FromStringAndSize((char *)mapped, (Py_ssize_t)size);
  vkUnmapMemory(dev->device, staging_mem);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);
  return bytes;
}

/* -------------------------------------------------------------------------
   download() -> bytes (texture only)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_Download(VkComp_Resource *self, PyObject *args) {
  if (!VkComp_Resource_IsTexture(self)) {
    PyErr_SetString(PyExc_TypeError, "download() only supported for textures");
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  VkDeviceSize size = self->size;
  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(dev, size, &staging_buf,
                                                    &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  /* Transition to TRANSFER_SRC_OPTIMAL */
  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
      .dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT,
      .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
      .newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = self->image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = 0,
              .layerCount = self->slices,
          },
  };
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  VkBufferImageCopy region = {
      .bufferOffset = 0,
      .bufferRowLength = 0,
      .bufferImageHeight = 0,
      .imageSubresource =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .mipLevel = 0,
              .baseArrayLayer = 0,
              .layerCount = self->slices,
          },
      .imageExtent = self->image_extent,
  };
  vkCmdCopyImageToBuffer(cmd, self->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                         staging_buf, 1, &region);

  /* Transition back to GENERAL */
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Download submission failed: %d", res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, size, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }
  PyObject *bytes = PyBytes_FromStringAndSize((char *)mapped, (Py_ssize_t)size);
  vkUnmapMemory(dev->device, staging_mem);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);
  return bytes;
}

/* -------------------------------------------------------------------------
   download_regions(regions) -> list of bytes
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_DownloadRegions(VkComp_Resource *self,
                                          PyObject *args) {
  PyObject *regions_list;
  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &regions_list))
    return NULL;

  if (!VkComp_Resource_IsTexture(self)) {
    PyErr_SetString(PyExc_TypeError,
                    "download_regions() only supported for textures");
    return NULL;
  }

  Py_ssize_t num_regions = PyList_Size(regions_list);
  if (num_regions == 0)
    return PyList_New(0);

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  /* Parse regions and compute total buffer size */
  typedef struct {
    uint32_t x, y, w, h;
    VkDeviceSize offset;
    VkDeviceSize size;
  } Region;
  Region *regions = PyMem_Malloc(num_regions * sizeof(Region));
  if (!regions)
    return PyErr_NoMemory();

  VkDeviceSize total_size = 0;
  for (Py_ssize_t i = 0; i < num_regions; i++) {
    PyObject *tuple = PyList_GetItem(regions_list, i);
    if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 4) {
      PyMem_Free(regions);
      PyErr_SetString(PyExc_TypeError,
                      "Each region must be a 4-tuple (x, y, width, height)");
      return NULL;
    }
    Region *r = &regions[i];
    if (!PyArg_ParseTuple(tuple, "IIII", &r->x, &r->y, &r->w, &r->h)) {
      PyMem_Free(regions);
      return NULL;
    }
    if (r->w == 0 || r->h == 0) {
      PyMem_Free(regions);
      PyErr_Format(PyExc_ValueError, "Region %zd has zero size", i);
      return NULL;
    }
    if (r->x + r->w > self->image_extent.width ||
        r->y + r->h > self->image_extent.height) {
      PyMem_Free(regions);
      PyErr_Format(
          PyExc_ValueError,
          "Region %zd (%u,%u %ux%u) exceeds texture dimensions (%ux%u)", i,
          r->x, r->y, r->w, r->h, self->image_extent.width,
          self->image_extent.height);
      return NULL;
    }
    r->size = r->w * r->h * 4;
    r->offset = total_size;
    total_size += r->size;
  }

  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(
      dev, total_size, &staging_buf, &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    PyMem_Free(regions);
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyMem_Free(regions);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  /* Transition source to TRANSFER_SRC_OPTIMAL */
  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
      .dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT,
      .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
      .newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = self->image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = 0,
              .layerCount = 1,
          },
  };
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  /* Copy each region */
  for (Py_ssize_t i = 0; i < num_regions; i++) {
    Region *r = &regions[i];
    VkBufferImageCopy copy_region = {
        .bufferOffset = r->offset,
        .imageSubresource =
            {
                .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                .mipLevel = 0,
                .baseArrayLayer = 0,
                .layerCount = 1,
            },
        .imageOffset = {(int32_t)r->x, (int32_t)r->y, 0},
        .imageExtent = {r->w, r->h, 1},
    };
    vkCmdCopyImageToBuffer(cmd, self->image,
                           VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, staging_buf, 1,
                           &copy_region);
  }

  /* Transition back to GENERAL */
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyMem_Free(regions);
    PyErr_Format(PyExc_RuntimeError, "Download submission failed: %d", res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, total_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyMem_Free(regions);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }

  PyObject *result = PyList_New(num_regions);
  uint8_t *base = (uint8_t *)mapped;
  for (Py_ssize_t i = 0; i < num_regions; i++) {
    PyObject *bytes = PyBytes_FromStringAndSize(
        (char *)(base + regions[i].offset), (Py_ssize_t)regions[i].size);
    if (!bytes) {
      Py_DECREF(result);
      result = NULL;
      break;
    }
    PyList_SetItem(result, i, bytes);
  }

  vkUnmapMemory(dev->device, staging_mem);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);
  PyMem_Free(regions);
  return result;
}

/* -------------------------------------------------------------------------
   upload_subresource(data, x, y, width, height)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_UploadSubresource(VkComp_Resource *self,
                                            PyObject *args) {
  Py_buffer view;
  unsigned int x, y, width, height;
  if (!PyArg_ParseTuple(args, "y*IIII", &view, &x, &y, &width, &height))
    return NULL;

  if (!VkComp_Resource_IsTexture(self)) {
    PyBuffer_Release(&view);
    PyErr_SetString(PyExc_TypeError,
                    "upload_subresource() only supported for textures");
    return NULL;
  }

  if (width == 0 || height == 0) {
    PyBuffer_Release(&view);
    Py_RETURN_NONE;
  }

  if (x + width > self->image_extent.width ||
      y + height > self->image_extent.height) {
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_ValueError,
                 "Rectangle (%u,%u %ux%u) exceeds texture dimensions (%ux%u)",
                 x, y, width, height, self->image_extent.width,
                 self->image_extent.height);
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev) {
    PyBuffer_Release(&view);
    return NULL;
  }

  VkDeviceSize size = width * height * 4;
  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(dev, size, &staging_buf,
                                                    &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, size, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyBuffer_Release(&view);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }
  memcpy(mapped, view.buf, view.len);
  vkUnmapMemory(dev->device, staging_mem);
  PyBuffer_Release(&view);

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  /* Transition to TRANSFER_DST_OPTIMAL */
  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
      .dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT,
      .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
      .newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = self->image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = 0,
              .layerCount = 1,
          },
  };
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  VkBufferImageCopy copy_region = {
      .bufferOffset = 0,
      .imageSubresource =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .mipLevel = 0,
              .baseArrayLayer = 0,
              .layerCount = 1,
          },
      .imageOffset = {(int32_t)x, (int32_t)y, 0},
      .imageExtent = {width, height, 1},
  };
  vkCmdCopyBufferToImage(cmd, staging_buf, self->image,
                         VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &copy_region);

  /* Transition back to GENERAL */
  barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Upload submission failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   upload_subresources(rects) where each rect is (data, x, y, width, height)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_UploadSubresources(VkComp_Resource *self,
                                             PyObject *args) {
  PyObject *rects_list;
  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &rects_list))
    return NULL;

  if (!VkComp_Resource_IsTexture(self)) {
    PyErr_SetString(PyExc_TypeError,
                    "upload_subresources() only supported for textures");
    return NULL;
  }

  Py_ssize_t num_rects = PyList_Size(rects_list);
  if (num_rects == 0)
    Py_RETURN_NONE;

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  /* First pass: validate and compute total size */
  typedef struct {
    uint32_t x, y, w, h;
    Py_buffer view;
    VkDeviceSize offset;
  } RectUpload;
  RectUpload *rects = PyMem_Malloc(num_rects * sizeof(RectUpload));
  if (!rects)
    return PyErr_NoMemory();

  VkDeviceSize total_size = 0;
  for (Py_ssize_t i = 0; i < num_rects; i++) {
    PyObject *tuple = PyList_GetItem(rects_list, i);
    if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
      PyMem_Free(rects);
      PyErr_SetString(
          PyExc_TypeError,
          "Each item must be a 5-tuple (data, x, y, width, height)");
      return NULL;
    }
    RectUpload *r = &rects[i];
    if (!PyArg_ParseTuple(tuple, "y*IIII", &r->view, &r->x, &r->y, &r->w,
                          &r->h)) {
      PyMem_Free(rects);
      return NULL;
    }
    if (r->w == 0 || r->h == 0) {
      PyBuffer_Release(&r->view);
      continue;
    }
    if (r->x + r->w > self->image_extent.width ||
        r->y + r->h > self->image_extent.height) {
      for (Py_ssize_t j = 0; j <= i; j++)
        PyBuffer_Release(&rects[j].view);
      PyMem_Free(rects);
      PyErr_Format(PyExc_ValueError,
                   "Rectangle (%u,%u %ux%u) exceeds texture dimensions (%ux%u)",
                   r->x, r->y, r->w, r->h, self->image_extent.width,
                   self->image_extent.height);
      return NULL;
    }
    VkDeviceSize data_size = r->w * r->h * 4;
    r->offset = total_size;
    total_size += data_size;
  }

  if (total_size == 0) {
    PyMem_Free(rects);
    Py_RETURN_NONE;
  }

  VkBuffer staging_buf;
  VkDeviceMemory staging_mem;
  VkBool32 from_pool;
  VkResult res = VkComp_Device_AcquireStagingBuffer(
      dev, total_size, &staging_buf, &staging_mem, &from_pool);
  if (res != VK_SUCCESS) {
    for (Py_ssize_t i = 0; i < num_rects; i++)
      PyBuffer_Release(&rects[i].view);
    PyMem_Free(rects);
    PyErr_Format(PyExc_RuntimeError, "Failed to acquire staging buffer: %d",
                 res);
    return NULL;
  }

  void *mapped;
  res = vkMapMemory(dev->device, staging_mem, 0, total_size, 0, &mapped);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    for (Py_ssize_t i = 0; i < num_rects; i++)
      PyBuffer_Release(&rects[i].view);
    PyMem_Free(rects);
    PyErr_Format(PyExc_RuntimeError, "Failed to map staging buffer: %d", res);
    return NULL;
  }
  uint8_t *dst = (uint8_t *)mapped;
  for (Py_ssize_t i = 0; i < num_rects; i++) {
    RectUpload *r = &rects[i];
    if (r->w > 0 && r->h > 0) {
      memcpy(dst + r->offset, r->view.buf, r->view.len);
    }
    PyBuffer_Release(&r->view);
  }
  vkUnmapMemory(dev->device, staging_mem);

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem,
                                       from_pool);
    PyMem_Free(rects);
    PyErr_Format(PyExc_RuntimeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
      .dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT,
      .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
      .newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = self->image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = 0,
              .layerCount = 1,
          },
  };
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  for (Py_ssize_t i = 0; i < num_rects; i++) {
    RectUpload *r = &rects[i];
    if (r->w == 0 || r->h == 0)
      continue;
    VkBufferImageCopy copy_region = {
        .bufferOffset = r->offset,
        .imageSubresource =
            {
                .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                .mipLevel = 0,
                .baseArrayLayer = 0,
                .layerCount = 1,
            },
        .imageOffset = {(int32_t)r->x, (int32_t)r->y, 0},
        .imageExtent = {r->w, r->h, 1},
    };
    vkCmdCopyBufferToImage(cmd, staging_buf, self->image,
                           VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1,
                           &copy_region);
  }

  barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  VkComp_Device_ReleaseStagingBuffer(dev, staging_buf, staging_mem, from_pool);
  PyMem_Free(rects);

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Upload submission failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   bind_tile(x, y, z, heap, heap_offset, slice) – sparse binding
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_BindTile(VkComp_Resource *self, PyObject *args) {
  unsigned int x, y, z, slice = 0;
  PyObject *py_heap = Py_None;
  unsigned long long heap_offset = 0;

  if (!PyArg_ParseTuple(args, "III|OKI", &x, &y, &z, &py_heap, &heap_offset,
                        &slice))
    return NULL;

  if (x >= self->tiles_x || y >= self->tiles_y || z >= self->tiles_z) {
    PyErr_Format(PyExc_ValueError,
                 "Tile coordinates (%u,%u,%u) out of range (%u,%u,%u)", x, y, z,
                 self->tiles_x, self->tiles_y, self->tiles_z);
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  if (!dev->supports_sparse) {
    PyErr_SetString(PyExc_RuntimeError, "Sparse binding not supported");
    return NULL;
  }

  VkSparseMemoryBind *binds = NULL;
  uint32_t bind_count = 0;

  if (py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &VkComp_Heap_Type)) {
      PyErr_SetString(PyExc_TypeError, "Expected a Heap object or None");
      return NULL;
    }
    VkComp_Heap *heap = (VkComp_Heap *)py_heap;
    if (heap->device != dev) {
      PyErr_SetString(PyExc_ValueError, "Heap belongs to a different device");
      return NULL;
    }

    VkDeviceSize tile_size;
    if (VkComp_Resource_IsBuffer(self)) {
      tile_size = self->tile_width;
    } else {
      tile_size = self->tile_width * self->tile_height * 4; /* simplified */
    }
    VkDeviceSize offset =
        (x + y * self->tiles_x + z * self->tiles_x * self->tiles_y) * tile_size;

    binds = PyMem_Malloc(sizeof(VkSparseMemoryBind));
    if (!binds)
      return PyErr_NoMemory();
    binds[0] = (VkSparseMemoryBind){
        .resourceOffset = offset,
        .size = tile_size,
        .memory = heap->memory,
        .memoryOffset = heap_offset,
        .flags = 0,
    };
    bind_count = 1;
  }

  VkSparseBufferMemoryBindInfo buffer_bind = {0};
  VkSparseImageOpaqueMemoryBindInfo image_bind = {0};
  VkBindSparseInfo bind_info = {
      .sType = VK_STRUCTURE_TYPE_BIND_SPARSE_INFO,
  };

  if (VkComp_Resource_IsBuffer(self)) {
    buffer_bind.buffer = self->buffer;
    buffer_bind.bindCount = bind_count;
    buffer_bind.pBinds = binds;
    bind_info.bufferBindCount = 1;
    bind_info.pBufferBinds = &buffer_bind;
  } else {
    image_bind.image = self->image;
    image_bind.bindCount = bind_count;
    image_bind.pBinds = binds;
    bind_info.imageOpaqueBindCount = 1;
    bind_info.pImageOpaqueBinds = &image_bind;
  }

  VkResult res = vkQueueBindSparse(dev->queue, 1, &bind_info, VK_NULL_HANDLE);
  if (binds)
    PyMem_Free(binds);

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Sparse binding failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   Static helper implementations
   ------------------------------------------------------------------------- */
static VkResult copy_buffer_to_buffer(VkComp_Resource *src,
                                      VkComp_Resource *dst, uint64_t size,
                                      uint64_t src_offset,
                                      uint64_t dst_offset) {
  VkComp_Device *dev = VkComp_Device_GetActive(src->device);
  if (!dev)
    return VK_ERROR_DEVICE_LOST;

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS)
    return res;

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkBufferCopy region = {src_offset, dst_offset, size};
  vkCmdCopyBuffer(cmd, src->buffer, dst->buffer, 1, &region);

  vkEndCommandBuffer(cmd);
  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  return res;
}

static VkResult copy_buffer_to_texture(VkComp_Resource *src,
                                       VkComp_Resource *dst, uint64_t size,
                                       uint64_t src_offset,
                                       uint32_t dst_slice) {
  VkComp_Device *dev = VkComp_Device_GetActive(src->device);
  if (!dev)
    return VK_ERROR_DEVICE_LOST;

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS)
    return res;

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
      .dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT,
      .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
      .newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = dst->image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = dst_slice,
              .layerCount = 1,
          },
  };
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  VkBufferImageCopy region = {
      .bufferOffset = src_offset,
      .imageSubresource =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .mipLevel = 0,
              .baseArrayLayer = dst_slice,
              .layerCount = 1,
          },
      .imageExtent = dst->image_extent,
  };
  vkCmdCopyBufferToImage(cmd, src->buffer, dst->image,
                         VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

  barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);
  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  return res;
}

static VkResult copy_texture_to_buffer(VkComp_Resource *src,
                                       VkComp_Resource *dst, uint64_t size,
                                       uint64_t dst_offset,
                                       uint32_t src_slice) {
  VkComp_Device *dev = VkComp_Device_GetActive(src->device);
  if (!dev)
    return VK_ERROR_DEVICE_LOST;

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS)
    return res;

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
      .dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT,
      .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
      .newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = src->image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = src_slice,
              .layerCount = 1,
          },
  };
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  VkBufferImageCopy region = {
      .bufferOffset = dst_offset,
      .imageSubresource =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .mipLevel = 0,
              .baseArrayLayer = src_slice,
              .layerCount = 1,
          },
      .imageExtent = src->image_extent,
  };
  vkCmdCopyImageToBuffer(cmd, src->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                         dst->buffer, 1, &region);

  barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);

  vkEndCommandBuffer(cmd);
  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  return res;
}

static VkResult
copy_texture_to_texture(VkComp_Resource *src, VkComp_Resource *dst,
                        uint32_t src_x, uint32_t src_y, uint32_t src_z,
                        uint32_t dst_x, uint32_t dst_y, uint32_t dst_z,
                        uint32_t width, uint32_t height, uint32_t depth,
                        uint32_t src_slice, uint32_t dst_slice) {
  VkComp_Device *dev = VkComp_Device_GetActive(src->device);
  if (!dev)
    return VK_ERROR_DEVICE_LOST;

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS)
    return res;

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkImageMemoryBarrier barriers[2] = {
      {
          .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
          .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
          .dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT,
          .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
          .newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
          .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .image = src->image,
          .subresourceRange =
              {
                  .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                  .baseMipLevel = 0,
                  .levelCount = 1,
                  .baseArrayLayer = src_slice,
                  .layerCount = 1,
              },
      },
      {
          .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
          .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
          .dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT,
          .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
          .newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
          .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .image = dst->image,
          .subresourceRange =
              {
                  .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                  .baseMipLevel = 0,
                  .levelCount = 1,
                  .baseArrayLayer = dst_slice,
                  .layerCount = 1,
              },
      }};
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 2,
                       barriers);

  VkImageCopy region = {
      .srcSubresource =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .mipLevel = 0,
              .baseArrayLayer = src_slice,
              .layerCount = 1,
          },
      .srcOffset = {(int32_t)src_x, (int32_t)src_y, (int32_t)src_z},
      .dstSubresource =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .mipLevel = 0,
              .baseArrayLayer = dst_slice,
              .layerCount = 1,
          },
      .dstOffset = {(int32_t)dst_x, (int32_t)dst_y, (int32_t)dst_z},
      .extent = {width, height, depth},
  };
  vkCmdCopyImage(cmd, src->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                 dst->image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

  barriers[0].srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barriers[0].dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barriers[0].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barriers[0].newLayout = VK_IMAGE_LAYOUT_GENERAL;
  barriers[1].srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barriers[1].dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barriers[1].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barriers[1].newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 2, barriers);

  vkEndCommandBuffer(cmd);
  res = vkcomp_submit_and_wait(dev, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(dev, cmd);
  return res;
}