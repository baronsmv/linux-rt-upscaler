#include "vk_device.h"
#include "vk_compute.h"
#include "vk_utils.h"
#include <unordered_map>
#include <vector>
#include <cstring>

// Forward declare resource type for checking
extern PyTypeObject vk_Resource_Type;
extern PyTypeObject vk_Sampler_Type;

/* ----------------------------------------------------------------------------
   Compute deallocator
   ------------------------------------------------------------------------- */
void vk_Compute_dealloc(vk_Compute *self) {
    if (self->py_device) {
        VkDevice dev = self->py_device->device;
        if (self->pipeline) vkDestroyPipeline(dev, self->pipeline, nullptr);
        if (self->pipeline_layout) vkDestroyPipelineLayout(dev, self->pipeline_layout, nullptr);
        if (self->descriptor_pool) vkDestroyDescriptorPool(dev, self->descriptor_pool, nullptr);
        if (self->descriptor_set_layout) vkDestroyDescriptorSetLayout(dev, self->descriptor_set_layout, nullptr);
        if (self->shader_module) vkDestroyShaderModule(dev, self->shader_module, nullptr);
        if (self->dispatch_fence) vkDestroyFence(dev, self->dispatch_fence, nullptr);
        Py_DECREF(self->py_device);
    }
    Py_XDECREF(self->py_cbv_list);
    Py_XDECREF(self->py_srv_list);
    Py_XDECREF(self->py_uav_list);
    Py_XDECREF(self->py_samplers_list);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/* ----------------------------------------------------------------------------
   Helper: create descriptor set layout and pipeline layout
   ------------------------------------------------------------------------- */
static bool create_descriptor_set_layout(vk_Device *dev,
                                         const std::vector<vk_Resource *> &cbv,
                                         const std::vector<vk_Resource *> &srv,
                                         const std::vector<vk_Resource *> &uav,
                                         const std::vector<vk_Sampler *> &samplers,
                                         uint32_t bindless,
                                         VkDescriptorSetLayout *out_layout) {
    std::vector<VkDescriptorSetLayoutBinding> bindings;
    std::vector<VkDescriptorBindingFlags> binding_flags;
    bool use_update_after_bind = (bindless > 0) && dev->supports_bindless;

    auto add_binding = [&](uint32_t binding, VkDescriptorType type, uint32_t count) {
        VkDescriptorSetLayoutBinding lb = {};
        lb.binding = binding;
        lb.descriptorType = type;
        lb.descriptorCount = count;
        lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
        bindings.push_back(lb);
        if (use_update_after_bind) {
            binding_flags.push_back(VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT |
                                    VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT);
        }
    };

    if (bindless == 0) {
        // Non‑bindless: each resource gets its own binding
        uint32_t idx = 0;
        for (size_t i = 0; i < cbv.size(); ++i)
            add_binding(idx++, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1);
        idx = 1024;
        for (size_t i = 0; i < srv.size(); ++i) {
            vk_Resource *res = srv[i];
            VkDescriptorType type;
            if (res->buffer) {
                type = res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
            } else {
                type = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
            }
            add_binding(idx++, type, 1);
        }
        idx = 2048;
        for (size_t i = 0; i < uav.size(); ++i) {
            vk_Resource *res = uav[i];
            VkDescriptorType type;
            if (res->buffer) {
                type = res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
            } else {
                type = VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
            }
            add_binding(idx++, type, 1);
        }
        idx = 3072;
        for (size_t i = 0; i < samplers.size(); ++i) {
            add_binding(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, 1);
        }
    } else {
        // Bindless: three large arrays (CBV, SRV, UAV)
        if (dev->supports_bindless) {
            add_binding(0, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, bindless);
            add_binding(1024, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, bindless);
            add_binding(2048, VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, bindless);
            // Samplers still separate
            uint32_t idx = 3072;
            for (size_t i = 0; i < samplers.size(); ++i)
                add_binding(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, 1);
        } else {
            PyErr_SetString(PyExc_ValueError, "Bindless not supported on this device");
            return false;
        }
    }

    VkDescriptorSetLayoutCreateInfo dsl_info = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO };
    dsl_info.bindingCount = static_cast<uint32_t>(bindings.size());
    dsl_info.pBindings = bindings.data();

    VkDescriptorSetLayoutBindingFlagsCreateInfo flags_info = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_BINDING_FLAGS_CREATE_INFO };
    if (use_update_after_bind) {
        flags_info.bindingCount = static_cast<uint32_t>(binding_flags.size());
        flags_info.pBindingFlags = binding_flags.data();
        dsl_info.pNext = &flags_info;
        dsl_info.flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT;
    }

    return vkCreateDescriptorSetLayout(dev->device, &dsl_info, nullptr, out_layout) == VK_SUCCESS;
}

/* ----------------------------------------------------------------------------
   Helper: create descriptor pool and allocate descriptor set
   ------------------------------------------------------------------------- */
