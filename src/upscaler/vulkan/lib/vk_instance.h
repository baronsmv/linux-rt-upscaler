#ifndef VK_INSTANCE_H
#define VK_INSTANCE_H

#include "vk_common.h"

// ---------------------------------------------------------------------------
// Global instance management
// ---------------------------------------------------------------------------

// Create the global VkInstance (idempotent). Returns true on success.
bool vk_instance_ensure(void);

// Enable validation layers / debug callbacks (must be called before instance).
PyObject *vk_enable_debug_mode(PyObject *self, PyObject *args);

// Return the required shader binary type (SPIR-V = 1).
PyObject *vk_get_shader_binary_type(PyObject *self);

// Enumerate physical devices and return a Python list of vk.Device objects.
PyObject *vk_get_discovered_devices(PyObject *self, PyObject *args);

#endif // VK_INSTANCE_H