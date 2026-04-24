#ifndef VK_COMPUTE_H
#define VK_COMPUTE_H

#include "vk_common.h"

// ---------------------------------------------------------------------------
// Python type for a compute pipeline and its bound resources
// ---------------------------------------------------------------------------
extern PyTypeObject vk_Compute_Type;

// Lifecycle
void vk_Compute_dealloc(vk_Compute *self);

// Pipeline creation (called from vk_device.cpp)
PyObject *vk_Device_create_compute_impl(vk_Device *self, PyObject *args,
                                        PyObject *kwds);

// Dispatch methods
PyObject *vk_Compute_dispatch(vk_Compute *self, PyObject *args);
PyObject *vk_Compute_dispatch_sequence(vk_Compute *self, PyObject *args,
                                       PyObject *kwds);
PyObject *vk_Compute_execute_tile_batch(vk_Compute *self, PyObject *args);

#endif // VK_COMPUTE_H