/**
 * @file vulkan_sampler.c
 * @brief Implementation of Vulkan sampler Python type.
 */

#include "vulkan_sampler.h"
#include "vulkan_device.h"
#include <string.h>

/* -------------------------------------------------------------------------
   Python type definition
   ------------------------------------------------------------------------- */
PyTypeObject VkComp_Sampler_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Sampler",
    .tp_basicsize = sizeof(VkComp_Sampler),
    .tp_dealloc = (destructor)VkComp_Sampler_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

/* -------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
void VkComp_Sampler_Dealloc(VkComp_Sampler *self) {
  if (self->device && self->device->device && self->sampler) {
    vkDestroySampler(self->device->device, self->sampler, NULL);
    Py_DECREF(self->device);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}