/**
 * @file vulkan_compute.c
 * @brief Implementation of Vulkan compute pipeline Python type.
 *
 * This module creates compute pipelines from SPIR‑V shaders, manages
 * descriptor sets (including bindless), and provides dispatch methods
 * (direct, indirect, sequenced, and tiled).
 */

#include "vulkan_compute.h"
#include "vulkan_device.h"
#include "vulkan_resource.h"
#include "vulkan_utils.h"
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------------------------------
   Forward declarations of static helpers
   ------------------------------------------------------------------------- */
static VkResult
create_descriptor_set_layout(VkComp_Compute *comp, VkComp_Resource **cbv,
                             size_t cbv_count, VkComp_Resource **srv,
                             size_t srv_count, VkComp_Resource **uav,
                             size_t uav_count, VkComp_Sampler **samplers,
                             size_t sampler_count, uint32_t bindless_max);
static VkResult create_pipeline_layout(VkComp_Compute *comp,
                                       uint32_t push_size);
static VkResult create_compute_pipeline(VkComp_Compute *comp,
                                        const uint32_t *code, size_t code_size,
                                        const char *entry_point);
static VkResult allocate_and_update_descriptor_set(
    VkComp_Compute *comp, VkComp_Resource **cbv, size_t cbv_count,
    VkComp_Resource **srv, size_t srv_count, VkComp_Resource **uav,
    size_t uav_count, VkComp_Sampler **samplers, size_t sampler_count);
static void fill_bindless_lists(VkComp_Compute *comp, VkComp_Resource **cbv,
                                size_t cbv_count, VkComp_Resource **srv,
                                size_t srv_count, VkComp_Resource **uav,
                                size_t uav_count, VkComp_Sampler **samplers,
                                size_t sampler_count);

/* -------------------------------------------------------------------------
   Python type definition
   ------------------------------------------------------------------------- */
static PyMethodDef VkComp_Compute_methods[] = {
    {"dispatch", (PyCFunction)VkComp_Compute_Dispatch, METH_VARARGS,
     "Dispatch compute workgroups (x, y, z) with optional push constants."},
    {"dispatch_indirect", (PyCFunction)VkComp_Compute_DispatchIndirect,
     METH_VARARGS, "Dispatch using indirect arguments from a buffer."},
    {"dispatch_indirect_batch",
     (PyCFunction)VkComp_Compute_DispatchIndirectBatch, METH_VARARGS,
     "Dispatch multiple indirect dispatches from a buffer."},
    {"dispatch_sequence", (PyCFunction)VkComp_Compute_DispatchSequence,
     METH_VARARGS | METH_KEYWORDS,
     "Submit a sequence of dispatches with optional pre/post copies."},
    {"dispatch_tiles", (PyCFunction)VkComp_Compute_DispatchTiles, METH_VARARGS,
     "Dispatch multiple tiles with per‑tile push constants."},
    {"bind_cbv", (PyCFunction)VkComp_Compute_BindCBV, METH_VARARGS,
     "Bind a constant buffer view (bindless mode only)."},
    {"bind_srv", (PyCFunction)VkComp_Compute_BindSRV, METH_VARARGS,
     "Bind a shader resource view (bindless mode only)."},
    {"bind_uav", (PyCFunction)VkComp_Compute_BindUAV, METH_VARARGS,
     "Bind an unordered access view (bindless mode only)."},
    {NULL, NULL, 0, NULL}};

PyTypeObject VkComp_Compute_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Compute",
    .tp_basicsize = sizeof(VkComp_Compute),
    .tp_dealloc = (destructor)VkComp_Compute_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = VkComp_Compute_methods,
};

/* -------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
void VkComp_Compute_Dealloc(VkComp_Compute *self) {
  if (self->device && self->device->device) {
    VkDevice dev = self->device->device;
    if (self->pipeline)
      vkDestroyPipeline(dev, self->pipeline, NULL);
    if (self->pipeline_layout)
      vkDestroyPipelineLayout(dev, self->pipeline_layout, NULL);
    if (self->descriptor_pool)
      vkDestroyDescriptorPool(dev, self->descriptor_pool, NULL);
    if (self->descriptor_set_layout)
      vkDestroyDescriptorSetLayout(dev, self->descriptor_set_layout, NULL);
    if (self->shader_module)
      vkDestroyShaderModule(dev, self->shader_module, NULL);
    if (self->dispatch_fence)
      vkDestroyFence(dev, self->dispatch_fence, NULL);
    Py_DECREF(self->device);
  }
  Py_XDECREF(self->cbv_list);
  Py_XDECREF(self->srv_list);
  Py_XDECREF(self->uav_list);
  Py_XDECREF(self->samplers_list);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* -------------------------------------------------------------------------
   Python method: __new__ / __init__ is handled by Device.create_compute
   (implemented in vulkan_device.c, calls into a helper here)
   ------------------------------------------------------------------------- */

/**
 * @brief Internal constructor called from VkComp_Device_CreateCompute.
 */
