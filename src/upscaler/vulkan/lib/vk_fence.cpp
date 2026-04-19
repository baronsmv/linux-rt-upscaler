/**
 * @file vk_fence.cpp
 * @brief Vulkan fence implementation.
 *
 * Provides a Python wrapper for VkFence, used for GPU-CPU synchronization.
 */

#include "vk_fence.h"
#include "vk_device.h"
#include "vk_utils.h"

// Forward declaration
extern PyObject* vk_FenceError;

/* ----------------------------------------------------------------------------
   Fence deallocator
   ------------------------------------------------------------------------- */
void vk_Fence_dealloc(vk_Fence* self) {
    if (self->py_device && self->fence) {
        vkDestroyFence(self->py_device->device, self->fence, nullptr);
    }
    Py_XDECREF(self->py_device);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject*>(self));
}

/* ----------------------------------------------------------------------------
   vk_create_fence (module-level function)
   ------------------------------------------------------------------------- */
PyObject* vk_create_fence(PyObject* self, PyObject* args, PyObject* kwds) {
    static const char* kwlist[] = {"device", "signaled", nullptr};
    PyObject* device_obj = nullptr;
    int signaled = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|Op", (char**)kwlist,
                                     &device_obj, &signaled))
        return nullptr;

    vk_Device* dev = nullptr;
    if (device_obj && device_obj != Py_None) {
        if (!PyObject_TypeCheck(device_obj, &vk_Device_Type)) {
            PyErr_SetString(PyExc_TypeError, "device must be a vk.Device");
            return nullptr;
        }
        dev = reinterpret_cast<vk_Device*>(device_obj);
    } else {
        // Use current device from default context
        PyObject* mod = PyImport_ImportModule("vulkan");
        if (!mod) return nullptr;
        PyObject* get_dev = PyObject_GetAttrString(mod, "get_current_device");
        Py_DECREF(mod);
        if (!get_dev) return nullptr;
        PyObject* cur_dev = PyObject_CallObject(get_dev, nullptr);
        Py_DECREF(get_dev);
        if (!cur_dev) return nullptr;
        dev = reinterpret_cast<vk_Device*>(cur_dev);
    }

    // Ensure device is initialized
    dev = vk_Device_get_initialized(dev);
    if (!dev) return nullptr;

    VkFenceCreateInfo info = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    if (signaled) {
        info.flags = VK_FENCE_CREATE_SIGNALED_BIT;
    }

    VkFence fence;
    VkResult res = vkCreateFence(dev->device, &info, nullptr, &fence);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_FenceError, "Failed to create fence (VkResult %d)", res);
        return nullptr;
    }

    vk_Fence* py_fence = PyObject_New(vk_Fence, &vk_Fence_Type);
    if (!py_fence) {
        vkDestroyFence(dev->device, fence, nullptr);
        return PyErr_NoMemory();
    }
    VK_CLEAR_OBJECT(py_fence);
    py_fence->py_device = dev;
    Py_INCREF(dev);
    py_fence->fence = fence;

    return reinterpret_cast<PyObject*>(py_fence);
}

/* ----------------------------------------------------------------------------
   Fence.wait(timeout_ns=UINT64_MAX)
   ------------------------------------------------------------------------- */
PyObject* vk_Fence_wait(vk_Fence* self, PyObject* args) {
    unsigned long long timeout = UINT64_MAX;
    if (!PyArg_ParseTuple(args, "|K", &timeout))
        return nullptr;

    if (!self->fence) {
        PyErr_SetString(vk_FenceError, "Fence is invalid");
        return nullptr;
    }

    VkResult res;
    Py_BEGIN_ALLOW_THREADS
    res = vkWaitForFences(self->py_device->device, 1, &self->fence, VK_TRUE, timeout);
    Py_END_ALLOW_THREADS

    if (res == VK_TIMEOUT) {
        Py_RETURN_FALSE;
    } else if (res == VK_SUCCESS) {
        Py_RETURN_TRUE;
    } else {
        PyErr_Format(vk_FenceError, "vkWaitForFences failed (VkResult %d)", res);
        return nullptr;
    }
}

/* ----------------------------------------------------------------------------
   Fence.reset()
   ------------------------------------------------------------------------- */
PyObject* vk_Fence_reset(vk_Fence* self, PyObject* ignored) {
    if (!self->fence) {
        PyErr_SetString(vk_FenceError, "Fence is invalid");
        return nullptr;
    }
    VkResult res = vkResetFences(self->py_device->device, 1, &self->fence);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_FenceError, "vkResetFences failed (VkResult %d)", res);
        return nullptr;
    }
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Fence.is_signaled()
   ------------------------------------------------------------------------- */
PyObject* vk_Fence_is_signaled(vk_Fence* self, PyObject* ignored) {
    if (!self->fence) {
        PyErr_SetString(vk_FenceError, "Fence is invalid");
        return nullptr;
    }
    VkResult res = vkGetFenceStatus(self->py_device->device, self->fence);
    if (res == VK_SUCCESS) {
        Py_RETURN_TRUE;
    } else if (res == VK_NOT_READY) {
        Py_RETURN_FALSE;
    } else {
        PyErr_Format(vk_FenceError, "vkGetFenceStatus failed (VkResult %d)", res);
        return nullptr;
    }
}

/* ----------------------------------------------------------------------------
   Fence type definition
   ------------------------------------------------------------------------- */
static PyMethodDef vk_Fence_methods[] = {
    {"wait", (PyCFunction)vk_Fence_wait, METH_VARARGS,
     "Wait for the fence to be signaled. Returns True on success, False on timeout."},
    {"reset", (PyCFunction)vk_Fence_reset, METH_NOARGS,
     "Reset the fence to unsignaled state."},
    {"is_signaled", (PyCFunction)vk_Fence_is_signaled, METH_NOARGS,
     "Return True if the fence is currently signaled."},
    {nullptr, nullptr, 0, nullptr}
};

PyTypeObject vk_Fence_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Fence",
    .tp_basicsize = sizeof(vk_Fence),
    .tp_dealloc = (destructor)vk_Fence_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Fence_methods,
};