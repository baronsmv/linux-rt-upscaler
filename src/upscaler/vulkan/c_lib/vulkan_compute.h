/**
 * @file vulkan_compute.h
 * @brief Vulkan compute pipeline type definition and methods.
 */

#ifndef VULKAN_COMPUTE_H
#define VULKAN_COMPUTE_H

#include "vulkan_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Public Python type object (defined in vulkan_compute.c)
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Compute_Type;

/* -------------------------------------------------------------------------
   Python object lifecycle
   ------------------------------------------------------------------------- */
void VkComp_Compute_Dealloc(VkComp_Compute *self);

/* -------------------------------------------------------------------------
   Internal constructor (called from Device.create_compute)
   ------------------------------------------------------------------------- */
VkComp_Compute *
VkComp_Compute_Create(VkComp_Device *device, Py_buffer *shader_view,
                      PyObject *cbv_list, PyObject *srv_list,
                      PyObject *uav_list, PyObject *samplers_list,
                      uint32_t push_size, uint32_t bindless_max);

/* -------------------------------------------------------------------------
   Compute method declarations (exposed to Python)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_Dispatch(VkComp_Compute *self, PyObject *args);
PyObject *VkComp_Compute_DispatchIndirect(VkComp_Compute *self, PyObject *args);
PyObject *VkComp_Compute_DispatchIndirectBatch(VkComp_Compute *self,
                                               PyObject *args);
PyObject *VkComp_Compute_DispatchSequence(VkComp_Compute *self, PyObject *args,
                                          PyObject *kwds);
PyObject *VkComp_Compute_DispatchTiles(VkComp_Compute *self, PyObject *args);
PyObject *VkComp_Compute_BindCBV(VkComp_Compute *self, PyObject *args);
PyObject *VkComp_Compute_BindSRV(VkComp_Compute *self, PyObject *args);
PyObject *VkComp_Compute_BindUAV(VkComp_Compute *self, PyObject *args);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_COMPUTE_H */