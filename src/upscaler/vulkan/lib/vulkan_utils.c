/**
 * @file vulkan_utils.c
 * @brief Implementation of utility functions for the Vulkan backend.
 */

#include "vulkan_utils.h"
#include "vulkan_device.h"
#include "vulkan_types.h"
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------------------------------
   Size calculation
   ------------------------------------------------------------------------- */
size_t vkcomp_get_size_by_pitch(size_t pitch, size_t width, size_t height,
                                size_t depth, size_t bytes_per_pixel) {
  size_t rows = height * depth;
  if (rows > 1) {
    return (pitch * (rows - 1)) + (bytes_per_pixel * width);
  }
  return pitch;
}

/* -------------------------------------------------------------------------
   Copy validation
   ------------------------------------------------------------------------- */
bool vkcomp_check_copy_to(
    bool src_is_buffer, bool dst_is_buffer, uint64_t size, uint64_t src_offset,
    uint64_t dst_offset, uint64_t src_size, uint64_t dst_size, uint32_t src_x,
    uint32_t src_y, uint32_t src_z, uint32_t src_slice, uint32_t src_slices,
    uint32_t dst_slice, uint32_t dst_slices, uint32_t src_width,
    uint32_t src_height, uint32_t src_depth, uint32_t dst_width,
    uint32_t dst_height, uint32_t dst_depth, uint32_t *dst_x, uint32_t *dst_y,
    uint32_t *dst_z, uint32_t *width, uint32_t *height, uint32_t *depth) {
  /* Buffer to buffer */
  if (src_is_buffer && dst_is_buffer) {
    if (src_offset + size > src_size || dst_offset + size > dst_size) {
      PyErr_Format(
          PyExc_ValueError,
          "Copy out of bounds: size=%llu, src_offset=%llu, src_size=%llu, "
          "dst_offset=%llu, dst_size=%llu",
          size, src_offset, src_size, dst_offset, dst_size);
      return false;
    }
  }
  /* Buffer to texture */
  else if (src_is_buffer && !dst_is_buffer) {
    *dst_x = 0;
    *dst_y = 0;
    *dst_z = 0;
    if (src_offset + size > src_size || size < dst_size ||
        dst_slice >= dst_slices) {
      PyErr_Format(PyExc_ValueError,
                   "Buffer->texture copy out of bounds: size=%llu, "
                   "src_offset=%llu, src_size=%llu, "
                   "dst_size=%llu, dst_slice=%u, dst_slices=%u",
                   size, src_offset, src_size, dst_size, dst_slice, dst_slices);
      return false;
    }
  }
  /* Texture to buffer */
  else if (!src_is_buffer && dst_is_buffer) {
    *dst_x = 0;
    *dst_y = 0;
    *dst_z = 0;
    if (dst_offset + size > dst_size || size < src_size ||
        src_slice >= src_slices) {
      PyErr_Format(PyExc_ValueError,
                   "Texture->buffer copy out of bounds: size=%llu, "
                   "dst_offset=%llu, dst_size=%llu, "
                   "src_size=%llu, src_slice=%u, src_slices=%u",
                   size, dst_offset, dst_size, src_size, src_slice, src_slices);
      return false;
    }
  }
  /* Texture to texture */
  else {
    if (*width == 0)
      *width = src_width;
    if (*height == 0)
      *height = src_height;
    if (*depth == 0)
      *depth = src_depth;

    if (src_x + *width > src_width || src_y + *height > src_height ||
        src_z + *depth > src_depth || *dst_x + *width > dst_width ||
        *dst_y + *height > dst_height || *dst_z + *depth > dst_depth ||
        src_slice >= src_slices || dst_slice >= dst_slices) {
      PyErr_Format(PyExc_ValueError,
                   "Texture->texture copy out of bounds: "
                   "copy=(%u,%u,%u %ux%ux%u), src=(%ux%ux%u slices=%u), "
                   "dst=(%ux%ux%u slices=%u)",
                   *dst_x, *dst_y, *dst_z, *width, *height, *depth, src_width,
                   src_height, src_depth, src_slices, dst_width, dst_height,
                   dst_depth, dst_slices);
      return false;
    }
  }
  return true;
}

/* -------------------------------------------------------------------------
   Descriptor validation (C version – no templates)
   ------------------------------------------------------------------------- */
