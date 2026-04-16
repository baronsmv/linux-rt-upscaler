#ifndef VK_SAMPLER_H
#define VK_SAMPLER_H

#include "vk_common.h"

extern PyTypeObject vk_Sampler_Type;

void vk_Sampler_dealloc(vk_Sampler *self);

#endif /* VK_SAMPLER_H */