static bool create_descriptor_pool_and_set(vk_Device *dev,
                                           const std::vector<vk_Resource *> &cbv,
                                           const std::vector<vk_Resource *> &srv,
                                           const std::vector<vk_Resource *> &uav,
                                           const std::vector<vk_Sampler *> &samplers,
                                           uint32_t bindless,
                                           VkDescriptorSetLayout layout,
                                           VkDescriptorPool *out_pool,
                                           VkDescriptorSet *out_set) {
    std::unordered_map<VkDescriptorType, uint32_t> type_counts;
    auto count_type = [&](VkDescriptorType type, uint32_t count = 1) {
        type_counts[type] += count;
    };

    if (bindless == 0) {
        for (size_t i = 0; i < cbv.size(); ++i)
            count_type(VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER);
        for (vk_Resource *res : srv) {
            VkDescriptorType type = res->buffer
                ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER)
                : VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
            count_type(type);
        }
        for (vk_Resource *res : uav) {
            VkDescriptorType type = res->buffer
                ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER)
                : VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
            count_type(type);
        }
        for (size_t i = 0; i < samplers.size(); ++i)
            count_type(VK_DESCRIPTOR_TYPE_SAMPLER);
    } else {
        if (dev->supports_bindless) {
            count_type(VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, bindless);
            count_type(VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, bindless);
            count_type(VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, bindless);
            for (size_t i = 0; i < samplers.size(); ++i)
                count_type(VK_DESCRIPTOR_TYPE_SAMPLER);
        }
    }

    std::vector<VkDescriptorPoolSize> pool_sizes;
    for (const auto &kv : type_counts) {
        VkDescriptorPoolSize ps = { kv.first, kv.second };
        pool_sizes.push_back(ps);
    }

    VkDescriptorPoolCreateInfo dp_info = { VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO };
    dp_info.maxSets = 1;
    dp_info.poolSizeCount = static_cast<uint32_t>(pool_sizes.size());
    dp_info.pPoolSizes = pool_sizes.data();
    if (bindless > 0 && dev->supports_bindless)
        dp_info.flags = VK_DESCRIPTOR_POOL_CREATE_UPDATE_AFTER_BIND_BIT;

    if (vkCreateDescriptorPool(dev->device, &dp_info, nullptr, out_pool) != VK_SUCCESS)
        return false;

    VkDescriptorSetAllocateInfo alloc_info = { VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO };
    alloc_info.descriptorPool = *out_pool;
    alloc_info.descriptorSetCount = 1;
    alloc_info.pSetLayouts = &layout;

    return vkAllocateDescriptorSets(dev->device, &alloc_info, out_set) == VK_SUCCESS;
}

/* ----------------------------------------------------------------------------
   Helper: write descriptors into the set
   ------------------------------------------------------------------------- */
static void write_descriptors(vk_Device *dev,
                              VkDescriptorSet set,
                              const std::vector<vk_Resource *> &cbv,
                              const std::vector<vk_Resource *> &srv,
                              const std::vector<vk_Resource *> &uav,
                              const std::vector<vk_Sampler *> &samplers,
                              uint32_t bindless) {
    std::vector<VkWriteDescriptorSet> writes;
    std::vector<VkDescriptorBufferInfo> buffer_infos;
    std::vector<VkDescriptorImageInfo> image_infos;
    std::vector<VkBufferView> buffer_views;

    auto add_write = [&](uint32_t binding, VkDescriptorType type,
                         VkDescriptorBufferInfo *buf_info = nullptr,
                         VkDescriptorImageInfo *img_info = nullptr,
                         VkBufferView *buf_view = nullptr) {
        VkWriteDescriptorSet w = { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET };
        w.dstSet = set;
        w.dstBinding = binding;
        w.descriptorCount = 1;
        w.descriptorType = type;
        if (buf_info) w.pBufferInfo = buf_info;
        if (img_info) w.pImageInfo = img_info;
        if (buf_view) w.pTexelBufferView = buf_view;
        writes.push_back(w);
    };

    if (bindless == 0) {
        uint32_t idx = 0;
        for (vk_Resource *res : cbv)
            add_write(idx++, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, &res->descriptor_buffer_info);
        idx = 1024;
        for (vk_Resource *res : srv) {
            if (res->buffer) {
                if (res->buffer_view) {
                    add_write(idx, VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER, nullptr, nullptr, &res->buffer_view);
                } else {
                    add_write(idx, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, &res->descriptor_buffer_info);
                }
            } else {
                add_write(idx, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, nullptr, &res->descriptor_image_info);
            }
            ++idx;
        }
        idx = 2048;
        for (vk_Resource *res : uav) {
            if (res->buffer) {
                if (res->buffer_view) {
                    add_write(idx, VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER, nullptr, nullptr, &res->buffer_view);
                } else {
                    add_write(idx, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, &res->descriptor_buffer_info);
                }
            } else {
                add_write(idx, VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, nullptr, &res->descriptor_image_info);
            }
            ++idx;
        }
        idx = 3072;
        for (vk_Sampler *samp : samplers) {
            add_write(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, nullptr, &samp->descriptor_image_info);
        }
    } else {
        // Bindless: we need to write arrays
        // For simplicity, we'll write one element at a time using array index
        // (Vulkan allows writing individual elements of an array binding)
        for (size_t i = 0; i < cbv.size(); ++i) {
            add_write(i, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, &cbv[i]->descriptor_buffer_info);
        }
        for (size_t i = 0; i < srv.size(); ++i) {
            vk_Resource *res = srv[i];
            if (res->image) {
                add_write(1024 + i, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, nullptr, &res->descriptor_image_info);
            } else {
                // In bindless, we only support images for SRV; buffers would need separate array.
                // For simplicity, we assume images only.
            }
        }
        for (size_t i = 0; i < uav.size(); ++i) {
            vk_Resource *res = uav[i];
            if (res->image) {
                add_write(2048 + i, VK_DESCRIPTOR_TYPE_STORAGE_IMAGE, nullptr, &res->descriptor_image_info);
            }
        }
        uint32_t idx = 3072;
        for (vk_Sampler *samp : samplers) {
            add_write(idx++, VK_DESCRIPTOR_TYPE_SAMPLER, nullptr, &samp->descriptor_image_info);
        }
    }

    vkUpdateDescriptorSets(dev->device, static_cast<uint32_t>(writes.size()), writes.data(), 0, nullptr);
}

