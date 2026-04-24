/**
 * @file vk_heap.cpp
 * @brief Vulkan memory heap wrapper.
 *
 * A `vk.Heap` encapsulates a single, contiguous `VkDeviceMemory` block.
 * It is intended for manual sub-allocation: multiple resources (buffers,
 * images) can be bound to non-overlapping regions of the same heap,
 * reducing the overall number of memory objects and decreasing driver
 * overhead.
 *
 * The Python object exposes two read-only properties:
 *   - `size`      - total usable bytes.
 *   - `heap_type` - one of `HEAP_DEFAULT` (device-local), `HEAP_UPLOAD`
 *                   (host-visible & coherent), or `HEAP_READBACK`
 *                   (host-visible, coherent, cached).
 *
 * Heaps are created by `Device.create_heap()` and typically never resized.
 * When the heap is destroyed, the underlying memory is freed and any
 * resources still bound to it become invalid - it is the application’s
 * responsibility to ensure that all such resources are released first.
 */

#include "vk_heap.h"

// =============================================================================
//  Lifecycle - deallocation
// =============================================================================

/**
 * Free the device memory and release the reference to the owning device.
 */
void vk_Heap_dealloc(vk_Heap *self) {
  if (self->py_device && self->memory) {
    vkFreeMemory(self->py_device->device, self->memory, nullptr);
  }
  Py_XDECREF(self->py_device);
  Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

// =============================================================================
//  Type definition
// =============================================================================

static PyMemberDef vk_Heap_members[] = {
    {"size", T_ULONGLONG, offsetof(vk_Heap, size), 0,
     "Total size of the heap in bytes."},
    {"heap_type", T_INT, offsetof(vk_Heap, heap_type), 0,
     "Memory type: 0=HEAP_DEFAULT (device-local), 1=HEAP_UPLOAD, "
     "2=HEAP_READBACK."},
    {nullptr}};

PyTypeObject vk_Heap_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0).tp_name = "vulkan.Heap",
    .tp_basicsize = sizeof(vk_Heap),
    .tp_dealloc = (destructor)vk_Heap_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = vk_Heap_members,
};