bool vkcomp_check_descriptors(PyTypeObject *py_resource_type, PyObject *py_cbv,
                              VkComp_Resource ***cbv_out, size_t *cbv_count,
                              PyObject *py_srv, VkComp_Resource ***srv_out,
                              size_t *srv_count, PyObject *py_uav,
                              VkComp_Resource ***uav_out, size_t *uav_count,
                              PyTypeObject *py_sampler_type,
                              PyObject *py_samplers,
                              VkComp_Sampler ***samplers_out,
                              size_t *samplers_count) {
/* Helper macro to process an iterable */
#define PROCESS_LIST(list_obj, out_array, out_count, type_check, elem_type)    \
  do {                                                                         \
    if (list_obj) {                                                            \
      PyObject *iter = PyObject_GetIter(list_obj);                             \
      if (!iter)                                                               \
        return false;                                                          \
      size_t cap = 0;                                                          \
      out_array = NULL;                                                        \
      out_count = 0;                                                           \
      PyObject *item;                                                          \
      while ((item = PyIter_Next(iter)) != NULL) {                             \
        int is_inst = PyObject_IsInstance(item, (PyObject *)type_check);       \
        if (is_inst < 0) {                                                     \
          Py_DECREF(item);                                                     \
          Py_DECREF(iter);                                                     \
          goto error;                                                          \
        } else if (is_inst == 0) {                                             \
          Py_DECREF(item);                                                     \
          Py_DECREF(iter);                                                     \
          PyErr_SetString(PyExc_TypeError,                                     \
                          "Expected a " #elem_type " object");                 \
          goto error;                                                          \
        }                                                                      \
        if (out_count >= cap) {                                                \
          cap = cap ? cap * 2 : 4;                                             \
          void *new_arr = PyMem_Realloc(out_array, cap * sizeof(elem_type *)); \
          if (!new_arr) {                                                      \
            Py_DECREF(item);                                                   \
            Py_DECREF(iter);                                                   \
            PyErr_NoMemory();                                                  \
            goto error;                                                        \
          }                                                                    \
          out_array = new_arr;                                                 \
        }                                                                      \
        out_array[out_count++] = (elem_type *)item;                            \
        Py_DECREF(item);                                                       \
      }                                                                        \
      Py_DECREF(iter);                                                         \
      if (PyErr_Occurred())                                                    \
        goto error;                                                            \
    } else {                                                                   \
      out_array = NULL;                                                        \
      out_count = 0;                                                           \
    }                                                                          \
  } while (0)

  PROCESS_LIST(py_cbv, *cbv_out, *cbv_count, py_resource_type, VkComp_Resource);
  PROCESS_LIST(py_srv, *srv_out, *srv_count, py_resource_type, VkComp_Resource);
  PROCESS_LIST(py_uav, *uav_out, *uav_count, py_resource_type, VkComp_Resource);
  PROCESS_LIST(py_samplers, *samplers_out, *samplers_count, py_sampler_type,
               VkComp_Sampler);

#undef PROCESS_LIST
  return true;

error:
  /* Cleanup on error */
  if (*cbv_out) {
    for (size_t i = 0; i < *cbv_count; ++i)
      Py_DECREF((*cbv_out)[i]);
    PyMem_Free(*cbv_out);
    *cbv_out = NULL;
    *cbv_count = 0;
  }
  if (*srv_out) {
    for (size_t i = 0; i < *srv_count; ++i)
      Py_DECREF((*srv_out)[i]);
    PyMem_Free(*srv_out);
    *srv_out = NULL;
    *srv_count = 0;
  }
  if (*uav_out) {
    for (size_t i = 0; i < *uav_count; ++i)
      Py_DECREF((*uav_out)[i]);
    PyMem_Free(*uav_out);
    *uav_out = NULL;
    *uav_count = 0;
  }
  if (*samplers_out) {
    for (size_t i = 0; i < *samplers_count; ++i)
      Py_DECREF((*samplers_out)[i]);
    PyMem_Free(*samplers_out);
    *samplers_out = NULL;
    *samplers_count = 0;
  }
  return false;
}

/* -------------------------------------------------------------------------
   Vulkan memory type finder
   ------------------------------------------------------------------------- */
uint32_t vkcomp_find_memory_type(const VkPhysicalDeviceMemoryProperties *props,
                                 uint32_t type_filter,
                                 VkMemoryPropertyFlags properties) {
  for (uint32_t i = 0; i < props->memoryTypeCount; i++) {
    if ((type_filter & (1 << i)) &&
        (props->memoryTypes[i].propertyFlags & properties) == properties) {
      return i;
    }
  }
  return UINT32_MAX;
}

/* -------------------------------------------------------------------------
   Image layout transition
   ------------------------------------------------------------------------- */
bool vkcomp_texture_set_layout(VkComp_Device *device, VkImage image,
                               VkImageLayout old_layout,
                               VkImageLayout new_layout, uint32_t slices) {
  VkCommandBuffer cmd;
  if (VkComp_Device_AllocateCmd(device, &cmd) != VK_SUCCESS) {
    return false;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  VkImageMemoryBarrier barrier = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
      .oldLayout = old_layout,
      .newLayout = new_layout,
      .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
      .image = image,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = 0,
              .layerCount = slices,
          },
  };

  /* Determine access masks */
  switch (old_layout) {
  case VK_IMAGE_LAYOUT_UNDEFINED:
    barrier.srcAccessMask = 0;
    break;
  case VK_IMAGE_LAYOUT_GENERAL:
    barrier.srcAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
    break;
  case VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL:
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    break;
  case VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL:
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    break;
  case VK_IMAGE_LAYOUT_PRESENT_SRC_KHR:
    barrier.srcAccessMask = VK_ACCESS_MEMORY_READ_BIT;
    break;
  default:
    barrier.srcAccessMask = 0;
  }

  switch (new_layout) {
  case VK_IMAGE_LAYOUT_GENERAL:
    barrier.dstAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
    break;
  case VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL:
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    break;
  case VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL:
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    break;
  case VK_IMAGE_LAYOUT_PRESENT_SRC_KHR:
    barrier.dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;
    break;
  default:
    barrier.dstAccessMask = 0;
  }

  VkPipelineStageFlags src_stage = VK_PIPELINE_STAGE_ALL_COMMANDS_BIT;
  VkPipelineStageFlags dst_stage = VK_PIPELINE_STAGE_ALL_COMMANDS_BIT;

  if (old_layout == VK_IMAGE_LAYOUT_UNDEFINED) {
    src_stage = VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT;
  }
  if (new_layout == VK_IMAGE_LAYOUT_PRESENT_SRC_KHR) {
    dst_stage = VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT;
  }

  vkCmdPipelineBarrier(cmd, src_stage, dst_stage, 0, 0, NULL, 0, NULL, 1,
                       &barrier);

  vkEndCommandBuffer(cmd);

  VkResult res = vkcomp_submit_and_wait(device, cmd, VK_NULL_HANDLE);
  VkComp_Device_FreeCmd(device, cmd);
  return (res == VK_SUCCESS);
}

