#include "vk_sampler.h"

void vk_Sampler_dealloc(vk_Sampler *self) {
    if (self->py_device && self->sampler) {
        vkDestroySampler(self->py_device->device, self->sampler, nullptr);
    }
    Py_XDECREF(self->py_device);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

PyTypeObject vk_Sampler_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Sampler",
    .tp_basicsize = sizeof(vk_Sampler),
    .tp_dealloc = (destructor)vk_Sampler_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};