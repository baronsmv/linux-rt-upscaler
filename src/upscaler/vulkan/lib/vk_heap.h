#ifndef VK_HEAP_H
#define VK_HEAP_H

#include "vk_common.h"

// ---------------------------------------------------------------------------
// Python type for a device memory heap
// ---------------------------------------------------------------------------
extern PyTypeObject vk_Heap_Type;

void vk_Heap_dealloc(vk_Heap *self);

#endif // VK_HEAP_H