VkComp_Compute *
VkComp_Compute_Create(VkComp_Device *device, Py_buffer *shader_view,
                      PyObject *cbv_list, PyObject *srv_list,
                      PyObject *uav_list, PyObject *samplers_list,
                      uint32_t push_size, uint32_t bindless_max) {
  VkComp_Compute *comp = PyObject_New(VkComp_Compute, &VkComp_Compute_Type);
  if (!comp)
    return NULL;
  VKCOMP_CLEAR_OBJECT(comp);
  comp->device = device;
  Py_INCREF(device);
  comp->push_constant_size = push_size;
  comp->bindless_max = bindless_max;

  /* Validate and collect descriptors */
  VkComp_Resource **cbv = NULL, **srv = NULL, **uav = NULL;
  VkComp_Sampler **samplers = NULL;
  size_t cbv_count = 0, srv_count = 0, uav_count = 0, sampler_count = 0;

  if (!vkcomp_check_descriptors(
          &VkComp_Resource_Type, cbv_list, &cbv, &cbv_count, srv_list, &srv,
          &srv_count, uav_list, &uav, &uav_count, &VkComp_Sampler_Type,
          samplers_list, &samplers, &sampler_count)) {
    Py_DECREF(comp);
    return NULL;
  }

  /* Validate bindless limits */
  if (bindless_max > 0) {
    if (cbv_count > bindless_max || srv_count > bindless_max ||
        uav_count > bindless_max) {
      PyErr_Format(PyExc_ValueError,
                   "Too many initial resources for bindless (max %u)",
                   bindless_max);
      goto error;
    }
    if (!device->supports_bindless) {
      PyErr_SetString(PyExc_ValueError,
                      "Bindless not supported on this device");
      goto error;
    }
  }

  /* Create fence for dispatches */
  VkFenceCreateInfo fence_info = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
  if (vkCreateFence(device->device, &fence_info, NULL, &comp->dispatch_fence) !=
      VK_SUCCESS) {
    PyErr_SetString(VkComp_ComputeError, "Failed to create dispatch fence");
    goto error;
  }

  /* Create descriptor set layout */
  if (create_descriptor_set_layout(comp, cbv, cbv_count, srv, srv_count, uav,
                                   uav_count, samplers, sampler_count,
                                   bindless_max) != VK_SUCCESS) {
    PyErr_SetString(VkComp_ComputeError,
                    "Failed to create descriptor set layout");
    goto error;
  }

  /* Create pipeline layout */
  if (create_pipeline_layout(comp, push_size) != VK_SUCCESS) {
    PyErr_SetString(VkComp_ComputeError, "Failed to create pipeline layout");
    goto error;
  }

  /* Patch SPIR‑V for BGRA UAVs if needed */
  const uint32_t *code = (const uint32_t *)shader_view->buf;
  size_t code_size = shader_view->len;
  uint32_t *patched_code = NULL;

  if (!device->features.shaderStorageImageReadWithoutFormat) {
    uint32_t binding = 2048;
    for (size_t i = 0; i < uav_count; i++) {
      if (uav[i]->image && (uav[i]->format == VK_FORMAT_B8G8R8A8_UNORM ||
                            uav[i]->format == VK_FORMAT_B8G8R8A8_SRGB)) {
        patched_code = vkcomp_patch_spirv_unknown_uav(code, code_size, binding);
        if (patched_code) {
          code = patched_code;
          code_size += 12;
        }
        break;
      }
      binding++;
    }
  }

  /* Extract entry point */
  const char *entry = vkcomp_get_spirv_entry_point(code, code_size);
  if (!entry) {
    PyErr_SetString(VkComp_ComputeError, "Invalid SPIR‑V: no entry point");
    if (patched_code)
      PyMem_Free(patched_code);
    goto error;
  }

  /* Create shader module and pipeline */
  if (create_compute_pipeline(comp, code, code_size, entry) != VK_SUCCESS) {
    PyErr_SetString(VkComp_ComputeError, "Failed to create compute pipeline");
    if (patched_code)
      PyMem_Free(patched_code);
    goto error;
  }

  if (patched_code)
    PyMem_Free(patched_code);

  /* Allocate descriptor pool and descriptor set */
  if (allocate_and_update_descriptor_set(comp, cbv, cbv_count, srv, srv_count,
                                         uav, uav_count, samplers,
                                         sampler_count) != VK_SUCCESS) {
    PyErr_SetString(VkComp_ComputeError,
                    "Failed to allocate/update descriptor set");
    goto error;
  }

  /* Fill Python lists for bindless */
  fill_bindless_lists(comp, cbv, cbv_count, srv, srv_count, uav, uav_count,
                      samplers, sampler_count);

  /* Cleanup temporary arrays */
  if (cbv)
    PyMem_Free(cbv);
  if (srv)
    PyMem_Free(srv);
  if (uav)
    PyMem_Free(uav);
  if (samplers)
    PyMem_Free(samplers);

  return comp;

error:
  if (cbv)
    PyMem_Free(cbv);
  if (srv)
    PyMem_Free(srv);
  if (uav)
    PyMem_Free(uav);
  if (samplers)
    PyMem_Free(samplers);
  Py_DECREF(comp);
  return NULL;
}

/* -------------------------------------------------------------------------
   Descriptor set layout creation (supports bindless)
   ------------------------------------------------------------------------- */
