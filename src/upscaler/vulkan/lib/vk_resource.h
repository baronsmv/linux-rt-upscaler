#ifndef VK_RESOURCE_H
#define VK_RESOURCE_H

#include "vk_common.h"

// ---------------------------------------------------------------------------
// Python type for a Vulkan buffer or image resource
// ---------------------------------------------------------------------------
extern PyTypeObject vk_Resource_Type;

// Lifecycle
void vk_Resource_dealloc(vk_Resource *self);

// Data transfer methods
PyObject *vk_Resource_upload(vk_Resource *self, PyObject *args);
PyObject *vk_Resource_upload_subresources(vk_Resource *self, PyObject *args);
PyObject *vk_Resource_download(vk_Resource *self, PyObject *ignored);
PyObject *vk_Resource_copy_to(vk_Resource *self, PyObject *args);
PyObject *vk_Resource_clear_color(vk_Resource *self, PyObject *args);

#endif // VK_RESOURCE_H