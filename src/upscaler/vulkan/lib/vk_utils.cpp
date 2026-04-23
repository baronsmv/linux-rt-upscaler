/**
 * @file vk_utils.cpp
 * @brief Utility functions for Vulkan operations.
 *
 * This file provides helpers for memory allocation, command buffer execution,
 * synchronisation, SPIR-V manipulation, and descriptor set management.
 */

#include "vk_utils.h"
#include <cstring>
#include <functional>
#include <unordered_map>
#include <vector>

// Forward declaration of error objects (defined in vk_module.cpp)
extern PyObject *vk_ComputeError;
extern PyObject *vk_HeapError;

/* ----------------------------------------------------------------------------
   Memory type index lookup
   ------------------------------------------------------------------------- */
uint32_t vk_find_memory_type_index(VkPhysicalDeviceMemoryProperties *props,
                                   VkMemoryPropertyFlags flags) {
  for (uint32_t i = 0; i < props->memoryTypeCount; i++) {
    if ((props->memoryTypes[i].propertyFlags & flags) == flags)
      return i;
  }
  return UINT32_MAX;
}

/* ----------------------------------------------------------------------------
   Low-level command buffer execution
   ------------------------------------------------------------------------- */
VkResult vk_execute_command_buffer(vk_Device *dev, VkCommandBuffer cmd,
                                   VkFence fence, uint32_t wait_semaphore_count,
                                   VkSemaphore *wait_semaphores,
                                   VkPipelineStageFlags *wait_stages,
                                   uint32_t signal_semaphore_count,
                                   VkSemaphore *signal_semaphores) {
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;
  submit.waitSemaphoreCount = wait_semaphore_count;
  submit.pWaitSemaphores = wait_semaphores;
  submit.pWaitDstStageMask = wait_stages;
  submit.signalSemaphoreCount = signal_semaphore_count;
  submit.pSignalSemaphores = signal_semaphores;

  return vkQueueSubmit(dev->queue, 1, &submit, fence);
}

/* ----------------------------------------------------------------------------
   Image memory barrier (generic)
   ------------------------------------------------------------------------- */
void vk_image_barrier(VkCommandBuffer cmd, VkImage image,
                      VkImageLayout old_layout, VkImageLayout new_layout,
                      VkPipelineStageFlags src_stage,
                      VkPipelineStageFlags dst_stage, VkAccessFlags src_access,
                      VkAccessFlags dst_access, uint32_t base_mip,
                      uint32_t mip_count, uint32_t base_layer,
                      uint32_t layer_count) {
  VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  barrier.srcAccessMask = src_access;
  barrier.dstAccessMask = dst_access;
  barrier.oldLayout = old_layout;
  barrier.newLayout = new_layout;
  barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
  barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
  barrier.image = image;
  barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barrier.subresourceRange.baseMipLevel = base_mip;
  barrier.subresourceRange.levelCount = mip_count;
  barrier.subresourceRange.baseArrayLayer = base_layer;
  barrier.subresourceRange.layerCount = layer_count;

  vkCmdPipelineBarrier(cmd, src_stage, dst_stage, 0, 0, nullptr, 0, nullptr, 1,
                       &barrier);
}

/* ----------------------------------------------------------------------------
   Staging buffer pool management
   ------------------------------------------------------------------------- */
