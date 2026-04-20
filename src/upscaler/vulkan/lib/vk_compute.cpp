/**
 * @file vk_compute.cpp
 * @brief Vulkan compute pipeline implementation.
 *
 * This file implements the vk.Compute Python type, which encapsulates a
 * Vulkan compute pipeline, descriptor set, and associated resources.
 * It provides methods to dispatch compute shaders and execute sequences
 * of dispatches with optional pre-copy and presentation.
 */

#include "vk_device.h"
#include "vk_compute.h"
#include "vk_utils.h"
#include <unordered_map>
#include <vector>
#include <cstring>

// Forward declarations of Python type objects (defined elsewhere)
extern PyTypeObject vk_Resource_Type;
extern PyTypeObject vk_Sampler_Type;

/* ----------------------------------------------------------------------------
   Compute deallocator
   ------------------------------------------------------------------------- */
void vk_Compute_dealloc(vk_Compute *self) {
    if (self->py_device) {
        VkDevice dev = self->py_device->device;
        if (self->pipeline)           vkDestroyPipeline(dev, self->pipeline, nullptr);
        if (self->pipeline_layout)    vkDestroyPipelineLayout(dev, self->pipeline_layout, nullptr);
        if (self->descriptor_pool)    vkDestroyDescriptorPool(dev, self->descriptor_pool, nullptr);
        if (self->descriptor_set_layout) vkDestroyDescriptorSetLayout(dev, self->descriptor_set_layout, nullptr);
        if (self->shader_module)      vkDestroyShaderModule(dev, self->shader_module, nullptr);
        if (self->dispatch_fence)     vkDestroyFence(dev, self->dispatch_fence, nullptr);
        Py_DECREF(self->py_device);
    }
    Py_XDECREF(self->py_cbv_list);
    Py_XDECREF(self->py_srv_list);
    Py_XDECREF(self->py_uav_list);
    Py_XDECREF(self->py_samplers_list);
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/* ----------------------------------------------------------------------------
   vk_Device_create_compute_impl
   ------------------------------------------------------------------------- */
/**
 * Internal implementation of Device.create_compute().
 * Creates a compute pipeline, descriptor set layout, descriptor pool,
 * and descriptor set from the provided shader and resource lists.
 *
 * @param self   vk.Device instance.
 * @param args   Tuple containing shader bytes and optional lists.
 * @param kwds   Keyword arguments (cbv, srv, uav, samplers, push_size, bindless).
 * @return       New vk.Compute object or NULL with Python exception set.
 */
PyObject *vk_Device_create_compute_impl(vk_Device *self, PyObject *args, PyObject *kwds) {
    static const char *kwlist[] = {"shader", "cbv", "srv", "uav", "samplers",
                                   "push_size", "bindless", nullptr};
    Py_buffer shader_view;
    PyObject *cbv_list = nullptr, *srv_list = nullptr, *uav_list = nullptr, *samplers_list = nullptr;
    uint32_t push_size = 0;
    uint32_t bindless = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "y*|OOOOII", (char **)kwlist,
                                     &shader_view, &cbv_list, &srv_list, &uav_list,
                                     &samplers_list, &push_size, &bindless))
        return nullptr;

    // Ensure device is initialized
    vk_Device *dev = vk_Device_get_initialized(self);
    if (!dev) {
        PyBuffer_Release(&shader_view);
        return nullptr;
    }

    // Collect resource lists and validate
    std::vector<vk_Resource *> cbv, srv, uav;
    std::vector<vk_Sampler *> samplers;
    if (!vk_check_descriptor_lists(&vk_Resource_Type, cbv_list, cbv,
                                   srv_list, srv, uav_list, uav,
                                   &vk_Sampler_Type, samplers_list, samplers)) {
        PyBuffer_Release(&shader_view);
        return nullptr;
    }

    // Check bindless support
    if (bindless > 0 && !dev->supports_bindless) {
        PyBuffer_Release(&shader_view);
        PyErr_SetString(vk_ComputeError, "Bindless not supported on this device");
        return nullptr;
    }

    // SPIR-V patching for BGRA UAVs if needed
    const uint32_t *spirv_code = static_cast<const uint32_t *>(shader_view.buf);
    size_t spirv_size = shader_view.len;
    uint32_t *patched_code = nullptr;

    if (!dev->features.shaderStorageImageReadWithoutFormat) {
        uint32_t binding = 2048;
        for (vk_Resource *res : uav) {
            if (res->image && (res->format == VK_FORMAT_B8G8R8A8_UNORM ||
                               res->format == VK_FORMAT_B8G8R8A8_SRGB)) {
                patched_code = vk_spirv_patch_nonreadable_uav(spirv_code, spirv_size, binding);
                if (patched_code) {
                    spirv_code = patched_code;
                    spirv_size += 12; // 3 words added
                    break;
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
        PyErr_SetString(vk_ComputeError, "Invalid SPIR-V or no compute entry point");
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
    VK_CHECK_OR_RETURN_NULL(res, vk_ComputeError, "Failed to create shader module");

    // Create descriptor set layout
    VkDescriptorSetLayout dsl;
    if (!vk_create_compute_descriptor_set_layout(dev, cbv, srv, uav, samplers,
                                                 bindless, &dsl)) {
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        return nullptr; // error already set
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
    res = vkCreatePipelineLayout(dev->device, &pl_info, nullptr, &pipeline_layout);
    if (res != VK_SUCCESS) {
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        PyErr_Format(vk_ComputeError, "Failed to create pipeline layout (error %d)", res);
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

    // Allocate descriptor pool and write descriptor set
    VkDescriptorPool descriptor_pool;
    VkDescriptorSet descriptor_set;
    if (!vk_allocate_and_write_descriptor_set(dev, cbv, srv, uav, samplers,
                                              bindless, dsl,
                                              &descriptor_pool, &descriptor_set)) {
        vkDestroyPipeline(dev->device, pipeline, nullptr);
        vkDestroyPipelineLayout(dev->device, pipeline_layout, nullptr);
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        return nullptr; // error already set
    }

    // Create dispatch fence (used for synchronisation)
    VkFence dispatch_fence = vk_create_fence(dev);
    if (!dispatch_fence) {
        vkDestroyDescriptorPool(dev->device, descriptor_pool, nullptr);
        vkDestroyPipeline(dev->device, pipeline, nullptr);
        vkDestroyPipelineLayout(dev->device, pipeline_layout, nullptr);
        vkDestroyDescriptorSetLayout(dev->device, dsl, nullptr);
        vkDestroyShaderModule(dev->device, shader_module, nullptr);
        return nullptr;
    }

    // Allocate Python object
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

    auto fill_list = [](PyObject *list, size_t count, const auto &vec) {
        for (size_t i = 0; i < count; ++i) {
            PyObject *item = (i < vec.size()) ? reinterpret_cast<PyObject *>(vec[i]) : Py_None;
            Py_INCREF(item);
            PyList_SetItem(list, i, item);
        }
    };
    fill_list(comp->py_cbv_list, num_cbv, cbv);
    fill_list(comp->py_srv_list, num_srv, srv);
    fill_list(comp->py_uav_list, num_uav, uav);

    for (vk_Sampler *samp : samplers) {
        PyList_Append(comp->py_samplers_list, reinterpret_cast<PyObject *>(samp));
    }

    return reinterpret_cast<PyObject *>(comp);
}

/* ----------------------------------------------------------------------------
   Dispatch methods
   ------------------------------------------------------------------------- */

/**
 * Execute a single compute dispatch.
 *
 * Args:
 *     x (int): number of groups in X.
 *     y (int): number of groups in Y.
 *     z (int): number of groups in Z.
 *     push_data (bytes, optional): push constant data (must be multiple of 4).
 */
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

    // Record and execute command buffer using one-shot helper
    bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
        vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                                self->pipeline_layout, 0, 1, &self->descriptor_set, 0, nullptr);
        if (push.len > 0) {
            vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                               0, static_cast<uint32_t>(push.len), push.buf);
        }
        vkCmdDispatch(cmd, x, y, z);

        // Make writes available to future command buffers (especially the copy in present)
        VkMemoryBarrier mem_barrier = { VK_STRUCTURE_TYPE_MEMORY_BARRIER };
        mem_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
        mem_barrier.dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;  // Broad availability
        vkCmdPipelineBarrier(cmd,
            VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
            VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,  // All subsequent commands see the writes
            0, 1, &mem_barrier, 0, nullptr, 0, nullptr);
            });

    if (push.buf) PyBuffer_Release(&push);
    if (!ok) return nullptr;

    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   dispatch_sequence
   ------------------------------------------------------------------------- */
/**
 * Execute a sequence of compute dispatches with optional pre-copy and presentation.
 *
 * Args (keyword arguments):
 *     sequence (list): list of 5-tuples (compute, x, y, z, push_data).
 *     copy_src (vk.Resource, optional): source buffer to copy to texture.
 *     copy_dst (vk.Resource, optional): destination texture.
 *     copy_slice (int, optional): texture array slice.
 *     present_image (vk.Resource, optional): texture to transition for present.
 *     timestamps (bool, optional): enable timestamp queries.
 *
 * Returns:
 *     If timestamps enabled, returns (None, timestamps_list). Else None.
 */
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

    // Validate and collect resources
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

    // Parse sequence of dispatches
    std::vector<vk_Compute *> comps;
    std::vector<uint32_t> xs, ys, zs;
    std::vector<PyObject *> pushes;
    comps.reserve(num_items);
    for (Py_ssize_t i = 0; i < num_items; ++i) {
        PyObject *tuple = PyList_GetItem(sequence_list, i);
        if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
            PyErr_Format(PyExc_TypeError, "Item %zd must be a 5-tuple", i);
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
        } else {
            use_timestamps = false;
        }
    }

    // Record command buffer (using one-shot execution)
    bool ok = vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        if (use_timestamps) {
            vkCmdResetQueryPool(cmd, dev->timestamp_pool, 0, total_ts);
            vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                                dev->timestamp_pool, 0);
        }

        // Pre-copy from buffer to texture
        if (src_buf && dst_img) {
            if (use_timestamps) {
                vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                                    dev->timestamp_pool, ts_copy_before);
            }
            vk_cmd_transition_for_copy_dst(cmd, dst_img->image, copy_slice, 1);
            VkBufferImageCopy region = {};
            region.bufferOffset = 0;
            region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            region.imageSubresource.baseArrayLayer = static_cast<uint32_t>(copy_slice);
            region.imageSubresource.layerCount = 1;
            region.imageExtent = dst_img->image_extent;
            vkCmdCopyBufferToImage(cmd, src_buf->buffer, dst_img->image,
                                   VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);
            vk_cmd_transition_for_compute(cmd, dst_img->image, copy_slice, 1);
            if (use_timestamps) {
                vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                                    dev->timestamp_pool, ts_copy_after);
            }
        }

        // Dispatches
        for (Py_ssize_t i = 0; i < num_items; ++i) {
            vk_Compute *comp = comps[i];
            if (use_timestamps) {
                vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                                    dev->timestamp_pool, ts_before[i]);
            }
            vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, comp->pipeline);
            vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                                    comp->pipeline_layout, 0, 1, &comp->descriptor_set, 0, nullptr);
            if (pushes[i] != Py_None) {
                Py_buffer view;
                if (PyObject_GetBuffer(pushes[i], &view, PyBUF_SIMPLE) < 0) {
                    // Cleanup handled by caller
                    return;
                }
                if (view.len > 0) {
                    vkCmdPushConstants(cmd, comp->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                                       0, static_cast<uint32_t>(view.len), view.buf);
                }
                PyBuffer_Release(&view);
            }
            vkCmdDispatch(cmd, xs[i], ys[i], zs[i]);
            if (use_timestamps) {
                vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                                    dev->timestamp_pool, ts_after[i]);
            }
            // Memory barrier between dispatches
            if (i < num_items - 1 || present_img) {
                VkMemoryBarrier barrier = { VK_STRUCTURE_TYPE_MEMORY_BARRIER };
                barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
                barrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;
                vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                                     VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0,
                                     1, &barrier, 0, nullptr, 0, nullptr);
            }
        }
    });

    for (auto p : pushes) Py_DECREF(p);
    if (!ok) return nullptr;

    // Read timestamps if requested
    if (use_timestamps) {
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
   Compute type definition
   ------------------------------------------------------------------------- */
static PyMethodDef vk_Compute_methods[] = {
    {"dispatch", (PyCFunction)vk_Compute_dispatch, METH_VARARGS,
     "Execute compute pipeline with given group count."},
    {"dispatch_sequence", (PyCFunction)vk_Compute_dispatch_sequence,
     METH_VARARGS | METH_KEYWORDS,
     "Execute a sequence of dispatches with optional copy and present."},
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