/* ----------------------------------------------------------------------------
   vk_Device_create_compute_impl (called from vk_Device_create_compute)
   ------------------------------------------------------------------------- */
PyObject *vk_Device_create_compute_impl(vk_Device *self, PyObject *args, PyObject *kwds) {
    static const char *kwlist[] = {"shader", "cbv", "srv", "uav", "samplers", "push_size", "bindless", nullptr};
    Py_buffer shader_view;
    PyObject *cbv_list = nullptr, *srv_list = nullptr, *uav_list = nullptr, *samplers_list = nullptr;
    uint32_t push_size = 0;
    uint32_t bindless = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "y*|OOOOII", (char **)kwlist,
                                     &shader_view, &cbv_list, &srv_list, &uav_list,
                                     &samplers_list, &push_size, &bindless))
        return nullptr;

    vk_Device *dev = vk_Device_get_initialized(self);
    if (!dev) {
        PyBuffer_Release(&shader_view);
        return nullptr;
    }

    // Collect resource lists
    std::vector<vk_Resource *> cbv, srv, uav;
    std::vector<vk_Sampler *> samplers;
    if (!vk_check_descriptor_lists(&vk_Resource_Type, cbv_list, cbv, srv_list, srv, uav_list, uav,
                                   &vk_Sampler_Type, samplers_list, samplers)) {
        PyBuffer_Release(&shader_view);
        return nullptr;
    }

    // Check bindless support
    if (bindless > 0 && !dev->supports_bindless) {
        PyBuffer_Release(&shader_view);
        PyErr_SetString(PyExc_ValueError, "Bindless not supported on this device");
        return nullptr;
    }

    // SPIR‑V patching for BGRA UAVs on Intel (if needed)
    const uint32_t *spirv_code = static_cast<const uint32_t *>(shader_view.buf);
    size_t spirv_size = shader_view.len;
    uint32_t *patched_code = nullptr;

    if (!dev->features.shaderStorageImageReadWithoutFormat) {
        uint32_t binding = 2048;
        for (vk_Resource *res : uav) {
            if (res->image && (res->format == VK_FORMAT_B8G8R8A8_UNORM || res->format == VK_FORMAT_B8G8R8A8_SRGB)) {
                patched_code = vk_spirv_patch_nonreadable_uav(spirv_code, spirv_size, binding);
                if (patched_code) {
                    spirv_code = patched_code;
                    spirv_size += 12; // 3 words added
                    break; // only patch once (first UAV)
                }
            }
            ++binding;
        }
    }

    // Extract entry point
    const char *entry_point = vk_spirv_get_entry_point(spirv_code, spirv_size);
    if (!entry_point) {
        if (patched_code) PyMem_Free(patched_code);
        PyBuffer_Release(&shader_view);
        PyErr_SetString(PyExc_ValueError, "Invalid SPIR‑V or no compute entry point");
        return nullptr;
    }

    // Create shader module
    VkShaderModuleCreateInfo sm_info = { VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO };
    sm_info.codeSize = spirv_size;
    sm_info.pCode = spirv_code;
    VkShaderModule shader_module;
    VkResult res = vkCreateShaderModule(dev->device, &sm_info, nullptr, &shader_module);
    if (patched_code) PyMem_Free(patched_code);
    PyBuffer_Release(&shader_view);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_ComputeError, "Failed to create shader module (error %d)", res);
        return nullptr;
    }

    // Create descriptor set layout
    VkDescriptorSetLayout dsl;
    if (!create_descriptor_set_layout(dev, cbv, srv, uav, samplers, bindless, &dsl)) {
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        PyErr_SetString(vk_ComputeError, "Failed to create descriptor set layout");
        return nullptr;
    }

    // Create pipeline layout
    VkPipelineLayoutCreateInfo pl_info = { VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO };
    pl_info.setLayoutCount = 1;
    pl_info.pSetLayouts = &dsl;
    VkPushConstantRange pc_range = { VK_SHADER_STAGE_COMPUTE_BIT, 0, push_size };
    if (push_size > 0) {
        pl_info.pushConstantRangeCount = 1;
        pl_info.pPushConstantRanges = &pc_range;
    }
    VkPipelineLayout pipeline_layout;
    if (vkCreatePipelineLayout(dev->device, &pl_info, nullptr, &pipeline_layout) != VK_SUCCESS) {
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        PyErr_SetString(vk_ComputeError, "Failed to create pipeline layout");
        return nullptr;
    }

    // Create compute pipeline
    VkComputePipelineCreateInfo cp_info = { VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO };
    cp_info.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    cp_info.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT;
    cp_info.stage.module = shader_module;
    cp_info.stage.pName = entry_point;
    cp_info.layout = pipeline_layout;
    VkPipeline pipeline;
    res = vkCreateComputePipelines(dev->device, dev->pipeline_cache, 1, &cp_info, nullptr, &pipeline);
    if (res != VK_SUCCESS) {
        vkDestroyPipelineLayout(dev->device, pipeline_layout, nullptr);
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        PyErr_Format(vk_ComputeError, "Failed to create compute pipeline (error %d)", res);
        return nullptr;
    }

    // Create descriptor pool and allocate set
    VkDescriptorPool descriptor_pool;
    VkDescriptorSet descriptor_set;
    if (!create_descriptor_pool_and_set(dev, cbv, srv, uav, samplers, bindless, dsl,
                                        &descriptor_pool, &descriptor_set)) {
        vkDestroyPipeline(dev->device, pipeline, nullptr);
        vkDestroyPipelineLayout(dev->device, pipeline_layout, nullptr);
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        PyErr_SetString(vk_ComputeError, "Failed to create descriptor pool/set");
        return nullptr;
    }

    // Write descriptors
    write_descriptors(dev, descriptor_set, cbv, srv, uav, samplers, bindless);

    // Create dispatch fence
    VkFenceCreateInfo finfo = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    VkFence dispatch_fence;
    if (vkCreateFence(dev->device, &finfo, nullptr, &dispatch_fence) != VK_SUCCESS) {
        vkDestroyDescriptorPool(dev->device, descriptor_pool, nullptr);
        vkDestroyPipeline(dev->device, pipeline, nullptr);
        vkDestroyPipelineLayout(dev->device, pipeline_layout, nullptr);
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        PyErr_SetString(vk_ComputeError, "Failed to create dispatch fence");
        return nullptr;
    }

    // Allocate Compute object
    vk_Compute *comp = PyObject_New(vk_Compute, &vk_Compute_Type);
    if (!comp) {
        vkDestroyFence(dev->device, dispatch_fence, nullptr);
        vkDestroyDescriptorPool(dev->device, descriptor_pool, nullptr);
        vkDestroyPipeline(dev->device, pipeline, nullptr);
        vkDestroyPipelineLayout(dev->device, pipeline_layout, nullptr);
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        return PyErr_NoMemory();
    }
    VK_CLEAR_OBJECT(comp);
    comp->py_device = dev;
    Py_INCREF(dev);
    comp->shader_module = shader_module;
    comp->pipeline_layout = pipeline_layout;
    comp->descriptor_set_layout = dsl;
    comp->descriptor_pool = descriptor_pool;
    comp->descriptor_set = descriptor_set;
    comp->pipeline = pipeline;
    comp->dispatch_fence = dispatch_fence;
    comp->push_constant_size = push_size;
    comp->bindless = bindless;

    // Initialize Python lists for bindless tracking
    size_t num_cbv = bindless ? bindless : cbv.size();
    size_t num_srv = bindless ? bindless : srv.size();
    size_t num_uav = bindless ? bindless : uav.size();
    comp->py_cbv_list = PyList_New(num_cbv);
    comp->py_srv_list = PyList_New(num_srv);
    comp->py_uav_list = PyList_New(num_uav);
    comp->py_samplers_list = PyList_New(0);
    for (size_t i = 0; i < num_cbv; ++i) {
        PyObject *item = (i < cbv.size()) ? reinterpret_cast<PyObject *>(cbv[i]) : Py_None;
        Py_INCREF(item);
        PyList_SetItem(comp->py_cbv_list, i, item);
    }
    for (size_t i = 0; i < num_srv; ++i) {
        PyObject *item = (i < srv.size()) ? reinterpret_cast<PyObject *>(srv[i]) : Py_None;
        Py_INCREF(item);
        PyList_SetItem(comp->py_srv_list, i, item);
    }
    for (size_t i = 0; i < num_uav; ++i) {
        PyObject *item = (i < uav.size()) ? reinterpret_cast<PyObject *>(uav[i]) : Py_None;
        Py_INCREF(item);
        PyList_SetItem(comp->py_uav_list, i, item);
    }
    for (vk_Sampler *samp : samplers) {
        PyList_Append(comp->py_samplers_list, reinterpret_cast<PyObject *>(samp));
    }

    return reinterpret_cast<PyObject *>(comp);
}