bool vk_staging_buffer_acquire(vk_Device *dev, VkDeviceSize size,
                               VkBuffer *out_buffer, VkDeviceMemory *out_memory,
                               void **out_mapped, bool *used_pool) {
  // Try to use a pooled buffer if size fits
  if (dev->staging_pool.count > 0) {
    int idx = dev->staging_pool.next;
    for (int i = 0; i < dev->staging_pool.count; i++) {
      int cur = (idx + i) % dev->staging_pool.count;
      if (dev->staging_pool.sizes[cur] >= size) {
        *out_buffer = dev->staging_pool.buffers[cur];
        *out_memory = dev->staging_pool.memories[cur];
        *used_pool = true;
        dev->staging_pool.next = (cur + 1) % dev->staging_pool.count;

        VkResult res =
            vkMapMemory(dev->device, *out_memory, 0, size, 0, out_mapped);
        if (res != VK_SUCCESS) {
          PyErr_Format(PyExc_RuntimeError,
                       "Failed to map staging buffer memory (error %d)", res);
          return false;
        }
        return true;
      }
    }
  }

  // Allocate temporary buffer
  VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
  binfo.size = size;
  binfo.usage =
      VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;

  VkBuffer buffer;
  if (vkCreateBuffer(dev->device, &binfo, nullptr, &buffer) != VK_SUCCESS) {
    PyErr_SetString(PyExc_RuntimeError,
                    "Failed to create temporary staging buffer");
    return false;
  }

  VkMemoryRequirements req;
  vkGetBufferMemoryRequirements(dev->device, buffer, &req);

  VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
  alloc.allocationSize = req.size;
  alloc.memoryTypeIndex = vk_find_memory_type_index(
      &dev->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                           VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);

  VkDeviceMemory memory;
  if (vkAllocateMemory(dev->device, &alloc, nullptr, &memory) != VK_SUCCESS) {
    vkDestroyBuffer(dev->device, buffer, nullptr);
    PyErr_SetString(PyExc_RuntimeError,
                    "Failed to allocate temporary staging memory");
    return false;
  }

  vkBindBufferMemory(dev->device, buffer, memory, 0);

  void *mapped;
  if (vkMapMemory(dev->device, memory, 0, size, 0, &mapped) != VK_SUCCESS) {
    vkFreeMemory(dev->device, memory, nullptr);
    vkDestroyBuffer(dev->device, buffer, nullptr);
    PyErr_SetString(PyExc_RuntimeError,
                    "Failed to map temporary staging buffer");
    return false;
  }

  *out_buffer = buffer;
  *out_memory = memory;
  *out_mapped = mapped;
  *used_pool = false;
  return true;
}

void vk_staging_buffer_release(vk_Device *dev, VkBuffer buffer,
                               VkDeviceMemory memory, bool used_pool) {
  if (used_pool) {
    vkUnmapMemory(dev->device, memory);
  } else {
    vkUnmapMemory(dev->device, memory);
    vkFreeMemory(dev->device, memory, nullptr);
    vkDestroyBuffer(dev->device, buffer, nullptr);
  }
}

/* ----------------------------------------------------------------------------
   SPIR-V helpers
   ------------------------------------------------------------------------- */
