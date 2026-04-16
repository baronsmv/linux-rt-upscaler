#ifndef VK_SWAPCHAIN_H
#define VK_SWAPCHAIN_H

#include "vk_common.h"

extern PyTypeObject vk_Swapchain_Type;

void vk_Swapchain_dealloc(vk_Swapchain *self);

PyObject *vk_Device_create_swapchain_impl(vk_Device *self, PyObject *args);

PyObject *vk_Swapchain_present(vk_Swapchain *self, PyObject *args);
PyObject *vk_Swapchain_is_suboptimal(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_is_out_of_date(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_needs_recreation(vk_Swapchain *self, PyObject *ignored);

#endif /* VK_SWAPCHAIN_H */