#ifndef VK_UTILS_H
#define VK_UTILS_H

#include "vk_common.h"
#include <functional>

/* ----------------------------------------------------------------------------
   Error checking macros
   ------------------------------------------------------------------------- */

/**
 * Check a Vulkan result. If not VK_SUCCESS, set a Python exception with a
 * formatted message and return NULL. Must be used inside a function returning
 * PyObject*.
 *
 * @param expr   Vulkan function call or VkResult variable.
 * @param errObj Python exception type (e.g., vk_ComputeError).
 * @param fmt    printf-style format string for the error message.
 * @param ...    arguments for the format string.
 */
#define VK_CHECK_OR_RETURN_NULL(expr, errObj, fmt, ...)                        \
  do {                                                                         \
    VkResult _res = (expr);                                                    \
    if (_res != VK_SUCCESS) {                                                  \
      PyErr_Format(errObj, fmt " (VkResult %d)", ##__VA_ARGS__, _res);         \
      return nullptr;                                                          \
    }                                                                          \
  } while (0)

/**
 * Check a Vulkan result. If not VK_SUCCESS, set a Python exception with a
 * formatted message and return false. For internal functions returning bool.
 */
#define VK_CHECK_OR_RETURN_FALSE(expr, errObj, fmt, ...)                       \
  do {                                                                         \
    VkResult _res = (expr);                                                    \
    if (_res != VK_SUCCESS) {                                                  \
      PyErr_Format(errObj, fmt " (VkResult %d)", ##__VA_ARGS__, _res);         \
      return false;                                                            \
    }                                                                          \
  } while (0)

/* ----------------------------------------------------------------------------
   Memory type and queue submission helpers
   ------------------------------------------------------------------------- */

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

bool vk_staging_buffer_acquire(vk_Device *dev, VkDeviceSize size,
                               VkBuffer *out_buffer, VkDeviceMemory *out_memory,
                               void **out_mapped, bool *used_pool);

void vk_staging_buffer_release(vk_Device *dev, VkBuffer buffer,
                               VkDeviceMemory memory, bool used_pool);

const char *vk_spirv_get_entry_point(const uint32_t *code, size_t size);
uint32_t *vk_spirv_patch_nonreadable_uav(const uint32_t *code, size_t size,
                                         uint32_t binding);

/* ----------------------------------------------------------------------------
   Command buffer management
   ------------------------------------------------------------------------- */

VkCommandBuffer vk_allocate_temp_cmd(vk_Device *dev);
void vk_free_temp_cmd(vk_Device *dev, VkCommandBuffer cmd);

/**
 * Execute a one-time command buffer: allocate, begin, record, end, submit,
 * wait for completion, and free. The recording function is called with the
 * command buffer. Returns true on success, false on failure (Python exception
 * set).
 */
bool vk_execute_one_time_commands(
    vk_Device *dev, const std::function<void(VkCommandBuffer)> &record_func);

/* ----------------------------------------------------------------------------
   Fence and queue submission
   ------------------------------------------------------------------------- */

VkFence vk_create_fence(vk_Device *dev, VkFenceCreateFlags flags = 0);

/**
 * Submit a command buffer to the device queue and wait for the fence.
 * The GIL is released during the wait. Returns VK_SUCCESS or an error code.
 */
VkResult vk_queue_submit_and_wait(vk_Device *dev, VkCommandBuffer cmd,
                                  VkFence fence);

/* ----------------------------------------------------------------------------
   Memory mapping (with Python error handling)
   ------------------------------------------------------------------------- */

/**
 * Map a device memory region. On failure, sets a Python exception and returns
 * nullptr. The caller must unmap with vkUnmapMemory.
 */
void *vk_map_memory(vk_Device *dev, VkDeviceMemory memory, VkDeviceSize offset,
                    VkDeviceSize size);

/* ----------------------------------------------------------------------------
   RAII wrapper for Python buffer objects
   ------------------------------------------------------------------------- */
struct PyBufferGuard {
  Py_buffer view;
  bool owned = false;

  PyBufferGuard() = default;
  ~PyBufferGuard() {
    if (owned)
      PyBuffer_Release(&view);
  }

  // Disable copy
  PyBufferGuard(const PyBufferGuard &) = delete;
  PyBufferGuard &operator=(const PyBufferGuard &) = delete;

  // Enable move
  PyBufferGuard(PyBufferGuard &&other) noexcept
      : view(other.view), owned(other.owned) {
    other.owned = false;
  }
  PyBufferGuard &operator=(PyBufferGuard &&other) noexcept {
    if (this != &other) {
      if (owned)
        PyBuffer_Release(&view);
      view = other.view;
      owned = other.owned;
      other.owned = false;
    }
    return *this;
  }

  bool acquire(PyObject *obj, int flags = PyBUF_SIMPLE) {
    if (PyObject_GetBuffer(obj, &view, flags) < 0)
      return false;
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
   RAII wrapper for staging buffers
   ------------------------------------------------------------------------- */
/**
 * ScopedStagingBuffer acquires a staging buffer from the pool on construction
 * and automatically releases it on destruction. Provides mapped pointer and
 * buffer handle.
 */
class ScopedStagingBuffer {
public:
  ScopedStagingBuffer(vk_Device *dev, VkDeviceSize size);
  ~ScopedStagingBuffer();

  // Disable copy
  ScopedStagingBuffer(const ScopedStagingBuffer &) = delete;
  ScopedStagingBuffer &operator=(const ScopedStagingBuffer &) = delete;

  // Returns true if acquisition succeeded.
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

/* ----------------------------------------------------------------------------
   Image layout transition helpers (convenience wrappers)
   ------------------------------------------------------------------------- */

/**
 * Transition an image to VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL.
 */
void vk_cmd_transition_for_copy_dst(VkCommandBuffer cmd, VkImage image,
                                    uint32_t base_layer = 0,
                                    uint32_t layer_count = 1);

/**
 * Transition an image to VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL.
 */
void vk_cmd_transition_for_copy_src(VkCommandBuffer cmd, VkImage image,
                                    uint32_t base_layer = 0,
                                    uint32_t layer_count = 1);

/**
 * Transition an image to VK_IMAGE_LAYOUT_GENERAL for compute shader access.
 */
void vk_cmd_transition_for_compute(VkCommandBuffer cmd, VkImage image,
                                   uint32_t base_layer = 0,
                                   uint32_t layer_count = 1);

/**
 * Transition an image to VK_IMAGE_LAYOUT_PRESENT_SRC_KHR.
 */
void vk_cmd_transition_for_present(VkCommandBuffer cmd, VkImage image);

/* ----------------------------------------------------------------------------
   Descriptor set helpers (used by compute pipeline creation)
   ------------------------------------------------------------------------- */

/**
 * Create a descriptor set layout for a compute pipeline.
 *
 * @param dev             Initialized device.
 * @param cbv             List of constant buffer resources.
 * @param srv             List of shader resource resources.
 * @param uav             List of unordered access resources.
 * @param samplers        List of samplers.
 * @param bindless        If >0, create bindless arrays of this size.
 * @param out_layout      Output descriptor set layout.
 * @return true on success, false with Python exception set.
 */
bool vk_create_compute_descriptor_set_layout(
    vk_Device *dev, const std::vector<vk_Resource *> &cbv,
    const std::vector<vk_Resource *> &srv,
    const std::vector<vk_Resource *> &uav,
    const std::vector<vk_Sampler *> &samplers, uint32_t bindless,
    VkDescriptorSetLayout *out_layout);

/**
 * Allocate a descriptor pool and descriptor set, then write the descriptors.
 *
 * @param dev             Initialized device.
 * @param cbv             List of constant buffer resources.
 * @param srv             List of shader resource resources.
 * @param uav             List of unordered access resources.
 * @param samplers        List of samplers.
 * @param bindless        If >0, treat bindings as arrays.
 * @param layout          Descriptor set layout.
 * @param out_pool        Output descriptor pool.
 * @param out_set         Output descriptor set.
 * @return true on success, false with Python exception set.
 */
bool vk_allocate_and_write_descriptor_set(
    vk_Device *dev, const std::vector<vk_Resource *> &cbv,
    const std::vector<vk_Resource *> &srv,
    const std::vector<vk_Resource *> &uav,
    const std::vector<vk_Sampler *> &samplers, uint32_t bindless,
    VkDescriptorSetLayout layout, VkDescriptorPool *out_pool,
    VkDescriptorSet *out_set);

#endif /* VK_UTILS_H */