/* ----------------------------------------------------------------------------
   Dispatch methods
   ------------------------------------------------------------------------- */
static VkResult submit_and_wait(vk_Device *dev, VkCommandBuffer cmd, VkFence fence) {
    VkSubmitInfo submit = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
    submit.commandBufferCount = 1;
    submit.pCommandBuffers = &cmd;
    VkResult res = vkQueueSubmit(dev->queue, 1, &submit, fence);
    if (res != VK_SUCCESS) return res;
    if (fence) {
        Py_BEGIN_ALLOW_THREADS;
        vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
        vkResetFences(dev->device, 1, &fence);
        Py_END_ALLOW_THREADS;
    }
    return VK_SUCCESS;
}

PyObject *vk_Compute_dispatch(vk_Compute *self, PyObject *args) {
    uint32_t x, y, z;
    Py_buffer push = {0};
    if (!PyArg_ParseTuple(args, "III|y*", &x, &y, &z, &push))
        return nullptr;

    if (push.len > 0) {
        if (push.len > self->push_constant_size || (push.len % 4) != 0) {
            PyBuffer_Release(&push);
            PyErr_Format(PyExc_ValueError, "Invalid push constant size");
            return nullptr;
        }
    }

    vk_Device *dev = self->py_device;
    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        if (push.buf) PyBuffer_Release(&push);
        PyErr_SetString(vk_ComputeError, "Failed to allocate command buffer");
        return nullptr;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline_layout,
                            0, 1, &self->descriptor_set, 0, nullptr);
    if (push.len > 0) {
        vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                           0, static_cast<uint32_t>(push.len), push.buf);
    }
    vkCmdDispatch(cmd, x, y, z);
    vkEndCommandBuffer(cmd);

    if (push.buf) PyBuffer_Release(&push);

    VkResult res = submit_and_wait(dev, cmd, self->dispatch_fence);
    vk_free_temp_cmd(dev, cmd);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Dispatch submission failed (error %d)", res);
        return nullptr;
    }
    Py_RETURN_NONE;
}

