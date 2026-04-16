#ifndef VK_DEVICE_H
#define VK_DEVICE_H

#include "vk_common.h"

/* ----------------------------------------------------------------------------
   vk_Device_get_initialized
   ------------------------------------------------------------------------- */
/**
 * Ensures that the given vk_Device has its logical device, queues, command
 * pool, and other per‑device structures initialised. This function is
 * idempotent and may be called multiple times safely.
 *
 * Returns the same device pointer on success, or NULL and sets a Python
 * exception on failure.
 */
vk_Device *vk_Device_get_initialized(vk_Device *self);

/* ----------------------------------------------------------------------------
   Device deallocator (internal, used by type)
   ------------------------------------------------------------------------- */
void vk_Device_dealloc(vk_Device *self);

/* ----------------------------------------------------------------------------
   Python method: create_heap
   ------------------------------------------------------------------------- */
/**
 * Create a memory heap that can be used to suballocate resources.
 *
 * Args:
 *     heap_type (int): 0 = DEFAULT (device local), 1 = UPLOAD (host visible),
 *                      2 = READBACK (host visible, cached).
 *     size (int): size in bytes.
 *
 * Returns:
 *     vk.Heap object.
 */
PyObject *vk_Device_create_heap(vk_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: create_buffer
   ------------------------------------------------------------------------- */
/**
 * Create a buffer resource.
 *
 * Args:
 *     heap_type (int): memory placement (0 = DEFAULT, 1 = UPLOAD, 2 = READBACK).
 *     size (int): buffer size in bytes.
 *     stride (int): element stride (used for formatted buffers).
 *     format (int): pixel format constant (e.g., R32G32B32A32_FLOAT) or 0.
 *     heap (vk.Heap or None): optional heap to suballocate from.
 *     heap_offset (int): offset within the heap.
 *     sparse (bool): whether to create a sparse resource.
 *
 * Returns:
 *     vk.Resource object.
 */
PyObject *vk_Device_create_buffer(vk_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: create_texture2d
   ------------------------------------------------------------------------- */
/**
 * Create a 2D texture (or 2D array) resource.
 *
 * Args:
 *     width (int): width in pixels.
 *     height (int): height in pixels.
 *     format (int): pixel format constant.
 *     heap (vk.Heap or None): optional heap to suballocate from.
 *     heap_offset (int): offset within the heap.
 *     slices (int): number of array layers (default 1).
 *     sparse (bool): whether to create a sparse resource.
 *
 * Returns:
 *     vk.Resource object.
 */
PyObject *vk_Device_create_texture2d(vk_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: create_sampler
   ------------------------------------------------------------------------- */
/**
 * Create a sampler object.
 *
 * Args:
 *     address_u (int): address mode for U (0=wrap, 1=mirror, 2=clamp).
 *     address_v (int): address mode for V.
 *     address_w (int): address mode for W.
 *     filter_min (int): minification filter (0=point, 1=linear).
 *     filter_mag (int): magnification filter.
 *
 * Returns:
 *     vk.Sampler object.
 */
PyObject *vk_Device_create_sampler(vk_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: create_compute
   ------------------------------------------------------------------------- */
/**
 * Create a compute pipeline.
 *
 * Args:
 *     shader (bytes): SPIR‑V binary.
 *     cbv (list[vk.Resource]): constant buffer views.
 *     srv (list[vk.Resource]): shader resource views.
 *     uav (list[vk.Resource]): unordered access views.
 *     samplers (list[vk.Sampler]): samplers.
 *     push_size (int): size of push constant block (must be multiple of 4).
 *     bindless (int): if >0, create bindless descriptor tables of this size.
 *
 * Returns:
 *     vk.Compute object.
 */
PyObject *vk_Device_create_compute(vk_Device *self, PyObject *args, PyObject *kwds);

/* ----------------------------------------------------------------------------
   Python method: create_swapchain
   ------------------------------------------------------------------------- */
/**
 * Create a swapchain for presenting to a window.
 *
 * Args:
 *     window_handle (tuple): (display_ptr, window_ptr) for X11.
 *     format (int): pixel format constant.
 *     num_buffers (int): desired number of swapchain images.
 *     width (int, optional): desired width (0 = use surface caps).
 *     height (int, optional): desired height.
 *     present_mode (str, optional): "fifo" (default), "mailbox", "immediate".
 *
 * Returns:
 *     vk.Swapchain object.
 */
PyObject *vk_Device_create_swapchain(vk_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: get_debug_messages
   ------------------------------------------------------------------------- */
/**
 * Retrieve and clear the list of Vulkan debug messages collected.
 *
 * Returns:
 *     list[str]: debug messages since last call.
 */
PyObject *vk_Device_get_debug_messages(vk_Device *self, PyObject *ignored);

/* ----------------------------------------------------------------------------
   Python method: wait_idle
   ------------------------------------------------------------------------- */
/**
 * Wait for all GPU work on this device to finish.
 */
PyObject *vk_Device_wait_idle(vk_Device *self, PyObject *ignored);

#endif /* VK_DEVICE_H */