/**
 * @file vk_heap.cpp
 * @brief Vulkan memory heap implementation.
 *
 * A vk.Heap represents a contiguous block of device memory that can be
 * suballocated to multiple resources. This reduces memory fragmentation
 * and allocation overhead.
 */

#include "vk_heap.h"

/* ----------------------------------------------------------------------------
   Heap deallocator
   ------------------------------------------------------------------------- */
void vk_Heap_dealloc(vk_Heap *self) {
    if (self->py_device && self->memory) {
        vkFreeMemory(self->py_device->device, self->memory, nullptr);
    }
    Py_XDECREF(self->py_device);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/* ----------------------------------------------------------------------------
   Heap type definition
   ------------------------------------------------------------------------- */
static PyMemberDef vk_Heap_members[] = {
    {"size", T_ULONGLONG, offsetof(vk_Heap, size), 0,
     "Heap size in bytes"},
    {"heap_type", T_INT, offsetof(vk_Heap, heap_type), 0,
     "Heap type (0=DEFAULT, 1=UPLOAD, 2=READBACK)"},
    {nullptr}
};

PyTypeObject vk_Heap_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Heap",
    .tp_basicsize = sizeof(vk_Heap),
    .tp_dealloc = (destructor)vk_Heap_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = vk_Heap_members,
};