/**
 * @file vulkan_heap.h
 * @brief Vulkan memory heap type definition.
 */

#ifndef VULKAN_HEAP_H
#define VULKAN_HEAP_H

#include "vulkan_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Public Python type object (defined in vulkan_heap.c)
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Heap_Type;

/* -------------------------------------------------------------------------
   Python object lifecycle
   ------------------------------------------------------------------------- */

/**
 * @brief Deallocate the heap object (called by Python tp_dealloc).
 * @param self Heap object.
 */
void VkComp_Heap_Dealloc(VkComp_Heap *self);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_HEAP_H */