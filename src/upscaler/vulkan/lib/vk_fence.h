#ifndef VK_FENCE_H
#define VK_FENCE_H

#include "vk_common.h"

/* ----------------------------------------------------------------------------
   Fence type definition
   ------------------------------------------------------------------------- */
extern PyTypeObject vk_Fence_Type;

typedef struct {
    PyObject_HEAD;
    vk_Device* py_device;
    VkFence fence;
} vk_Fence;

/* ----------------------------------------------------------------------------
   Module‑level creation function
   ------------------------------------------------------------------------- */
/**
 * Create a new Vulkan fence.
 *
 * Args (keyword arguments):
 *     device (vk.Device, optional): Device to create the fence on.
 *                                   Uses the current device if omitted.
 *     signaled (bool, optional): If True, create the fence already signaled.
 *
 * Returns:
 *     vk.Fence object.
 */
PyObject* vk_create_fence(PyObject* self, PyObject* args, PyObject* kwds);

/* ----------------------------------------------------------------------------
   Fence methods
   ------------------------------------------------------------------------- */
/**
 * Wait for the fence to be signaled.
 *
 * Args:
 *     timeout_ns (int, optional): Timeout in nanoseconds. Default is UINT64_MAX.
 *
 * Returns:
 *     True if the fence was signaled, False on timeout.
 *     Raises an exception on error.
 */
PyObject* vk_Fence_wait(vk_Fence* self, PyObject* args);

/**
 * Reset the fence to the unsignaled state.
 */
PyObject* vk_Fence_reset(vk_Fence* self, PyObject* ignored);

/**
 * Query whether the fence is currently signaled.
 *
 * Returns:
 *     True if signaled, False otherwise.
 */
PyObject* vk_Fence_is_signaled(vk_Fence* self, PyObject* ignored);

/**
 * Return the raw VkFence handle as an integer.
 */
PyObject* vk_Fence_get_handle(vk_Fence* self, PyObject* ignored);

#endif /* VK_FENCE_H */