PyObject *vk_Compute_dispatch_indirect(vk_Compute *self, PyObject *args) {
    PyObject *buffer_obj;
    uint32_t offset;
    Py_buffer push = {0};
    if (!PyArg_ParseTuple(args, "OI|y*", &buffer_obj, &offset, &push))
        return nullptr;

    if (!PyObject_TypeCheck(buffer_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Expected a Buffer resource");
        return nullptr;
    }
    vk_Resource *buf = reinterpret_cast<vk_Resource *>(buffer_obj);
    if (!buf->buffer) {
        PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
        return nullptr;
    }

    vk_Device *dev = self->py_device;
    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        if (push.buf) PyBuffer_Release(&push);
        PyErr_SetString(vk_ComputeError, "Failed to allocate command buffer");
        return nullptr;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline_layout,
                            0, 1, &self->descriptor_set, 0, nullptr);
    if (push.len > 0) {
        vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                           0, static_cast<uint32_t>(push.len), push.buf);
    }
    vkCmdDispatchIndirect(cmd, buf->buffer, offset);
    vkEndCommandBuffer(cmd);

    if (push.buf) PyBuffer_Release(&push);

    VkResult res = submit_and_wait(dev, cmd, self->dispatch_fence);
    vk_free_temp_cmd(dev, cmd);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Indirect dispatch failed (error %d)", res);
        return nullptr;
    }
    Py_RETURN_NONE;
}

PyObject *vk_Compute_dispatch_indirect_batch(vk_Compute *self, PyObject *args) {
    PyObject *buffer_obj;
    uint32_t offset, count, stride;
    Py_buffer push = {0};
    if (!PyArg_ParseTuple(args, "OIII|y*", &buffer_obj, &offset, &count, &stride, &push))
        return nullptr;

    if (!PyObject_TypeCheck(buffer_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Expected a Buffer resource");
        return nullptr;
    }
    vk_Resource *buf = reinterpret_cast<vk_Resource *>(buffer_obj);
    if (!buf->buffer) {
        PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
        return nullptr;
    }

    vk_Device *dev = self->py_device;
    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        if (push.buf) PyBuffer_Release(&push);
        PyErr_SetString(vk_ComputeError, "Failed to allocate command buffer");
        return nullptr;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline_layout,
                            0, 1, &self->descriptor_set, 0, nullptr);
    if (push.len > 0) {
        vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                           0, static_cast<uint32_t>(push.len), push.buf);
    }
    for (uint32_t i = 0; i < count; ++i) {
        vkCmdDispatchIndirect(cmd, buf->buffer, offset + i * stride);
    }
    vkEndCommandBuffer(cmd);

    if (push.buf) PyBuffer_Release(&push);

    VkResult res = submit_and_wait(dev, cmd, self->dispatch_fence);
    vk_free_temp_cmd(dev, cmd);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Batch indirect dispatch failed (error %d)", res);
        return nullptr;
    }
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   dispatch_sequence – complex sequence with optional copy and present
   ------------------------------------------------------------------------- */
