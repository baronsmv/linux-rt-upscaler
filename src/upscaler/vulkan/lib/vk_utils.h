#ifndef VK_UTILS_H
#define VK_UTILS_H

#include "vk_common.h"
#include <functional>

// ---------------------------------------------------------------------------
// Convenience macros for Vulkan result checking
// ---------------------------------------------------------------------------

// Check a VkResult, set a Python exception on failure, and return `NULL`.
#define VK_CHECK_OR_RETURN_NULL(expr, errObj, fmt, ...)                        \
  do {                                                                         \
    VkResult _res = (expr);                                                    \
    if (_res != VK_SUCCESS) {                                                  \
      PyErr_Format(errObj, fmt " (VkResult %d)", ##__VA_ARGS__, _res);         \
      return nullptr;                                                          \
    }                                                                          \
  } while (0)

// Check a VkResult, set a Python exception on failure, and return `false`.
#define VK_CHECK_OR_RETURN_FALSE(expr, errObj, fmt, ...)                       \
  do {                                                                         \
    VkResult _res = (expr);                                                    \
    if (_res != VK_SUCCESS) {                                                  \
      PyErr_Format(errObj, fmt " (VkResult %d)", ##__VA_ARGS__, _res);         \
      return false;                                                            \
    }                                                                          \
  } while (0)

// ---------------------------------------------------------------------------
// Memory type and queue submission
// ---------------------------------------------------------------------------
uint32_t vk_find_memory_type_index(VkPhysicalDeviceMemoryProperties *props,
                                   VkMemoryPropertyFlags flags);

VkResult vk_execute_command_buffer(vk_Device *dev, VkCommandBuffer cmd,
                                   VkFence fence, uint32_t wait_semaphore_count,
                                   VkSemaphore *wait_semaphores,
                                   VkPipelineStageFlags *wait_stages,
                                   uint32_t signal_semaphore_count,
                                   VkSemaphore *signal_semaphores);

void vk_image_barrier(VkCommandBuffer cmd, VkImage image,
                      VkImageLayout old_layout, VkImageLayout new_layout,
                      VkPipelineStageFlags src_stage,
                      VkPipelineStageFlags dst_stage, VkAccessFlags src_access,
                      VkAccessFlags dst_access, uint32_t base_mip,
                      uint32_t mip_count, uint32_t base_layer,
                      uint32_t layer_count);

// ---------------------------------------------------------------------------
// Staging buffer pool
// ---------------------------------------------------------------------------
bool vk_staging_buffer_acquire(vk_Device *dev, VkDeviceSize size,
                               VkBuffer *out_buffer, VkDeviceMemory *out_memory,
                               void **out_mapped, bool *used_pool);
void vk_staging_buffer_release(vk_Device *dev, VkBuffer buffer,
                               VkDeviceMemory memory, bool used_pool);

// ---------------------------------------------------------------------------
// SPIR-V helpers
// ---------------------------------------------------------------------------
const char *vk_spirv_get_entry_point(const uint32_t *code, size_t size);
uint32_t *vk_spirv_patch_nonreadable_uav(const uint32_t *code, size_t size,
                                         uint32_t binding);

// ---------------------------------------------------------------------------
// Temporary command buffer management
// ---------------------------------------------------------------------------
VkCommandBuffer vk_allocate_temp_cmd(vk_Device *dev);
void vk_free_temp_cmd(vk_Device *dev, VkCommandBuffer cmd);

// Allocate, record, submit, and wait for a one-shot command buffer.
bool vk_execute_one_time_commands(
    vk_Device *dev, const std::function<void(VkCommandBuffer)> &record_func);

// ---------------------------------------------------------------------------
// Fence and queue submission
// ---------------------------------------------------------------------------
VkFence vk_create_fence(vk_Device *dev, VkFenceCreateFlags flags = 0);

// Submit a command buffer and wait for the fence (GIL released during wait).
VkResult vk_queue_submit_and_wait(vk_Device *dev, VkCommandBuffer cmd,
                                  VkFence fence);

// ---------------------------------------------------------------------------
// Memory mapping
// ---------------------------------------------------------------------------
void *vk_map_memory(vk_Device *dev, VkDeviceMemory memory, VkDeviceSize offset,
                    VkDeviceSize size);

// ---------------------------------------------------------------------------
// RAII wrappers
// ---------------------------------------------------------------------------

// Automatically release a Python buffer object.
struct PyBufferGuard {
  Py_buffer view;
  bool owned = false;

  PyBufferGuard() = default;
  ~PyBufferGuard() {
    if (owned)
      PyBuffer_Release(&view);
  }

  PyBufferGuard(const PyBufferGuard &) = delete;
  PyBufferGuard &operator=(const PyBufferGuard &) = delete;
  PyBufferGuard(PyBufferGuard &&other) noexcept;
  PyBufferGuard &operator=(PyBufferGuard &&other) noexcept;

  bool acquire(PyObject *obj, int flags = PyBUF_SIMPLE);
  void release();
};

// Acquire a staging buffer on construction, release on destruction.
class ScopedStagingBuffer {
public:
  ScopedStagingBuffer(vk_Device *dev, VkDeviceSize size);
  ~ScopedStagingBuffer();

  ScopedStagingBuffer(const ScopedStagingBuffer &) = delete;
  ScopedStagingBuffer &operator=(const ScopedStagingBuffer &) = delete;

  bool valid() const { return m_valid; }
  VkBuffer buffer() const { return m_buffer; }
  void *mapped() const { return m_mapped; }

private:
  vk_Device *m_dev;
  VkBuffer m_buffer = VK_NULL_HANDLE;
  VkDeviceMemory m_memory = VK_NULL_HANDLE;
  void *m_mapped = nullptr;
  bool m_used_pool = false;
  bool m_valid = false;
};

// ---------------------------------------------------------------------------
// Convenience image layout transitions
// ---------------------------------------------------------------------------
void vk_cmd_transition_for_copy_dst(VkCommandBuffer cmd, VkImage image,
                                    uint32_t base_layer = 0,
                                    uint32_t layer_count = 1);
void vk_cmd_transition_for_copy_src(VkCommandBuffer cmd, VkImage image,
                                    uint32_t base_layer = 0,
                                    uint32_t layer_count = 1);
void vk_cmd_transition_for_compute(VkCommandBuffer cmd, VkImage image,
                                   uint32_t base_layer = 0,
                                   uint32_t layer_count = 1);
void vk_cmd_transition_for_present(VkCommandBuffer cmd, VkImage image);

// ---------------------------------------------------------------------------
// Descriptor set helpers (used by compute pipeline creation)
// ---------------------------------------------------------------------------
bool vk_create_compute_descriptor_set_layout(
    vk_Device *dev, const std::vector<vk_Resource *> &cbv,
    const std::vector<vk_Resource *> &srv,
    const std::vector<vk_Resource *> &uav,
    const std::vector<vk_Sampler *> &samplers, uint32_t bindless,
    VkDescriptorSetLayout *out_layout);

bool vk_allocate_and_write_descriptor_set(
    vk_Device *dev, const std::vector<vk_Resource *> &cbv,
    const std::vector<vk_Resource *> &srv,
    const std::vector<vk_Resource *> &uav,
    const std::vector<vk_Sampler *> &samplers, uint32_t bindless,
    VkDescriptorSetLayout layout, VkDescriptorPool *out_pool,
    VkDescriptorSet *out_set);

#endif // VK_UTILS_H