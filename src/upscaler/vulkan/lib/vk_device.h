#ifndef VK_DEVICE_H
#define VK_DEVICE_H

#include "vk_common.h"

// ---------------------------------------------------------------------------
// Core device life-cycle
// ---------------------------------------------------------------------------

// Initialise the logical device and all auxiliary objects (command pool,
// staging pool, etc.). Idempotent - safe to call multiple times.
vk_Device *vk_Device_get_initialized(vk_Device *self);

// Destroy the logical device and free all associated resources.
void vk_Device_dealloc(vk_Device *self);

// ---------------------------------------------------------------------------
// Resource factories (return Python objects)
// ---------------------------------------------------------------------------

PyObject *vk_Device_create_heap(vk_Device *self, PyObject *args);
PyObject *vk_Device_create_buffer(vk_Device *self, PyObject *args);
PyObject *vk_Device_create_texture2d(vk_Device *self, PyObject *args);
PyObject *vk_Device_create_sampler(vk_Device *self, PyObject *args);
PyObject *vk_Device_create_compute(vk_Device *self, PyObject *args,
                                   PyObject *kwds);
PyObject *vk_Device_create_swapchain(vk_Device *self, PyObject *args);

// ---------------------------------------------------------------------------
// Debug & maintenance
// ---------------------------------------------------------------------------

PyObject *vk_Device_get_debug_messages(vk_Device *self, PyObject *ignored);
PyObject *vk_Device_set_buffer_pool_size(vk_Device *self, PyObject *args);

// ---------------------------------------------------------------------------
// Synchronisation
// ---------------------------------------------------------------------------

// Block until all GPU work has completed (heavy-handed).
PyObject *vk_Device_wait_idle(vk_Device *self, PyObject *ignored);

// Wait for a list of native fence handles (used for frame-level sync).
PyObject *vk_Device_wait_for_fences(vk_Device *self, PyObject *args);

#endif // VK_DEVICE_H