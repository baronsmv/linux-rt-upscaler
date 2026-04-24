/**
 * @file vk_sampler.cpp
 * @brief Vulkan sampler wrapper - a lightweight Python object around VkSampler.
 *
 * A `vk.Sampler` encapsulates the configuration for texture sampling in
 * shaders: address modes (wrap, mirror, clamp) and minification/magnification
 * filters (point, linear). Instances are created by `Device.create_sampler()`
 * and bound to compute pipelines as immutable descriptors.
 *
 * The Python object is intentionally minimal - it stores only a reference to
 * the owning device and the native VkSampler handle.
 */

#include "vk_sampler.h"

// =============================================================================
//  Lifecycle - deallocation
// =============================================================================

/**
 * Destroy the native VkSampler and release the device reference.
 * The device is not idled; the caller must ensure the sampler is no longer
 * in use by any in-flight command buffer.
 */
void vk_Sampler_dealloc(vk_Sampler *self) {
  if (self->py_device && self->sampler) {
    vkDestroySampler(self->py_device->device, self->sampler, nullptr);
  }
  Py_XDECREF(self->py_device);
  Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

// =============================================================================
//  Type definition
// =============================================================================

PyTypeObject vk_Sampler_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0).tp_name = "vulkan.Sampler",
    .tp_basicsize = sizeof(vk_Sampler),
    .tp_dealloc = (destructor)vk_Sampler_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};