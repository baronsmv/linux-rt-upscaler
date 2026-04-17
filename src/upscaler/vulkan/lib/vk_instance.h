#ifndef VK_INSTANCE_H
#define VK_INSTANCE_H

#include "vk_common.h"

/* ----------------------------------------------------------------------------
   Ensures a global VkInstance exists. Must be called before any device creation.
   Returns true on success, false on failure (with Python exception set).
   ------------------------------------------------------------------------- */
bool vk_instance_ensure(void);

/* ----------------------------------------------------------------------------
   Enables Vulkan debug output (validation layers, debug utils).
   Must be called before vk_instance_ensure().
   ------------------------------------------------------------------------- */
PyObject *vk_enable_debug_mode(PyObject *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Returns the required shader binary type for Vulkan (SPIR-V = 1).
   ------------------------------------------------------------------------- */
PyObject *vk_get_shader_binary_type(PyObject *self);

/* ----------------------------------------------------------------------------
   Returns a Python list of all discovered physical devices (as vk_Device objects).
   ------------------------------------------------------------------------- */
PyObject *vk_get_discovered_devices(PyObject *self, PyObject *args);

#endif /* VK_INSTANCE_H */