const char *vk_spirv_get_entry_point(const uint32_t *code, size_t size) {
  if (size < 20 || (size % 4) != 0)
    return NULL;
  if (code[0] != 0x07230203)
    return NULL; // SPIR-V magic

  size_t word_count = size / 4;
  size_t offset = 5; // Skip header (5 words)

  while (offset < word_count) {
    uint32_t word = code[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t length = word >> 16;
    if (length == 0)
      return NULL;

    // OpEntryPoint (0x0F) with ExecutionModel GLCompute (5)
    if (opcode == 0x0F && (offset + length < word_count) &&
        code[offset + 1] == 5) {
      if (length > 3) {
        const char *name = (const char *)&code[offset + 3];
        // Ensure null termination within the SPIR-V data
        size_t max_name_len = (length - 3) * 4;
        for (size_t i = 0; i < max_name_len; i++) {
          if (name[i] == 0)
            return name;
        }
      }
    }
    offset += length;
  }
  return NULL;
}

uint32_t *vk_spirv_patch_nonreadable_uav(const uint32_t *code, size_t size,
                                         uint32_t binding) {
  if (size < 20 || (size % 4) != 0)
    return NULL;
  if (code[0] != 0x07230203)
    return NULL;

  size_t word_count = size / 4;
  size_t offset = 5;
  bool found_binding = false;
  uint32_t target_id = 0;
  size_t inject_offset = 0;

  // Find OpDecorate Binding for the given binding number
  while (offset < word_count) {
    uint32_t word = code[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t length = word >> 16;
    if (length == 0)
      return NULL;

    // OpDecorate = 71, Decoration Binding = 33
    if (opcode == 71 && length >= 4 && code[offset + 2] == 33 &&
        code[offset + 3] == binding) {
      target_id = code[offset + 1];
      found_binding = true;
      inject_offset = offset + length; // position after this OpDecorate
      break;
    }
    offset += length;
  }
  if (!found_binding)
    return NULL;

  // Check if NonReadable (25) already exists for this id
  offset = 5;
  while (offset < word_count) {
    uint32_t word = code[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t length = word >> 16;
    if (opcode == 71 && length >= 3 && code[offset + 1] == target_id &&
        code[offset + 2] == 25) {
      return NULL; // Already has NonReadable
    }
    offset += length;
  }

  // Inject OpDecorate %id NonReadable (3 words)
  uint32_t *patched = (uint32_t *)PyMem_Malloc(size + 12);
  if (!patched)
    return NULL;

  memcpy(patched, code, inject_offset * 4);
  patched[inject_offset++] = (3 << 16) | 71; // OpDecorate, 3 words
  patched[inject_offset++] = target_id;
  patched[inject_offset++] = 25; // NonReadable
  memcpy(patched + inject_offset, code + (inject_offset - 3),
         size - ((inject_offset - 3) * 4));

  return patched;
}

/* ----------------------------------------------------------------------------
   Temporary command buffer allocation
   ------------------------------------------------------------------------- */
VkCommandBuffer vk_allocate_temp_cmd(vk_Device *dev) {
  std::lock_guard<std::mutex> lock(dev->cmd_pool_mutex);

  VkCommandBufferAllocateInfo alloc = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
  alloc.commandPool = dev->command_pool;
  alloc.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
  alloc.commandBufferCount = 1;

  VkCommandBuffer cmd;
  VkResult res = vkAllocateCommandBuffers(dev->device, &alloc, &cmd);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError,
                 "Failed to allocate temporary command buffer (error %d)", res);
    return VK_NULL_HANDLE;
  }
  return cmd;
}

void vk_free_temp_cmd(vk_Device *dev, VkCommandBuffer cmd) {
  std::lock_guard<std::mutex> lock(dev->cmd_pool_mutex);
  vkFreeCommandBuffers(dev->device, dev->command_pool, 1, &cmd);
}

/* ----------------------------------------------------------------------------
   One-time command buffer execution
   ------------------------------------------------------------------------- */
bool vk_execute_one_time_commands(
    vk_Device *dev, const std::function<void(VkCommandBuffer)> &record_func) {
  VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
  if (!cmd)
    return false;

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  begin.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
  vkBeginCommandBuffer(cmd, &begin);

  record_func(cmd);

  VkResult res = vkEndCommandBuffer(cmd);
  if (res != VK_SUCCESS) {
    vk_free_temp_cmd(dev, cmd);
    PyErr_Format(PyExc_RuntimeError, "Failed to end command buffer (error %d)",
                 res);
    return false;
  }

  VkFence fence = vk_create_fence(dev);
  if (!fence) {
    vk_free_temp_cmd(dev, cmd);
    return false;
  }

  res = vk_queue_submit_and_wait(dev, cmd, fence);
  vkDestroyFence(dev->device, fence, nullptr);
  vk_free_temp_cmd(dev, cmd);

  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Command execution failed (error %d)",
                 res);
    return false;
  }
  return true;
}

/* ----------------------------------------------------------------------------
   Fence creation
   ------------------------------------------------------------------------- */
VkFence vk_create_fence(vk_Device *dev, VkFenceCreateFlags flags) {
  VkFenceCreateInfo info = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
  info.flags = flags;
  VkFence fence;
  VkResult res = vkCreateFence(dev->device, &info, nullptr, &fence);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Failed to create fence (error %d)", res);
    return VK_NULL_HANDLE;
  }
  return fence;
}

/* ----------------------------------------------------------------------------
   Queue submit and wait (with GIL release)
   ------------------------------------------------------------------------- */
VkResult vk_queue_submit_and_wait(vk_Device *dev, VkCommandBuffer cmd,
                                  VkFence fence) {
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  VkResult res = vkQueueSubmit(dev->queue, 1, &submit, fence);
  if (res != VK_SUCCESS)
    return res;

  Py_BEGIN_ALLOW_THREADS res =
      vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
  Py_END_ALLOW_THREADS

      return res;
}

