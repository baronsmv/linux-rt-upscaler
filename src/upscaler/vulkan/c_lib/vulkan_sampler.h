/**
 * @file vulkan_sampler.h
 * @brief Vulkan sampler type definition.
 */

#ifndef VULKAN_SAMPLER_H
#define VULKAN_SAMPLER_H

#include "vulkan_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Public Python type object (defined in vulkan_sampler.c)
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Sampler_Type;

/* -------------------------------------------------------------------------
   Python object lifecycle
   ------------------------------------------------------------------------- */

/**
 * @brief Deallocate the sampler object (called by Python tp_dealloc).
 * @param self Sampler object.
 */
void VkComp_Sampler_Dealloc(VkComp_Sampler *self);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_SAMPLER_H */