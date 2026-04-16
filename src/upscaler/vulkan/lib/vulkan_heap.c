/**
 * @file vulkan_heap.c
 * @brief Implementation of Vulkan memory heap Python type.
 */

#include "vulkan_heap.h"
#include "vulkan_device.h"
#include "vulkan_utils.h"
#include <string.h>

/* -------------------------------------------------------------------------
   Python type definition
   ------------------------------------------------------------------------- */
static PyMemberDef VkComp_Heap_members[] = {
    {"size", T_ULONGLONG, offsetof(VkComp_Heap, size), 0, "Heap size in bytes"},
    {"heap_type", T_INT, offsetof(VkComp_Heap, heap_type), 0,
     "Heap type (0=DEFAULT,1=UPLOAD,2=READBACK)"},
    {NULL}};

PyTypeObject VkComp_Heap_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Heap",
    .tp_basicsize = sizeof(VkComp_Heap),
    .tp_dealloc = (destructor)VkComp_Heap_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = VkComp_Heap_members,
};

/* -------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
void VkComp_Heap_Dealloc(VkComp_Heap *self) {
  if (self->device && self->device->device && self->memory) {
    vkFreeMemory(self->device->device, self->memory, NULL);
    Py_DECREF(self->device);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}