/* ----------------------------------------------------------------------------
   Memory mapping with error handling
   ------------------------------------------------------------------------- */
void *vk_map_memory(vk_Device *dev, VkDeviceMemory memory, VkDeviceSize offset,
                    VkDeviceSize size) {
  void *mapped = nullptr;
  VkResult res = vkMapMemory(dev->device, memory, offset, size, 0, &mapped);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Failed to map memory (error %d)", res);
    return nullptr;
  }
  return mapped;
}

/* ----------------------------------------------------------------------------
   ScopedStagingBuffer RAII implementation
   ------------------------------------------------------------------------- */
ScopedStagingBuffer::ScopedStagingBuffer(vk_Device *dev, VkDeviceSize size)
    : m_dev(dev) {
  m_valid = vk_staging_buffer_acquire(dev, size, &m_buffer, &m_memory,
                                      &m_mapped, &m_used_pool);
}

ScopedStagingBuffer::~ScopedStagingBuffer() {
  if (m_valid) {
    vkUnmapMemory(m_dev->device, m_memory);
    vk_staging_buffer_release(m_dev, m_buffer, m_memory, m_used_pool);
  }
}

/* ----------------------------------------------------------------------------
   Convenience image transitions
   ------------------------------------------------------------------------- */
void vk_cmd_transition_for_copy_dst(VkCommandBuffer cmd, VkImage image,
                                    uint32_t base_layer, uint32_t layer_count) {
  vk_image_barrier(cmd, image, VK_IMAGE_LAYOUT_GENERAL,
                   VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                   VK_PIPELINE_STAGE_TRANSFER_BIT, VK_ACCESS_SHADER_WRITE_BIT,
                   VK_ACCESS_TRANSFER_WRITE_BIT, 0, 1, base_layer, layer_count);
}

void vk_cmd_transition_for_copy_src(VkCommandBuffer cmd, VkImage image,
                                    uint32_t base_layer, uint32_t layer_count) {
  vk_image_barrier(cmd, image, VK_IMAGE_LAYOUT_GENERAL,
                   VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                   VK_PIPELINE_STAGE_TRANSFER_BIT, VK_ACCESS_SHADER_WRITE_BIT,
                   VK_ACCESS_TRANSFER_READ_BIT, 0, 1, base_layer, layer_count);
}

void vk_cmd_transition_for_compute(VkCommandBuffer cmd, VkImage image,
                                   uint32_t base_layer, uint32_t layer_count) {
  vk_image_barrier(cmd, image, VK_IMAGE_LAYOUT_UNDEFINED,
                   VK_IMAGE_LAYOUT_GENERAL, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                   VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0,
                   VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT, 0, 1,
                   base_layer, layer_count);
}

void vk_cmd_transition_for_present(VkCommandBuffer cmd, VkImage image) {
  vk_image_barrier(cmd, image, VK_IMAGE_LAYOUT_GENERAL,
                   VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
                   VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                   VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                   VK_ACCESS_SHADER_WRITE_BIT, 0, 0, 1, 0, 1);
}

/* ----------------------------------------------------------------------------
   Descriptor set helpers for compute pipelines
   ------------------------------------------------------------------------- */
