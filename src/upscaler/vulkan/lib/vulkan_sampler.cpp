#include "vulkan_common.h"

static void vulkan_Sampler_dealloc(vulkan_Sampler *self) {
  if (self->py_device) {
    vkDestroySampler(self->py_device->device, self->sampler, NULL);
    Py_DECREF(self->py_device);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

PyTypeObject vulkan_Sampler_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Sampler",
    .tp_basicsize = sizeof(vulkan_Sampler),
    .tp_dealloc = (destructor)vulkan_Sampler_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};