/* -------------------------------------------------------------------------
   Image creation
   ------------------------------------------------------------------------- */
VkImage vkcomp_create_image(VkDevice device, VkImageType image_type,
                            VkFormat format, uint32_t width, uint32_t height,
                            uint32_t depth, uint32_t slices, bool sparse) {
  VkImageCreateInfo image_info = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,
      .imageType = image_type,
      .format = format,
      .extent = {width, height, depth},
      .mipLevels = 1,
      .arrayLayers = slices,
      .samples = VK_SAMPLE_COUNT_1_BIT,
      .tiling = VK_IMAGE_TILING_OPTIMAL,
      .usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT |
               VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT |
               VK_IMAGE_USAGE_STORAGE_BIT,
      .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
      .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
  };

  if (sparse) {
    image_info.flags = VK_IMAGE_CREATE_SPARSE_BINDING_BIT |
                       VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT;
  }

  VkImage image;
  VkResult res = vkCreateImage(device, &image_info, NULL, &image);
  return (res == VK_SUCCESS) ? image : VK_NULL_HANDLE;
}

/* -------------------------------------------------------------------------
   SPIR‑V entry point
   ------------------------------------------------------------------------- */
const char *vkcomp_get_spirv_entry_point(const uint32_t *words, size_t len) {
  if (len < 20 || (len % 4) != 0)
    return NULL;
  if (words[0] != 0x07230203)
    return NULL; /* SPIR-V magic */

  size_t num_words = len / 4;
  size_t offset = 5; /* skip header (5 words) */

  while (offset < num_words) {
    uint32_t word = words[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t size = word >> 16;

    if (size == 0 || offset + size > num_words)
      return NULL;

    /* OpEntryPoint = 15, Execution Model = 5 (GLCompute) */
    if (opcode == 15 && size >= 4 && words[offset + 1] == 5) {
      /* The entry point name starts at words[offset + 3] */
      const char *name = (const char *)&words[offset + 3];
      /* Verify null-termination within the instruction's word range */
      size_t max_len = (size - 3) * 4;
      for (size_t i = 0; i < max_len; i++) {
        if (name[i] == '\0')
          return name;
      }
      return NULL; /* malformed: no null terminator */
    }

    offset += size;
  }
  return NULL; /* no compute entry point found */
}

/* -------------------------------------------------------------------------
   SPIR‑V patching
   ------------------------------------------------------------------------- */
uint32_t *vkcomp_patch_spirv_unknown_uav(const uint32_t *words, size_t len,
                                         uint32_t binding) {
  if (len < 20 || (len % 4) != 0)
    return NULL;
  if (words[0] != 0x07230203)
    return NULL;

  size_t num_words = len / 4;
  size_t offset = 5;
  bool found = false;
  uint32_t binding_id = 0;
  size_t injection_offset = 0;

  /* Find OpDecorate for the given binding */
  while (offset < num_words) {
    uint32_t word = words[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t size = word >> 16;
    if (size == 0)
      return NULL;

    /* OpDecorate = 71 */
    if (opcode == 71 && size >= 4) {
      if (words[offset + 2] == 33 /* Decoration Binding */ &&
          words[offset + 3] == binding) {
        binding_id = words[offset + 1];
        found = true;
        injection_offset = offset + size;
        break;
      }
    }
    offset += size;
  }
  if (!found)
    return NULL;

  /* Check if NonReadable decoration already exists */
  offset = 5;
  while (offset < num_words) {
    uint32_t word = words[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t size = word >> 16;
    if (size == 0)
      return NULL;

    if (opcode == 71 && size >= 3) {
      if (words[offset + 2] == 25 /* NonReadable */) {
        return NULL; /* already patched */
      }
    }
    offset += size;
  }

  /* Allocate new buffer and inject NonReadable decoration */
  size_t new_len = len + 12;
  uint32_t *patched = PyMem_Malloc(new_len);
  if (!patched)
    return NULL;

  memcpy(patched, words, injection_offset * 4);

  /* OpDecorate %binding_id NonReadable (3 words) */
  patched[injection_offset++] = (3 << 16) | 71; /* OpDecorate, 3 words */
  patched[injection_offset++] = binding_id;
  patched[injection_offset++] = 25; /* NonReadable */

  memcpy(patched + injection_offset, words + (injection_offset - 3),
         len - ((injection_offset - 3) * 4));

  return patched;
}

/* -------------------------------------------------------------------------
   Submit and wait using timeline semaphore
   ------------------------------------------------------------------------- */
VkResult vkcomp_submit_and_wait(VkComp_Device *device, VkCommandBuffer cmd,
                                VkFence fence) {
  uint64_t signal_value = ++device->timeline_value;

  VkTimelineSemaphoreSubmitInfo timeline_info = {
      .sType = VK_STRUCTURE_TYPE_TIMELINE_SEMAPHORE_SUBMIT_INFO,
      .signalSemaphoreValueCount = 1,
      .pSignalSemaphoreValues = &signal_value,
  };

  VkSubmitInfo submit_info = {
      .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
      .pNext = &timeline_info,
      .commandBufferCount = 1,
      .pCommandBuffers = &cmd,
      .signalSemaphoreCount = 1,
      .pSignalSemaphores = &device->timeline_semaphore,
  };

  VkResult res = vkQueueSubmit(device->queue, 1, &submit_info, fence);
  if (res != VK_SUCCESS)
    return res;

  VkSemaphoreWaitInfo wait_info = {
      .sType = VK_STRUCTURE_TYPE_SEMAPHORE_WAIT_INFO,
      .semaphoreCount = 1,
      .pSemaphores = &device->timeline_semaphore,
      .pValues = &signal_value,
  };

  Py_BEGIN_ALLOW_THREADS res =
      vkWaitSemaphores(device->device, &wait_info, UINT64_MAX);
  Py_END_ALLOW_THREADS

      if (fence != VK_NULL_HANDLE) {
    vkResetFences(device->device, 1, &fence);
  }
  return res;
}