static VkResult
create_descriptor_set_layout(VkComp_Compute *comp, VkComp_Resource **cbv,
                             size_t cbv_count, VkComp_Resource **srv,
                             size_t srv_count, VkComp_Resource **uav,
                             size_t uav_count, VkComp_Sampler **samplers,
                             size_t sampler_count, uint32_t bindless_max) {
  VkDevice dev = comp->device->device;
  size_t binding_count = 0;
  VkDescriptorSetLayoutBinding *bindings = NULL;
  VkDescriptorBindingFlags *binding_flags = NULL;

  if (bindless_max > 0) {
    binding_count = bindless_max * 3 + sampler_count;
    bindings =
        PyMem_Malloc(binding_count * sizeof(VkDescriptorSetLayoutBinding));
    binding_flags =
        PyMem_Malloc(binding_count * sizeof(VkDescriptorBindingFlags));
    if (!bindings || !binding_flags) {
      PyMem_Free(bindings);
      PyMem_Free(binding_flags);
      return VK_ERROR_OUT_OF_HOST_MEMORY;
    }

    VkDescriptorBindingFlags flags =
        VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT |
        VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT;
    for (uint32_t i = 0; i < bindless_max; i++) {
      bindings[i] = (VkDescriptorSetLayoutBinding){
          .binding = i,
          .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
      binding_flags[i] = flags;
    }
    for (uint32_t i = 0; i < bindless_max; i++) {
      bindings[bindless_max + i] = (VkDescriptorSetLayoutBinding){
          .binding = 1024 + i,
          .descriptorType = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
      binding_flags[bindless_max + i] = flags;
    }
    for (uint32_t i = 0; i < bindless_max; i++) {
      bindings[2 * bindless_max + i] = (VkDescriptorSetLayoutBinding){
          .binding = 2048 + i,
          .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_IMAGE,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
      binding_flags[2 * bindless_max + i] = flags;
    }
    size_t offset = 3 * bindless_max;
    for (size_t i = 0; i < sampler_count; i++) {
      bindings[offset + i] = (VkDescriptorSetLayoutBinding){
          .binding = 3072 + (uint32_t)i,
          .descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
      binding_flags[offset + i] = 0;
    }
  } else {
    /* Non‑bindless: exact bindings */
    binding_count = cbv_count + srv_count + uav_count + sampler_count;
    bindings =
        PyMem_Malloc(binding_count * sizeof(VkDescriptorSetLayoutBinding));
    if (!bindings)
      return VK_ERROR_OUT_OF_HOST_MEMORY;

    size_t idx = 0;
    for (size_t i = 0; i < cbv_count; i++) {
      bindings[idx++] = (VkDescriptorSetLayoutBinding){
          .binding = (uint32_t)i,
          .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
    }
    for (size_t i = 0; i < srv_count; i++) {
      VkDescriptorType dtype =
          srv[i]->buffer
              ? (srv[i]->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                                     : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER)
              : VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
      bindings[idx++] = (VkDescriptorSetLayoutBinding){
          .binding = 1024 + (uint32_t)i,
          .descriptorType = dtype,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
    }
    for (size_t i = 0; i < uav_count; i++) {
      VkDescriptorType dtype =
          uav[i]->buffer
              ? (uav[i]->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                                     : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER)
              : VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
      bindings[idx++] = (VkDescriptorSetLayoutBinding){
          .binding = 2048 + (uint32_t)i,
          .descriptorType = dtype,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
    }
    for (size_t i = 0; i < sampler_count; i++) {
      bindings[idx++] = (VkDescriptorSetLayoutBinding){
          .binding = 3072 + (uint32_t)i,
          .descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER,
          .descriptorCount = 1,
          .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      };
    }
  }

  VkDescriptorSetLayoutCreateInfo layout_info = {
      .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
      .bindingCount = (uint32_t)binding_count,
      .pBindings = bindings,
  };
  VkDescriptorSetLayoutBindingFlagsCreateInfo flags_info = {
      .sType =
          VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_BINDING_FLAGS_CREATE_INFO,
      .bindingCount = (uint32_t)binding_count,
      .pBindingFlags = binding_flags,
  };
  if (bindless_max > 0) {
    layout_info.pNext = &flags_info;
    layout_info.flags =
        VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT;
  }

  VkResult res = vkCreateDescriptorSetLayout(dev, &layout_info, NULL,
                                             &comp->descriptor_set_layout);
  PyMem_Free(bindings);
  PyMem_Free(binding_flags);
  return res;
}

/* -------------------------------------------------------------------------
   Pipeline layout creation
   ------------------------------------------------------------------------- */
static VkResult create_pipeline_layout(VkComp_Compute *comp,
                                       uint32_t push_size) {
  VkPushConstantRange pc_range = {
      .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
      .offset = 0,
      .size = push_size,
  };
  VkPipelineLayoutCreateInfo layout_info = {
      .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
      .setLayoutCount = 1,
      .pSetLayouts = &comp->descriptor_set_layout,
      .pushConstantRangeCount = push_size > 0 ? 1 : 0,
      .pPushConstantRanges = push_size > 0 ? &pc_range : NULL,
  };
  return vkCreatePipelineLayout(comp->device->device, &layout_info, NULL,
                                &comp->pipeline_layout);
}

/* -------------------------------------------------------------------------
   Compute pipeline creation
   ------------------------------------------------------------------------- */
static VkResult create_compute_pipeline(VkComp_Compute *comp,
                                        const uint32_t *code, size_t code_size,
                                        const char *entry_point) {
  VkDevice dev = comp->device->device;

  VkShaderModuleCreateInfo shader_info = {
      .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
      .codeSize = code_size,
      .pCode = code,
  };
  VkResult res =
      vkCreateShaderModule(dev, &shader_info, NULL, &comp->shader_module);
  if (res != VK_SUCCESS)
    return res;

  VkComputePipelineCreateInfo pipeline_info = {
      .sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,
      .stage =
          {
              .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
              .stage = VK_SHADER_STAGE_COMPUTE_BIT,
              .module = comp->shader_module,
              .pName = entry_point,
          },
      .layout = comp->pipeline_layout,
  };
  res = vkCreateComputePipelines(dev, VK_NULL_HANDLE, 1, &pipeline_info, NULL,
                                 &comp->pipeline);
  if (res != VK_SUCCESS) {
    vkDestroyShaderModule(dev, comp->shader_module, NULL);
    comp->shader_module = VK_NULL_HANDLE;
  }
  return res;
}

/* -------------------------------------------------------------------------
   Descriptor pool and set allocation + update
   ------------------------------------------------------------------------- */
static VkResult allocate_and_update_descriptor_set(
    VkComp_Compute *comp, VkComp_Resource **cbv, size_t cbv_count,
    VkComp_Resource **srv, size_t srv_count, VkComp_Resource **uav,
    size_t uav_count, VkComp_Sampler **samplers, size_t sampler_count) {
  VkDevice dev = comp->device->device;

  /* Count descriptor pool sizes */
  uint32_t uniform_buffer_count = (uint32_t)cbv_count;
  uint32_t storage_buffer_count = 0;
  uint32_t sampled_image_count = 0;
  uint32_t storage_image_count = 0;
  uint32_t sampler_count_desc = (uint32_t)sampler_count;
  uint32_t uniform_texel_count = 0;
  uint32_t storage_texel_count = 0;

  for (size_t i = 0; i < srv_count; i++) {
    if (srv[i]->buffer) {
      if (srv[i]->buffer_view)
        uniform_texel_count++;
      else
        uniform_buffer_count++;
    } else {
      sampled_image_count++;
    }
  }
  for (size_t i = 0; i < uav_count; i++) {
    if (uav[i]->buffer) {
      if (uav[i]->buffer_view)
        storage_texel_count++;
      else
        storage_buffer_count++;
    } else {
      storage_image_count++;
    }
  }

  if (comp->bindless_max > 0) {
    uniform_buffer_count = comp->bindless_max;
    sampled_image_count = comp->bindless_max;
    storage_image_count = comp->bindless_max;
  }

  VkDescriptorPoolSize pool_sizes[6];
  uint32_t pool_size_count = 0;
#define ADD_POOL_SIZE(desc_type, count)                                        \
  if ((count) > 0) {                                                           \
    pool_sizes[pool_size_count].type = (desc_type);                            \
    pool_sizes[pool_size_count].descriptorCount = (count);                     \
    pool_size_count++;                                                         \
  }
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, uniform_buffer_count);
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, storage_buffer_count);
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, sampled_image_count);
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, storage_image_count);
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_SAMPLER, sampler_count_desc);
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER, uniform_texel_count);
  ADD_POOL_SIZE(VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER, storage_texel_count);
#undef ADD_POOL_SIZE

  VkDescriptorPoolCreateInfo pool_info = {
      .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,
      .maxSets = 1,
      .poolSizeCount = pool_size_count,
      .pPoolSizes = pool_sizes,
  };
  if (comp->bindless_max > 0) {
    pool_info.flags = VK_DESCRIPTOR_POOL_CREATE_UPDATE_AFTER_BIND_BIT;
  }
  VkResult res =
      vkCreateDescriptorPool(dev, &pool_info, NULL, &comp->descriptor_pool);
  if (res != VK_SUCCESS)
    return res;

  VkDescriptorSetAllocateInfo alloc_info = {
      .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,
      .descriptorPool = comp->descriptor_pool,
      .descriptorSetCount = 1,
      .pSetLayouts = &comp->descriptor_set_layout,
  };
  res = vkAllocateDescriptorSets(dev, &alloc_info, &comp->descriptor_set);
  if (res != VK_SUCCESS)
    return res;

  /* Build write descriptors */
  size_t write_count = cbv_count + srv_count + uav_count + sampler_count;
  VkWriteDescriptorSet *writes =
      PyMem_Malloc(write_count * sizeof(VkWriteDescriptorSet));
  if (!writes)
    return VK_ERROR_OUT_OF_HOST_MEMORY;

  size_t idx = 0;
  for (size_t i = 0; i < cbv_count; i++) {
    writes[idx++] = (VkWriteDescriptorSet){
        .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
        .dstSet = comp->descriptor_set,
        .dstBinding = (uint32_t)i,
        .dstArrayElement = 0,
        .descriptorCount = 1,
        .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
        .pBufferInfo = &cbv[i]->descriptor_buffer_info,
    };
  }
  for (size_t i = 0; i < srv_count; i++) {
    VkDescriptorType dtype =
        srv[i]->buffer
            ? (srv[i]->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                                   : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER)
            : VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
    writes[idx++] = (VkWriteDescriptorSet){
        .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
        .dstSet = comp->descriptor_set,
        .dstBinding = 1024 + (uint32_t)i,
        .descriptorCount = 1,
        .descriptorType = dtype,
        .pBufferInfo = srv[i]->buffer && !srv[i]->buffer_view
                           ? &srv[i]->descriptor_buffer_info
                           : NULL,
        .pTexelBufferView = srv[i]->buffer_view ? &srv[i]->buffer_view : NULL,
        .pImageInfo = !srv[i]->buffer ? &srv[i]->descriptor_image_info : NULL,
    };
  }
  for (size_t i = 0; i < uav_count; i++) {
    VkDescriptorType dtype =
        uav[i]->buffer
            ? (uav[i]->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                                   : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER)
            : VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
    writes[idx++] = (VkWriteDescriptorSet){
        .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
        .dstSet = comp->descriptor_set,
        .dstBinding = 2048 + (uint32_t)i,
        .descriptorCount = 1,
        .descriptorType = dtype,
        .pBufferInfo = uav[i]->buffer && !uav[i]->buffer_view
                           ? &uav[i]->descriptor_buffer_info
                           : NULL,
        .pTexelBufferView = uav[i]->buffer_view ? &uav[i]->buffer_view : NULL,
        .pImageInfo = !uav[i]->buffer ? &uav[i]->descriptor_image_info : NULL,
    };
  }
  for (size_t i = 0; i < sampler_count; i++) {
    writes[idx++] = (VkWriteDescriptorSet){
        .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
        .dstSet = comp->descriptor_set,
        .dstBinding = 3072 + (uint32_t)i,
        .descriptorCount = 1,
        .descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER,
        .pImageInfo = &samplers[i]->descriptor_image_info,
    };
  }

  vkUpdateDescriptorSets(dev, (uint32_t)write_count, writes, 0, NULL);
  PyMem_Free(writes);
  return VK_SUCCESS;
}

/* -------------------------------------------------------------------------
   Fill Python lists for bindless binding methods
   ------------------------------------------------------------------------- */
static void fill_bindless_lists(VkComp_Compute *comp, VkComp_Resource **cbv,
                                size_t cbv_count, VkComp_Resource **srv,
                                size_t srv_count, VkComp_Resource **uav,
                                size_t uav_count, VkComp_Sampler **samplers,
                                size_t sampler_count) {
  size_t max_cbv = comp->bindless_max > 0 ? comp->bindless_max : cbv_count;
  size_t max_srv = comp->bindless_max > 0 ? comp->bindless_max : srv_count;
  size_t max_uav = comp->bindless_max > 0 ? comp->bindless_max : uav_count;

  comp->cbv_list = PyList_New(max_cbv);
  comp->srv_list = PyList_New(max_srv);
  comp->uav_list = PyList_New(max_uav);
  comp->samplers_list = PyList_New(sampler_count);

  for (size_t i = 0; i < max_cbv; i++) {
    PyObject *item = (i < cbv_count) ? (PyObject *)cbv[i] : Py_None;
    Py_INCREF(item);
    PyList_SetItem(comp->cbv_list, i, item);
  }
  for (size_t i = 0; i < max_srv; i++) {
    PyObject *item = (i < srv_count) ? (PyObject *)srv[i] : Py_None;
    Py_INCREF(item);
    PyList_SetItem(comp->srv_list, i, item);
  }
  for (size_t i = 0; i < max_uav; i++) {
    PyObject *item = (i < uav_count) ? (PyObject *)uav[i] : Py_None;
    Py_INCREF(item);
    PyList_SetItem(comp->uav_list, i, item);
  }
  for (size_t i = 0; i < sampler_count; i++) {
    PyList_SetItem(comp->samplers_list, i, (PyObject *)samplers[i]);
  }
}

/* -------------------------------------------------------------------------
   dispatch(x, y, z, push_data=b"")
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_Dispatch(VkComp_Compute *self, PyObject *args) {
  unsigned int x, y, z;
  Py_buffer push = {0};
  if (!PyArg_ParseTuple(args, "III|y*", &x, &y, &z, &push))
    return NULL;

  if (push.len > 0) {
    if (push.len > self->push_constant_size || (push.len % 4) != 0) {
      PyBuffer_Release(&push);
      PyErr_Format(PyExc_ValueError,
                   "Push constant size %zd (max %u, must be multiple of 4)",
                   push.len, self->push_constant_size);
      return NULL;
    }
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev) {
    if (push.buf)
      PyBuffer_Release(&push);
    return NULL;
  }

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    if (push.buf)
      PyBuffer_Release(&push);
    PyErr_Format(VkComp_ComputeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  if (push.len > 0) {
    vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, (uint32_t)push.len, push.buf);
  }

  vkCmdDispatch(cmd, x, y, z);
  vkEndCommandBuffer(cmd);

  if (push.buf)
    PyBuffer_Release(&push);

  res = vkcomp_submit_and_wait(dev, cmd, self->dispatch_fence);
  VkComp_Device_FreeCmd(dev, cmd);

  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_ComputeError, "Dispatch submission failed: %d", res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   dispatch_indirect(indirect_buffer, offset=0, push_data=b"")
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_DispatchIndirect(VkComp_Compute *self,
                                          PyObject *args) {
  PyObject *indirect_obj;
  unsigned int offset = 0;
  Py_buffer push = {0};
  if (!PyArg_ParseTuple(args, "O|Iy*", &indirect_obj, &offset, &push))
    return NULL;

  if (!PyObject_TypeCheck(indirect_obj, &VkComp_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Buffer object");
    if (push.buf)
      PyBuffer_Release(&push);
    return NULL;
  }
  VkComp_Resource *indirect = (VkComp_Resource *)indirect_obj;
  if (!VkComp_Resource_IsBuffer(indirect)) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
    if (push.buf)
      PyBuffer_Release(&push);
    return NULL;
  }

  if (push.len > 0) {
    if (push.len > self->push_constant_size || (push.len % 4) != 0) {
      PyBuffer_Release(&push);
      PyErr_Format(PyExc_ValueError,
                   "Push constant size %zd (max %u, must be multiple of 4)",
                   push.len, self->push_constant_size);
      return NULL;
    }
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev) {
    if (push.buf)
      PyBuffer_Release(&push);
    return NULL;
  }

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    if (push.buf)
      PyBuffer_Release(&push);
    PyErr_Format(VkComp_ComputeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  if (push.len > 0) {
    vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, (uint32_t)push.len, push.buf);
  }

  vkCmdDispatchIndirect(cmd, indirect->buffer, offset);
  vkEndCommandBuffer(cmd);

  if (push.buf)
    PyBuffer_Release(&push);

  res = vkcomp_submit_and_wait(dev, cmd, self->dispatch_fence);
  VkComp_Device_FreeCmd(dev, cmd);

  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_ComputeError, "Indirect dispatch submission failed: %d",
                 res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   dispatch_indirect_batch
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_DispatchIndirectBatch(VkComp_Compute *self,
                                               PyObject *args) {
  PyObject *indirect_obj;
  unsigned int offset, count, stride;
  Py_buffer push = {0};
  if (!PyArg_ParseTuple(args, "OIII|y*", &indirect_obj, &offset, &count,
                        &stride, &push))
    return NULL;

  if (!PyObject_TypeCheck(indirect_obj, &VkComp_Resource_Type)) {
    if (push.buf)
      PyBuffer_Release(&push);
    PyErr_SetString(PyExc_TypeError, "Expected a Buffer object");
    return NULL;
  }
  VkComp_Resource *indirect = (VkComp_Resource *)indirect_obj;
  if (!VkComp_Resource_IsBuffer(indirect)) {
    if (push.buf)
      PyBuffer_Release(&push);
    PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
    return NULL;
  }

  if (push.len > 0) {
    if (push.len > self->push_constant_size || (push.len % 4) != 0) {
      PyBuffer_Release(&push);
      PyErr_Format(PyExc_ValueError,
                   "Push constant size %zd (max %u, must be multiple of 4)",
                   push.len, self->push_constant_size);
      return NULL;
    }
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev) {
    if (push.buf)
      PyBuffer_Release(&push);
    return NULL;
  }

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    if (push.buf)
      PyBuffer_Release(&push);
    PyErr_Format(VkComp_ComputeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  if (push.len > 0) {
    vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, (uint32_t)push.len, push.buf);
  }

  for (unsigned int i = 0; i < count; i++) {
    vkCmdDispatchIndirect(cmd, indirect->buffer, offset + i * stride);
  }

  vkEndCommandBuffer(cmd);

  if (push.buf)
    PyBuffer_Release(&push);

  res = vkcomp_submit_and_wait(dev, cmd, self->dispatch_fence);
  VkComp_Device_FreeCmd(dev, cmd);

  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_ComputeError, "Batch indirect dispatch failed: %d",
                 res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   dispatch_sequence(sequence, copy_src=None, copy_dst=None, copy_slice=0,
                     present_image=None, timestamps=False)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_DispatchSequence(VkComp_Compute *self, PyObject *args,
                                          PyObject *kwds) {
  static char *kwlist[] = {"sequence",   "copy_src",      "copy_dst",
                           "copy_slice", "present_image", "timestamps",
                           NULL};
  PyObject *sequence_list;
  PyObject *copy_src_obj = Py_None;
  PyObject *copy_dst_obj = Py_None;
  int copy_slice = 0;
  PyObject *present_obj = Py_None;
  int enable_timestamps = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|OOiOp", kwlist, &PyList_Type,
                                   &sequence_list, &copy_src_obj, &copy_dst_obj,
                                   &copy_slice, &present_obj,
                                   &enable_timestamps))
    return NULL;

  Py_ssize_t num_items = PyList_Size(sequence_list);

  /* Validate copy resources */
  VkComp_Resource *src_buf = NULL, *dst_img = NULL;
  if (copy_src_obj != Py_None && copy_dst_obj != Py_None) {
    if (!PyObject_TypeCheck(copy_src_obj, &VkComp_Resource_Type) ||
        !PyObject_TypeCheck(copy_dst_obj, &VkComp_Resource_Type)) {
      PyErr_SetString(PyExc_TypeError,
                      "copy_src and copy_dst must be Resource objects");
      return NULL;
    }
    src_buf = (VkComp_Resource *)copy_src_obj;
    dst_img = (VkComp_Resource *)copy_dst_obj;
    if (!VkComp_Resource_IsBuffer(src_buf) ||
        !VkComp_Resource_IsTexture(dst_img)) {
      PyErr_SetString(PyExc_TypeError,
                      "copy_src must be a Buffer, copy_dst a Texture");
      return NULL;
    }
    if (copy_slice < 0 || (uint32_t)copy_slice >= dst_img->slices) {
      PyErr_Format(PyExc_ValueError, "copy_slice %d out of range [0, %u)",
                   copy_slice, dst_img->slices);
      return NULL;
    }
  }

  VkComp_Resource *present_image = NULL;
  if (present_obj != Py_None) {
    if (!PyObject_TypeCheck(present_obj, &VkComp_Resource_Type)) {
      PyErr_SetString(PyExc_TypeError, "present_image must be a Texture");
      return NULL;
    }
    present_image = (VkComp_Resource *)present_obj;
    if (!VkComp_Resource_IsTexture(present_image)) {
      PyErr_SetString(PyExc_TypeError, "present_image must be a Texture");
      return NULL;
    }
  }

  /* Find the device from the first compute object or resources */
  VkComp_Device *dev = NULL;
  if (num_items > 0) {
    PyObject *first = PyList_GetItem(sequence_list, 0);
    if (!PyTuple_Check(first) || PyTuple_Size(first) != 5) {
      PyErr_SetString(
          PyExc_TypeError,
          "Each sequence item must be a 5‑tuple (compute, x, y, z, push)");
      return NULL;
    }
    PyObject *comp_obj = PyTuple_GetItem(first, 0);
    if (!PyObject_TypeCheck(comp_obj, &VkComp_Compute_Type)) {
      PyErr_SetString(PyExc_TypeError,
                      "First element must be a Compute object");
      return NULL;
    }
    dev = ((VkComp_Compute *)comp_obj)->device;
  } else if (src_buf) {
    dev = src_buf->device;
  } else if (present_image) {
    dev = present_image->device;
  } else {
    PyErr_SetString(PyExc_ValueError,
                    "No compute objects or resources provided");
    return NULL;
  }

  dev = VkComp_Device_GetActive(dev);
  if (!dev)
    return NULL;

  /* Parse dispatch items */
  typedef struct {
    VkComp_Compute *comp;
    uint32_t x, y, z;
    PyObject *push_obj;
  } DispatchItem;
  DispatchItem *items = PyMem_Malloc(num_items * sizeof(DispatchItem));
  if (!items)
    return PyErr_NoMemory();

  for (Py_ssize_t i = 0; i < num_items; i++) {
    PyObject *tuple = PyList_GetItem(sequence_list, i);
    PyObject *comp_obj;
    unsigned int x, y, z;
    PyObject *push_obj;
    if (!PyArg_ParseTuple(tuple, "OIII|O", &comp_obj, &x, &y, &z, &push_obj)) {
      PyMem_Free(items);
      return NULL;
    }
    if (!PyObject_TypeCheck(comp_obj, &VkComp_Compute_Type)) {
      PyMem_Free(items);
      PyErr_SetString(PyExc_TypeError,
                      "First element must be a Compute object");
      return NULL;
    }
    VkComp_Compute *comp = (VkComp_Compute *)comp_obj;
    if (comp->device != dev) {
      PyMem_Free(items);
      PyErr_SetString(PyExc_ValueError,
                      "All compute objects must belong to the same device");
      return NULL;
    }
    items[i] = (DispatchItem){comp, x, y, z, push_obj};
  }

  /* Timestamp setup */
  bool use_ts = enable_timestamps && dev->supports_timestamps;
  uint32_t ts_idx = 0, total_ts = 0;
  if (use_ts) {
    total_ts = 1 + 2 + (uint32_t)num_items * 2 + (present_image ? 2 : 0) + 1;
    if (dev->timestamp_count < total_ts)
      use_ts = false;
  }

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    PyMem_Free(items);
    PyErr_Format(VkComp_ComputeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  if (use_ts) {
    vkCmdResetQueryPool(cmd, dev->timestamp_pool, 0, total_ts);
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                        dev->timestamp_pool, ts_idx++);
  }

  /* Pre‑copy (buffer → texture) */
  if (src_buf && dst_img) {
    uint32_t copy_before = ts_idx, copy_after = ts_idx + 1;
    if (use_ts) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                          dev->timestamp_pool, copy_before);
      ts_idx += 2;
    }

    VkImageMemoryBarrier barrier = {
        .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
        .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
        .dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT,
        .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
        .newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
        .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .image = dst_img->image,
        .subresourceRange =
            {
                .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                .baseMipLevel = 0,
                .levelCount = 1,
                .baseArrayLayer = (uint32_t)copy_slice,
                .layerCount = 1,
            },
    };
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                         &barrier);

    VkBufferImageCopy region = {
        .bufferOffset = 0,
        .imageSubresource =
            {
                .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                .mipLevel = 0,
                .baseArrayLayer = (uint32_t)copy_slice,
                .layerCount = 1,
            },
        .imageExtent = dst_img->image_extent,
    };
    vkCmdCopyBufferToImage(cmd, src_buf->buffer, dst_img->image,
                           VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

    barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.dstAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
    barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                         NULL, 1, &barrier);

    if (use_ts) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                          dev->timestamp_pool, copy_after);
    }
  } else if (use_ts) {
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                        dev->timestamp_pool, ts_idx++);
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                        dev->timestamp_pool, ts_idx++);
  }

  /* Dispatch sequence */
  for (Py_ssize_t i = 0; i < num_items; i++) {
    DispatchItem *item = &items[i];
    uint32_t before = ts_idx, after = ts_idx + 1;
    if (use_ts) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                          dev->timestamp_pool, before);
      ts_idx += 2;
    }

    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                      item->comp->pipeline);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                            item->comp->pipeline_layout, 0, 1,
                            &item->comp->descriptor_set, 0, NULL);

    if (item->push_obj != Py_None) {
      Py_buffer view;
      if (PyObject_GetBuffer(item->push_obj, &view, PyBUF_SIMPLE) < 0) {
        vkEndCommandBuffer(cmd);
        VkComp_Device_FreeCmd(dev, cmd);
        PyMem_Free(items);
        return NULL;
      }
      if (view.len > 0) {
        vkCmdPushConstants(cmd, item->comp->pipeline_layout,
                           VK_SHADER_STAGE_COMPUTE_BIT, 0, (uint32_t)view.len,
                           view.buf);
      }
      PyBuffer_Release(&view);
    }

    vkCmdDispatch(cmd, item->x, item->y, item->z);

    if (use_ts) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                          dev->timestamp_pool, after);
    }

    if (i < num_items - 1 || present_image) {
      VkMemoryBarrier barrier = {
          .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER,
          .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
          .dstAccessMask = VK_ACCESS_SHADER_READ_BIT,
      };
      vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                           VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 1, &barrier,
                           0, NULL, 0, NULL);
    }
  }

  /* Transition present image */
  if (present_image) {
    uint32_t before = ts_idx, after = ts_idx + 1;
    if (use_ts) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                          dev->timestamp_pool, before);
      ts_idx += 2;
    }

    VkImageMemoryBarrier barrier = {
        .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
        .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
        .dstAccessMask = VK_ACCESS_MEMORY_READ_BIT,
        .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
        .newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
        .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .image = present_image->image,
        .subresourceRange =
            {
                .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                .baseMipLevel = 0,
                .levelCount = 1,
                .baseArrayLayer = 0,
                .layerCount = 1,
            },
    };
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0, 0, NULL, 0,
                         NULL, 1, &barrier);

    if (use_ts) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                          dev->timestamp_pool, after);
    }
  }

  if (use_ts) {
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                        dev->timestamp_pool, ts_idx++);
  }

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, self->dispatch_fence);
  VkComp_Device_FreeCmd(dev, cmd);
  PyMem_Free(items);

  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_ComputeError, "Sequence submission failed: %d", res);
    return NULL;
  }

  if (use_ts) {
    uint64_t *ts_data = PyMem_Malloc(total_ts * sizeof(uint64_t));
    if (!ts_data)
      return PyErr_NoMemory();
    vkGetQueryPoolResults(dev->device, dev->timestamp_pool, 0, total_ts,
                          total_ts * sizeof(uint64_t), ts_data,
                          sizeof(uint64_t),
                          VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT);
    PyObject *ts_list = PyList_New(total_ts);
    for (uint32_t i = 0; i < total_ts; i++) {
      PyList_SetItem(
          ts_list, i,
          PyFloat_FromDouble((double)ts_data[i] * dev->timestamp_period));
    }
    PyMem_Free(ts_data);
    PyObject *result = PyTuple_New(2);
    Py_INCREF(Py_None);
    PyTuple_SetItem(result, 0, Py_None);
    PyTuple_SetItem(result, 1, ts_list);
    return result;
  }

  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   dispatch_tiles(tiles, tile_width, tile_height)
   tiles: list of (tx, ty, push_bytes)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_DispatchTiles(VkComp_Compute *self, PyObject *args) {
  PyObject *tiles_list;
  unsigned int tile_width, tile_height;
  if (!PyArg_ParseTuple(args, "O!II", &PyList_Type, &tiles_list, &tile_width,
                        &tile_height))
    return NULL;

  Py_ssize_t num_tiles = PyList_Size(tiles_list);
  if (num_tiles == 0)
    Py_RETURN_NONE;

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  VkCommandBuffer cmd;
  VkResult res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_ComputeError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  uint32_t groups_x = (tile_width + 7) / 8;
  uint32_t groups_y = (tile_height + 7) / 8;

  for (Py_ssize_t i = 0; i < num_tiles; i++) {
    PyObject *tuple = PyList_GetItem(tiles_list, i);
    unsigned int tx, ty;
    PyObject *push_obj;
    if (!PyArg_ParseTuple(tuple, "IIO", &tx, &ty, &push_obj)) {
      vkEndCommandBuffer(cmd);
      VkComp_Device_FreeCmd(dev, cmd);
      return NULL;
    }

    Py_buffer view;
    if (PyObject_GetBuffer(push_obj, &view, PyBUF_SIMPLE) < 0) {
      vkEndCommandBuffer(cmd);
      VkComp_Device_FreeCmd(dev, cmd);
      return NULL;
    }

    if (view.len > 0) {
      if (view.len > self->push_constant_size || (view.len % 4) != 0) {
        PyBuffer_Release(&view);
        vkEndCommandBuffer(cmd);
        VkComp_Device_FreeCmd(dev, cmd);
        PyErr_Format(PyExc_ValueError,
                     "Invalid push constant size %zd (max %u, multiple of 4)",
                     view.len, self->push_constant_size);
        return NULL;
      }
      vkCmdPushConstants(cmd, self->pipeline_layout,
                         VK_SHADER_STAGE_COMPUTE_BIT, 0, (uint32_t)view.len,
                         view.buf);
    }
    PyBuffer_Release(&view);

    vkCmdDispatch(cmd, groups_x, groups_y, 1);

    if (i < num_tiles - 1) {
      VkMemoryBarrier barrier = {
          .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER,
          .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
          .dstAccessMask = VK_ACCESS_SHADER_READ_BIT,
      };
      vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                           VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 1, &barrier,
                           0, NULL, 0, NULL);
    }
  }

  vkEndCommandBuffer(cmd);

  res = vkcomp_submit_and_wait(dev, cmd, self->dispatch_fence);
  VkComp_Device_FreeCmd(dev, cmd);

  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_ComputeError, "Tiled dispatch submission failed: %d",
                 res);
    return NULL;
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   bind_cbv(index, resource) – bindless mode only
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_BindCBV(VkComp_Compute *self, PyObject *args) {
  unsigned int index;
  PyObject *res_obj;
  if (!PyArg_ParseTuple(args, "IO", &index, &res_obj))
    return NULL;

  if (self->bindless_max == 0) {
    PyErr_SetString(PyExc_ValueError,
                    "Compute pipeline is not in bindless mode");
    return NULL;
  }
  if (!PyObject_TypeCheck(res_obj, &VkComp_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Resource object");
    return NULL;
  }
  VkComp_Resource *res = (VkComp_Resource *)res_obj;
  if (!VkComp_Resource_IsBuffer(res)) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
    return NULL;
  }
  if (index >= self->bindless_max) {
    PyErr_Format(PyExc_ValueError, "Binding index %u exceeds max %u", index,
                 self->bindless_max - 1);
    return NULL;
  }

  VkWriteDescriptorSet write = {
      .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
      .dstSet = self->descriptor_set,
      .dstBinding = index,
      .descriptorCount = 1,
      .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
      .pBufferInfo = &res->descriptor_buffer_info,
  };
  vkUpdateDescriptorSets(self->device->device, 1, &write, 0, NULL);

  Py_INCREF(res_obj);
  PyList_SetItem(self->cbv_list, index, res_obj);
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   bind_srv(index, resource) – bindless mode only
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_BindSRV(VkComp_Compute *self, PyObject *args) {
  unsigned int index;
  PyObject *res_obj;
  if (!PyArg_ParseTuple(args, "IO", &index, &res_obj))
    return NULL;

  if (self->bindless_max == 0) {
    PyErr_SetString(PyExc_ValueError,
                    "Compute pipeline is not in bindless mode");
    return NULL;
  }
  if (!PyObject_TypeCheck(res_obj, &VkComp_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Resource object");
    return NULL;
  }
  VkComp_Resource *res = (VkComp_Resource *)res_obj;
  if (index >= self->bindless_max) {
    PyErr_Format(PyExc_ValueError, "Binding index %u exceeds max %u", index,
                 self->bindless_max - 1);
    return NULL;
  }

  VkDescriptorType dtype;
  if (res->buffer) {
    dtype = res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                             : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
  } else {
    dtype = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
  }

  VkWriteDescriptorSet write = {
      .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
      .dstSet = self->descriptor_set,
      .dstBinding = 1024 + index,
      .descriptorCount = 1,
      .descriptorType = dtype,
      .pBufferInfo = (res->buffer && !res->buffer_view)
                         ? &res->descriptor_buffer_info
                         : NULL,
      .pTexelBufferView = res->buffer_view ? &res->buffer_view : NULL,
      .pImageInfo = !res->buffer ? &res->descriptor_image_info : NULL,
  };
  vkUpdateDescriptorSets(self->device->device, 1, &write, 0, NULL);

  Py_INCREF(res_obj);
  PyList_SetItem(self->srv_list, index, res_obj);
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   bind_uav(index, resource) – bindless mode only
   ------------------------------------------------------------------------- */
PyObject *VkComp_Compute_BindUAV(VkComp_Compute *self, PyObject *args) {
  unsigned int index;
  PyObject *res_obj;
  if (!PyArg_ParseTuple(args, "IO", &index, &res_obj))
    return NULL;

  if (self->bindless_max == 0) {
    PyErr_SetString(PyExc_ValueError,
                    "Compute pipeline is not in bindless mode");
    return NULL;
  }
  if (!PyObject_TypeCheck(res_obj, &VkComp_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Resource object");
    return NULL;
  }
  VkComp_Resource *res = (VkComp_Resource *)res_obj;
  if (index >= self->bindless_max) {
    PyErr_Format(PyExc_ValueError, "Binding index %u exceeds max %u", index,
                 self->bindless_max - 1);
    return NULL;
  }

  VkDescriptorType dtype;
  if (res->buffer) {
    dtype = res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                             : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
  } else {
    dtype = VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
  }

  VkWriteDescriptorSet write = {
      .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
      .dstSet = self->descriptor_set,
      .dstBinding = 2048 + index,
      .descriptorCount = 1,
      .descriptorType = dtype,
      .pBufferInfo = (res->buffer && !res->buffer_view)
                         ? &res->descriptor_buffer_info
                         : NULL,
      .pTexelBufferView = res->buffer_view ? &res->buffer_view : NULL,
      .pImageInfo = !res->buffer ? &res->descriptor_image_info : NULL,
  };
  vkUpdateDescriptorSets(self->device->device, 1, &write, 0, NULL);

  Py_INCREF(res_obj);
  PyList_SetItem(self->uav_list, index, res_obj);
  Py_RETURN_NONE;
}