bool vk_create_compute_descriptor_set_layout(
    vk_Device *dev, const std::vector<vk_Resource *> &cbv,
    const std::vector<vk_Resource *> &srv,
    const std::vector<vk_Resource *> &uav,
    const std::vector<vk_Sampler *> &samplers, uint32_t bindless,
    VkDescriptorSetLayout *out_layout) {
  std::vector<VkDescriptorSetLayoutBinding> bindings;
  std::vector<VkDescriptorBindingFlags> binding_flags;
  bool use_update_after_bind = (bindless > 0) && dev->supports_bindless;

  auto add_binding = [&](uint32_t binding, VkDescriptorType type,
                         uint32_t count) {
    VkDescriptorSetLayoutBinding lb = {};
    lb.binding = binding;
    lb.descriptorType = type;
    lb.descriptorCount = count;
    lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
    bindings.push_back(lb);
    if (use_update_after_bind) {
      binding_flags.push_back(VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT |
                              VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT);
    }
  };

  if (bindless == 0) {
    // Non-bindless: each resource gets its own binding
    uint32_t idx = 0;
    for (size_t i = 0; i < cbv.size(); ++i)
      add_binding(idx++, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1);
    idx = 1024;
    for (size_t i = 0; i < srv.size(); ++i) {
      vk_Resource *res = srv[i];
      VkDescriptorType type;
      if (res->buffer) {
        type = res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                                : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
      } else {
        type = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
      }
      add_binding(idx++, type, 1);
    }
    idx = 2048;
    for (size_t i = 0; i < uav.size(); ++i) {
      vk_Resource *res = uav[i];
      VkDescriptorType type;
      if (res->buffer) {
        type = res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                                : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
      } else {
        type = VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
      }
      add_binding(idx++, type, 1);
    }
    idx = 3072;
    for (size_t i = 0; i < samplers.size(); ++i) {
      add_binding(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, 1);
    }
  } else {
    // Bindless: three large arrays (CBV, SRV, UAV)
    if (dev->supports_bindless) {
      add_binding(0, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, bindless);
      add_binding(1024, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, bindless);
      add_binding(2048, VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, bindless);
      uint32_t idx = 3072;
      for (size_t i = 0; i < samplers.size(); ++i)
        add_binding(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, 1);
    } else {
      PyErr_SetString(vk_ComputeError, "Bindless not supported on this device");
      return false;
    }
  }

  VkDescriptorSetLayoutCreateInfo dsl_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
  dsl_info.bindingCount = static_cast<uint32_t>(bindings.size());
  dsl_info.pBindings = bindings.data();

  VkDescriptorSetLayoutBindingFlagsCreateInfo flags_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_BINDING_FLAGS_CREATE_INFO};
  if (use_update_after_bind) {
    flags_info.bindingCount = static_cast<uint32_t>(binding_flags.size());
    flags_info.pBindingFlags = binding_flags.data();
    dsl_info.pNext = &flags_info;
    dsl_info.flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT;
  }

  VkResult res =
      vkCreateDescriptorSetLayout(dev->device, &dsl_info, nullptr, out_layout);
  VK_CHECK_OR_RETURN_FALSE(res, vk_ComputeError,
                           "Failed to create descriptor set layout");
  return true;
}