PyObject *vk_Compute_dispatch_sequence(vk_Compute *self, PyObject *args, PyObject *kwds) {
    static const char *kwlist[] = {"sequence", "copy_src", "copy_dst", "copy_slice",
                                   "present_image", "timestamps", nullptr};
    PyObject *sequence_list;
    PyObject *copy_src_obj = Py_None, *copy_dst_obj = Py_None, *present_obj = Py_None;
    int copy_slice = 0;
    int enable_timestamps = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|OOiOp", (char **)kwlist,
                                     &PyList_Type, &sequence_list,
                                     &copy_src_obj, &copy_dst_obj, &copy_slice,
                                     &present_obj, &enable_timestamps))
        return nullptr;

    Py_ssize_t num_items = PyList_Size(sequence_list);

    // Validate copy resources if provided
    vk_Resource *src_buf = nullptr, *dst_img = nullptr, *present_img = nullptr;
    vk_Device *dev = nullptr;
    if (copy_src_obj != Py_None && copy_dst_obj != Py_None) {
        if (!PyObject_TypeCheck(copy_src_obj, &vk_Resource_Type) ||
            !PyObject_TypeCheck(copy_dst_obj, &vk_Resource_Type)) {
            PyErr_SetString(PyExc_TypeError, "copy_src and copy_dst must be Resources");
            return nullptr;
        }
        src_buf = reinterpret_cast<vk_Resource *>(copy_src_obj);
        dst_img = reinterpret_cast<vk_Resource *>(copy_dst_obj);
        if (!src_buf->buffer || !dst_img->image) {
            PyErr_SetString(PyExc_TypeError, "copy_src must be buffer, copy_dst texture");
            return nullptr;
        }
        dev = src_buf->py_device;
        if (dev != dst_img->py_device) {
            PyErr_SetString(PyExc_ValueError, "Resources belong to different devices");
            return nullptr;
        }
    }
    if (present_obj != Py_None) {
        if (!PyObject_TypeCheck(present_obj, &vk_Resource_Type)) {
            PyErr_SetString(PyExc_TypeError, "present_image must be a texture");
            return nullptr;
        }
        present_img = reinterpret_cast<vk_Resource *>(present_obj);
        if (!present_img->image) {
            PyErr_SetString(PyExc_TypeError, "present_image must be a texture");
            return nullptr;
        }
        if (!dev) dev = present_img->py_device;
        else if (dev != present_img->py_device) {
            PyErr_SetString(PyExc_ValueError, "Resources belong to different devices");
            return nullptr;
        }
    }

    // Parse sequence and determine device
    std::vector<vk_Compute *> comps;
    std::vector<uint32_t> xs, ys, zs;
    std::vector<PyObject *> pushes;
    comps.reserve(num_items);
    for (Py_ssize_t i = 0; i < num_items; ++i) {
        PyObject *tuple = PyList_GetItem(sequence_list, i);
        if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
            PyErr_Format(PyExc_TypeError, "Item %zd must be a 5‑tuple", i);
            return nullptr;
        }
        PyObject *comp_obj = PyTuple_GetItem(tuple, 0);
        if (!PyObject_TypeCheck(comp_obj, &vk_Compute_Type)) {
            PyErr_Format(PyExc_TypeError, "Item %zd first element must be a Compute", i);
            return nullptr;
        }
        vk_Compute *comp = reinterpret_cast<vk_Compute *>(comp_obj);
        if (!dev) dev = comp->py_device;
        else if (dev != comp->py_device) {
            PyErr_Format(PyExc_ValueError, "Item %zd Compute belongs to different device", i);
            return nullptr;
        }
        uint32_t x, y, z;
        PyObject *push_obj;
        if (!PyArg_ParseTuple(tuple, "OIIIO", &comp_obj, &x, &y, &z, &push_obj))
            return nullptr;
        comps.push_back(comp);
        xs.push_back(x);
        ys.push_back(y);
        zs.push_back(z);
        pushes.push_back(push_obj);
        Py_INCREF(push_obj);
    }

    if (!dev) {
        PyErr_SetString(PyExc_ValueError, "No valid resources or computes provided");
        return nullptr;
    }

    // Timestamp setup
    bool use_timestamps = enable_timestamps && dev->supports_timestamps;
    uint32_t total_ts = 0;
    std::vector<uint32_t> ts_before, ts_after;
    uint32_t ts_copy_before = 0, ts_copy_after = 0;
    uint32_t ts_present_before = 0, ts_present_after = 0;
    if (use_timestamps) {
        total_ts = 2 + 2 * static_cast<uint32_t>(num_items) + (present_img ? 2 : 0);
        if (total_ts <= dev->timestamp_count) {
            ts_copy_before = 1;
            ts_copy_after = 2;
            uint32_t base = 3;
            for (Py_ssize_t i = 0; i < num_items; ++i) {
                ts_before.push_back(base++);
                ts_after.push_back(base++);
            }
            if (present_img) {
                ts_present_before = base++;
                ts_present_after = base++;
            }
        } else {
            use_timestamps = false;
        }
    }

    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        for (auto p : pushes) Py_DECREF(p);
        PyErr_SetString(vk_ComputeError, "Failed to allocate command buffer");
        return nullptr;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);

    if (use_timestamps) {
        vkCmdResetQueryPool(cmd, dev->timestamp_pool, 0, total_ts);
        vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, dev->timestamp_pool, 0);
    }

    // Optional pre‑copy
    if (src_buf && dst_img) {
        if (use_timestamps) {
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT, dev->timestamp_pool, ts_copy_before);
        }
        vk_image_barrier(cmd, dst_img->image,
                         VK_IMAGE_LAYOUT_GENERAL, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_ACCESS_SHADER_WRITE_BIT, VK_ACCESS_TRANSFER_WRITE_BIT,
                         0, 1, copy_slice, 1);
        VkBufferImageCopy region = {};
        region.bufferOffset = 0;
        region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        region.imageSubresource.baseArrayLayer = static_cast<uint32_t>(copy_slice);
        region.imageSubresource.layerCount = 1;
        region.imageExtent = dst_img->image_extent;
        vkCmdCopyBufferToImage(cmd, src_buf->buffer, dst_img->image,
                               VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
        vk_image_barrier(cmd, dst_img->image,
                         VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_ACCESS_TRANSFER_WRITE_BIT, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                         0, 1, copy_slice, 1);
        if (use_timestamps) {
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT, dev->timestamp_pool, ts_copy_after);
        }
    }

    // Dispatches
    for (Py_ssize_t i = 0; i < num_items; ++i) {
        vk_Compute *comp = comps[i];
        if (use_timestamps) {
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, dev->timestamp_pool, ts_before[i]);
        }
        vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, comp->pipeline);
        vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, comp->pipeline_layout,
                                0, 1, &comp->descriptor_set, 0, nullptr);
        if (pushes[i] != Py_None) {
            Py_buffer view;
            if (PyObject_GetBuffer(pushes[i], &view, PyBUF_SIMPLE) < 0) {
                vkEndCommandBuffer(cmd);
                vk_free_temp_cmd(dev, cmd);
                for (auto p : pushes) Py_DECREF(p);
                return nullptr;
            }
            if (view.len > 0) {
                vkCmdPushConstants(cmd, comp->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                                   0, static_cast<uint32_t>(view.len), view.buf);
            }
            PyBuffer_Release(&view);
        }
        vkCmdDispatch(cmd, xs[i], ys[i], zs[i]);
        if (use_timestamps) {
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, dev->timestamp_pool, ts_after[i]);
        }
        if (i < num_items - 1 || present_img) {
            VkMemoryBarrier barrier = { VK_STRUCTURE_TYPE_MEMORY_BARRIER };
            barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
            barrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;
            vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                                 VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0,
                                 1, &barrier, 0, nullptr, 0, nullptr);
        }
    }

    // Optional present transition
    if (present_img) {
        if (use_timestamps) {
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, dev->timestamp_pool, ts_present_before);
        }
        vk_image_barrier(cmd, present_img->image,
                         VK_IMAGE_LAYOUT_GENERAL, VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                         VK_ACCESS_SHADER_WRITE_BIT, 0,
                         0, 1, 0, 1);
        if (use_timestamps) {
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, dev->timestamp_pool, ts_present_after);
        }
    }

    vkEndCommandBuffer(cmd);

    VkFence fence = (num_items > 0) ? comps[0]->dispatch_fence : VK_NULL_HANDLE;
    VkFence temp_fence = VK_NULL_HANDLE;
    if (fence == VK_NULL_HANDLE) {
        VkFenceCreateInfo finfo = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
        vkCreateFence(dev->device, &finfo, nullptr, &temp_fence);
        fence = temp_fence;
    } else {
        vkResetFences(dev->device, 1, &fence);
    }

    VkResult res = submit_and_wait(dev, cmd, fence);
    vk_free_temp_cmd(dev, cmd);
    for (auto p : pushes) Py_DECREF(p);

    if (temp_fence) vkDestroyFence(dev->device, temp_fence, nullptr);

    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Sequence submission failed (error %d)", res);
        return nullptr;
    }

    if (use_timestamps) {
        // Read timestamps
        uint64_t *ts_data = (uint64_t *)PyMem_Malloc(total_ts * sizeof(uint64_t));
        vkGetQueryPoolResults(dev->device, dev->timestamp_pool, 0, total_ts,
                              total_ts * sizeof(uint64_t), ts_data, sizeof(uint64_t),
                              VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT);
        PyObject *ts_list = PyList_New(total_ts);
        for (uint32_t i = 0; i < total_ts; ++i) {
            double ns = ts_data[i] * dev->timestamp_period;
            PyList_SetItem(ts_list, i, PyFloat_FromDouble(ns));
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

/* ----------------------------------------------------------------------------
   dispatch_tiles
   ------------------------------------------------------------------------- */
PyObject *vk_Compute_dispatch_tiles(vk_Compute *self, PyObject *args) {
    PyObject *tiles_list;
    uint32_t tile_width, tile_height;
    if (!PyArg_ParseTuple(args, "O!II", &PyList_Type, &tiles_list, &tile_width, &tile_height))
        return nullptr;

    Py_ssize_t num_tiles = PyList_Size(tiles_list);
    if (num_tiles == 0)
        Py_RETURN_NONE;

    vk_Device *dev = self->py_device;
    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        PyErr_SetString(vk_ComputeError, "Failed to allocate command buffer");
        return nullptr;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);
    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline_layout,
                            0, 1, &self->descriptor_set, 0, nullptr);

    uint32_t groups_x = (tile_width + 7) / 8;
    uint32_t groups_y = (tile_height + 7) / 8;

    for (Py_ssize_t i = 0; i < num_tiles; ++i) {
        PyObject *tuple = PyList_GetItem(tiles_list, i);
        uint32_t tx, ty;
        PyObject *push_obj;
        if (!PyArg_ParseTuple(tuple, "IIO", &tx, &ty, &push_obj)) {
            vkEndCommandBuffer(cmd);
            vk_free_temp_cmd(dev, cmd);
            return nullptr;
        }
        Py_buffer view;
        if (PyObject_GetBuffer(push_obj, &view, PyBUF_SIMPLE) < 0) {
            vkEndCommandBuffer(cmd);
            vk_free_temp_cmd(dev, cmd);
            return nullptr;
        }
        if (view.len > 0) {
            vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                               0, static_cast<uint32_t>(view.len), view.buf);
        }
        PyBuffer_Release(&view);
        vkCmdDispatch(cmd, groups_x, groups_y, 1);
        if (i < num_tiles - 1) {
            VkMemoryBarrier barrier = { VK_STRUCTURE_TYPE_MEMORY_BARRIER };
            barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
            barrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;
            vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                                 VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0,
                                 1, &barrier, 0, nullptr, 0, nullptr);
        }
    }

    vkEndCommandBuffer(cmd);
    VkResult res = submit_and_wait(dev, cmd, self->dispatch_fence);
    vk_free_temp_cmd(dev, cmd);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Tile dispatch failed (error %d)", res);
        return nullptr;
    }
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Bindless binding methods
   ------------------------------------------------------------------------- */
