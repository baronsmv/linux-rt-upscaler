/**
 * @file vulkan_resource.h
 * @brief Vulkan resource (buffer/texture) type definition and methods.
 */

#ifndef VULKAN_RESOURCE_H
#define VULKAN_RESOURCE_H

#include "vulkan_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Public Python type object (defined in vulkan_resource.c)
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Resource_Type;

/* -------------------------------------------------------------------------
   Python object lifecycle
   ------------------------------------------------------------------------- */
void VkComp_Resource_Dealloc(VkComp_Resource *self);

/* -------------------------------------------------------------------------
   Resource method declarations (exposed to Python)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Resource_Upload(VkComp_Resource *self, PyObject *args);
PyObject *VkComp_Resource_Upload2D(VkComp_Resource *self, PyObject *args);
PyObject *VkComp_Resource_CopyTo(VkComp_Resource *self, PyObject *args);
PyObject *VkComp_Resource_Readback(VkComp_Resource *self, PyObject *args);
PyObject *VkComp_Resource_Download(VkComp_Resource *self, PyObject *args);
PyObject *VkComp_Resource_DownloadRegions(VkComp_Resource *self,
                                          PyObject *args);
PyObject *VkComp_Resource_UploadSubresource(VkComp_Resource *self,
                                            PyObject *args);
PyObject *VkComp_Resource_UploadSubresources(VkComp_Resource *self,
                                             PyObject *args);
PyObject *VkComp_Resource_BindTile(VkComp_Resource *self, PyObject *args);

/* -------------------------------------------------------------------------
   Inline helpers
   ------------------------------------------------------------------------- */

/**
 * @brief Check if resource is a buffer.
 */
static inline bool VkComp_Resource_IsBuffer(VkComp_Resource *res) {
  return res->buffer != VK_NULL_HANDLE;
}

/**
 * @brief Check if resource is a texture.
 */
static inline bool VkComp_Resource_IsTexture(VkComp_Resource *res) {
  return res->image != VK_NULL_HANDLE;
}

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_RESOURCE_H */