bool vk_allocate_and_write_descriptor_set(
    vk_Device *dev, const std::vector<vk_Resource *> &cbv,
    const std::vector<vk_Resource *> &srv,
    const std::vector<vk_Resource *> &uav,
    const std::vector<vk_Sampler *> &samplers, uint32_t bindless,
    VkDescriptorSetLayout layout, VkDescriptorPool *out_pool,
    VkDescriptorSet *out_set) {
  // Count descriptor types needed
  std::unordered_map<VkDescriptorType, uint32_t> type_counts;
  auto count_type = [&](VkDescriptorType type, uint32_t count = 1) {
    type_counts[type] += count;
  };

  if (bindless == 0) {
    for (size_t i = 0; i < cbv.size(); ++i)
      count_type(VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER);
    for (vk_Resource *res : srv) {
      VkDescriptorType type =
          res->buffer
              ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                                  : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER)
              : VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
      count_type(type);
    }
    for (vk_Resource *res : uav) {
      VkDescriptorType type =
          res->buffer
              ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                                  : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER)
              : VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
      count_type(type);
    }
    for (size_t i = 0; i < samplers.size(); ++i)
      count_type(VK_DESCRIPTOR_TYPE_SAMPLER);
  } else {
    if (dev->supports_bindless) {
      count_type(VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, bindless);
      count_type(VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, bindless);
      count_type(VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, bindless);
      for (size_t i = 0; i < samplers.size(); ++i)
        count_type(VK_DESCRIPTOR_TYPE_SAMPLER);
    }
  }

  std::vector<VkDescriptorPoolSize> pool_sizes;
  for (const auto &kv : type_counts) {
    pool_sizes.push_back({kv.first, kv.second});
  }

  VkDescriptorPoolCreateInfo dp_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
  dp_info.maxSets = 1;
  dp_info.poolSizeCount = static_cast<uint32_t>(pool_sizes.size());
  dp_info.pPoolSizes = pool_sizes.data();
  if (bindless > 0 && dev->supports_bindless)
    dp_info.flags = VK_DESCRIPTOR_POOL_CREATE_UPDATE_AFTER_BIND_BIT;

  VkResult res =
      vkCreateDescriptorPool(dev->device, &dp_info, nullptr, out_pool);
  VK_CHECK_OR_RETURN_FALSE(res, vk_ComputeError,
                           "Failed to create descriptor pool");

  VkDescriptorSetAllocateInfo alloc_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
  alloc_info.descriptorPool = *out_pool;
  alloc_info.descriptorSetCount = 1;
  alloc_info.pSetLayouts = &layout;
  res = vkAllocateDescriptorSets(dev->device, &alloc_info, out_set);
  VK_CHECK_OR_RETURN_FALSE(res, vk_ComputeError,
                           "Failed to allocate descriptor set");

  // Write descriptors
  std::vector<VkWriteDescriptorSet> writes;
  std::vector<VkDescriptorBufferInfo> buffer_infos;
  std::vector<VkDescriptorImageInfo> image_infos;
  std::vector<VkBufferView> buffer_views;

  auto add_write = [&](uint32_t binding, VkDescriptorType type,
                       VkDescriptorBufferInfo *buf_info = nullptr,
                       VkDescriptorImageInfo *img_info = nullptr,
                       VkBufferView *buf_view = nullptr) {
    VkWriteDescriptorSet w = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
    w.dstSet = *out_set;
    w.dstBinding = binding;
    w.descriptorCount = 1;
    w.descriptorType = type;
    if (buf_info)
      w.pBufferInfo = buf_info;
    if (img_info)
      w.pImageInfo = img_info;
    if (buf_view)
      w.pTexelBufferView = buf_view;
    writes.push_back(w);
  };

  if (bindless == 0) {
    uint32_t idx = 0;
    for (vk_Resource *res : cbv)
      add_write(idx++, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
                &res->descriptor_buffer_info);
    idx = 1024;
    for (vk_Resource *res : srv) {
      if (res->buffer) {
        if (res->buffer_view) {
          add_write(idx, VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER, nullptr,
                    nullptr, &res->buffer_view);
        } else {
          add_write(idx, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
                    &res->descriptor_buffer_info);
        }
      } else {
        add_write(idx, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, nullptr,
                  &res->descriptor_image_info);
      }
      ++idx;
    }
    idx = 2048;
    for (vk_Resource *res : uav) {
      if (res->buffer) {
        if (res->buffer_view) {
          add_write(idx, VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER, nullptr,
                    nullptr, &res->buffer_view);
        } else {
          add_write(idx, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                    &res->descriptor_buffer_info);
        }
      } else {
        add_write(idx, VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, nullptr,
                  &res->descriptor_image_info);
      }
      ++idx;
    }
    idx = 3072;
    for (vk_Sampler *samp : samplers) {
      add_write(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, nullptr,
                &samp->descriptor_image_info);
    }
  } else {
    // Bindless: write individual array elements
    for (size_t i = 0; i < cbv.size(); ++i) {
      add_write(static_cast<uint32_t>(i), VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
                &cbv[i]->descriptor_buffer_info);
    }
    for (size_t i = 0; i < srv.size(); ++i) {
      vk_Resource *res = srv[i];
      if (res->image) {
        add_write(1024 + static_cast<uint32_t>(i),
                  VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, nullptr,
                  &res->descriptor_image_info);
      }
    }
    for (size_t i = 0; i < uav.size(); ++i) {
      vk_Resource *res = uav[i];
      if (res->image) {
        add_write(2048 + static_cast<uint32_t>(i),
                  VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, nullptr,
                  &res->descriptor_image_info);
      }
    }
    uint32_t idx = 3072;
    for (vk_Sampler *samp : samplers) {
      add_write(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, nullptr,
                &samp->descriptor_image_info);
    }
  }

  vkUpdateDescriptorSets(dev->device, static_cast<uint32_t>(writes.size()),
                         writes.data(), 0, nullptr);
  return true;
}