PyObject *vk_Compute_bind_cbv(vk_Compute *self, PyObject *args) {
    uint32_t index;
    PyObject *res_obj;
    if (!PyArg_ParseTuple(args, "IO", &index, &res_obj))
        return nullptr;

    if (!self->bindless) {
        PyErr_SetString(PyExc_ValueError, "Compute is not bindless");
        return nullptr;
    }
    if (!PyObject_TypeCheck(res_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Expected a Resource");
        return nullptr;
    }
    vk_Resource *res = reinterpret_cast<vk_Resource *>(res_obj);
    if (!res->buffer) {
        PyErr_SetString(PyExc_TypeError, "Resource must be a buffer");
        return nullptr;
    }
    if (index >= self->bindless) {
        PyErr_Format(PyExc_ValueError, "Index %u out of range (max %u)", index, self->bindless - 1);
        return nullptr;
    }

    VkWriteDescriptorSet write = { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET };
    write.dstSet = self->descriptor_set;
    write.dstBinding = index;
    write.descriptorCount = 1;
    write.descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
    write.pBufferInfo = &res->descriptor_buffer_info;
    vkUpdateDescriptorSets(self->py_device->device, 1, &write, 0, nullptr);

    Py_INCREF(res_obj);
    PyList_SetItem(self->py_cbv_list, index, res_obj);
    Py_RETURN_NONE;
}

PyObject *vk_Compute_bind_srv(vk_Compute *self, PyObject *args) {
    uint32_t index;
    PyObject *res_obj;
    if (!PyArg_ParseTuple(args, "IO", &index, &res_obj))
        return nullptr;

    if (!self->bindless) {
        PyErr_SetString(PyExc_ValueError, "Compute is not bindless");
        return nullptr;
    }
    if (!PyObject_TypeCheck(res_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Expected a Resource");
        return nullptr;
    }
    vk_Resource *res = reinterpret_cast<vk_Resource *>(res_obj);
    if (index >= self->bindless) {
        PyErr_Format(PyExc_ValueError, "Index %u out of range (max %u)", index, self->bindless - 1);
        return nullptr;
    }

    VkWriteDescriptorSet write = { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET };
    write.dstSet = self->descriptor_set;
    write.dstBinding = 1024 + index;
    write.descriptorCount = 1;
    write.descriptorType = res->image ? VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
    if (res->image) {
        write.pImageInfo = &res->descriptor_image_info;
    } else {
        write.pBufferInfo = &res->descriptor_buffer_info;
    }
    vkUpdateDescriptorSets(self->py_device->device, 1, &write, 0, nullptr);

    Py_INCREF(res_obj);
    PyList_SetItem(self->py_srv_list, index, res_obj);
    Py_RETURN_NONE;
}

PyObject *vk_Compute_bind_uav(vk_Compute *self, PyObject *args) {
    uint32_t index;
    PyObject *res_obj;
    if (!PyArg_ParseTuple(args, "IO", &index, &res_obj))
        return nullptr;

    if (!self->bindless) {
        PyErr_SetString(PyExc_ValueError, "Compute is not bindless");
        return nullptr;
    }
    if (!PyObject_TypeCheck(res_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Expected a Resource");
        return nullptr;
    }
    vk_Resource *res = reinterpret_cast<vk_Resource *>(res_obj);
    if (index >= self->bindless) {
        PyErr_Format(PyExc_ValueError, "Index %u out of range (max %u)", index, self->bindless - 1);
        return nullptr;
    }

    VkWriteDescriptorSet write = { VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET };
    write.dstSet = self->descriptor_set;
    write.dstBinding = 2048 + index;
    write.descriptorCount = 1;
    write.descriptorType = res->image ? VK_DESCRIPTOR_TYPE_STORAGE_IMAGE : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    if (res->image) {
        write.pImageInfo = &res->descriptor_image_info;
    } else {
        write.pBufferInfo = &res->descriptor_buffer_info;
    }
    vkUpdateDescriptorSets(self->py_device->device, 1, &write, 0, nullptr);

    Py_INCREF(res_obj);
    PyList_SetItem(self->py_uav_list, index, res_obj);
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Compute type definition
   ------------------------------------------------------------------------- */
static PyMethodDef vk_Compute_methods[] = {
    {"dispatch", (PyCFunction)vk_Compute_dispatch, METH_VARARGS, "Execute compute pipeline."},
    {"dispatch_indirect", (PyCFunction)vk_Compute_dispatch_indirect, METH_VARARGS, "Execute indirect dispatch."},
    {"dispatch_indirect_batch", (PyCFunction)vk_Compute_dispatch_indirect_batch, METH_VARARGS, "Batch indirect dispatches."},
    {"dispatch_sequence", (PyCFunction)vk_Compute_dispatch_sequence, METH_VARARGS | METH_KEYWORDS, "Execute sequence of dispatches."},
    {"dispatch_tiles", (PyCFunction)vk_Compute_dispatch_tiles, METH_VARARGS, "Dispatch tiles with per‑tile push constants."},
    {"bind_cbv", (PyCFunction)vk_Compute_bind_cbv, METH_VARARGS, "Bind a CBV in bindless mode."},
    {"bind_srv", (PyCFunction)vk_Compute_bind_srv, METH_VARARGS, "Bind an SRV in bindless mode."},
    {"bind_uav", (PyCFunction)vk_Compute_bind_uav, METH_VARARGS, "Bind a UAV in bindless mode."},
    {nullptr, nullptr, 0, nullptr}
};

PyTypeObject vk_Compute_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Compute",
    .tp_basicsize = sizeof(vk_Compute),
    .tp_dealloc = (destructor)vk_Compute_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Compute_methods,
};