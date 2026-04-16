/**
 * @file vulkan_swapchain.h
 * @brief Vulkan swapchain type definition and methods.
 */

#ifndef VULKAN_SWAPCHAIN_H
#define VULKAN_SWAPCHAIN_H

#include "vulkan_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Public Python type object
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Swapchain_Type;

/* -------------------------------------------------------------------------
   Python object lifecycle
   ------------------------------------------------------------------------- */
void VkComp_Swapchain_Dealloc(VkComp_Swapchain *self);

/* -------------------------------------------------------------------------
   Internal constructor (called from Device.create_swapchain)
   ------------------------------------------------------------------------- */
VkComp_Swapchain *VkComp_Swapchain_Create(VkComp_Device *device,
                                          PyObject *window_handle, int format,
                                          uint32_t num_buffers, uint32_t width,
                                          uint32_t height,
                                          const char *present_mode);

/* -------------------------------------------------------------------------
   Python methods
   ------------------------------------------------------------------------- */
PyObject *VkComp_Swapchain_Present(VkComp_Swapchain *self, PyObject *args);
PyObject *VkComp_Swapchain_IsSuboptimal(VkComp_Swapchain *self, PyObject *args);
PyObject *VkComp_Swapchain_IsOutOfDate(VkComp_Swapchain *self, PyObject *args);
PyObject *VkComp_Swapchain_NeedsRecreation(VkComp_Swapchain *self,
                                           PyObject *args);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_SWAPCHAIN_H */