#ifndef VK_UTILS_H
#define VK_UTILS_H

#include "vk_common.h"

/* ----------------------------------------------------------------------------
   Finds a memory type index that supports the given property flags.
   ------------------------------------------------------------------------- */
uint32_t vk_find_memory_type_index(VkPhysicalDeviceMemoryProperties *props,
                                   VkMemoryPropertyFlags flags);

/* ----------------------------------------------------------------------------
   Executes a command buffer on the device's queue, optionally waiting on a fence.
   If fence != VK_NULL_HANDLE, the function blocks until completion (GIL released).
   Returns VK_SUCCESS or an error code.
   ------------------------------------------------------------------------- */
VkResult vk_execute_command_buffer(vk_Device *dev, VkCommandBuffer cmd,
                                   VkFence fence,
                                   uint32_t wait_semaphore_count,
                                   VkSemaphore *wait_semaphores,
                                   VkPipelineStageFlags *wait_stages,
                                   uint32_t signal_semaphore_count,
                                   VkSemaphore *signal_semaphores);

/* ----------------------------------------------------------------------------
   Inserts an image memory barrier. Convenience wrapper.
   ------------------------------------------------------------------------- */
void vk_image_barrier(VkCommandBuffer cmd, VkImage image,
                      VkImageLayout old_layout, VkImageLayout new_layout,
                      VkPipelineStageFlags src_stage, VkPipelineStageFlags dst_stage,
                      VkAccessFlags src_access, VkAccessFlags dst_access,
                      uint32_t base_mip, uint32_t mip_count,
                      uint32_t base_layer, uint32_t layer_count);

/* ----------------------------------------------------------------------------
   Acquires a staging buffer large enough for `size` bytes.
   Tries the device's pool first; if not possible, allocates a new one.
   On success, out_buffer, out_memory, and out_mapped are filled.
   *used_pool indicates whether the buffer came from the pool (so release knows).
   Returns true on success, false on failure (no Python exception set).
   ------------------------------------------------------------------------- */
bool vk_staging_buffer_acquire(vk_Device *dev, VkDeviceSize size,
                               VkBuffer *out_buffer, VkDeviceMemory *out_memory,
                               void **out_mapped, bool *used_pool);

/* ----------------------------------------------------------------------------
   Releases a staging buffer acquired with vk_staging_buffer_acquire.
   If used_pool is false, the buffer and memory are destroyed.
   ------------------------------------------------------------------------- */
void vk_staging_buffer_release(vk_Device *dev, VkBuffer buffer,
                               VkDeviceMemory memory, bool used_pool);

/* ----------------------------------------------------------------------------
   Extracts the entry point name from a SPIR-V binary (must be compute shader).
   Returns NULL if invalid.
   ------------------------------------------------------------------------- */
const char *vk_spirv_get_entry_point(const uint32_t *code, size_t size);

/* ----------------------------------------------------------------------------
   Patches a SPIR-V module to add the NonReadable decoration to the UAV with
   the given binding index. Returns a new malloc'd buffer, or NULL if no patch
   needed. The caller must free the returned buffer with PyMem_Free.
   ------------------------------------------------------------------------- */
uint32_t *vk_spirv_patch_nonreadable_uav(const uint32_t *code, size_t size,
                                         uint32_t binding);

/* ----------------------------------------------------------------------------
   Allocates a temporary command buffer from the device's command pool.
   ------------------------------------------------------------------------- */
VkCommandBuffer vk_allocate_temp_cmd(vk_Device *dev);

/* ----------------------------------------------------------------------------
   Frees a temporary command buffer back to the device's command pool.
   ------------------------------------------------------------------------- */
void vk_free_temp_cmd(vk_Device *dev, VkCommandBuffer cmd);

#endif /* VK_UTILS_H */