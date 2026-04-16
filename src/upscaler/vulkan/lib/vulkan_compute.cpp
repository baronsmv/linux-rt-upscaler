#include "vulkan_common.h"

/* ----------------------------------------------------------------------------
   Helpers
   ------------------------------------------------------------------------- */

static VkCommandBuffer allocate_temp_cmd(vulkan_Device *dev) {
  VkCommandBufferAllocateInfo allocInfo = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
  allocInfo.commandPool = dev->command_pool;
  allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
  allocInfo.commandBufferCount = 1;
  VkCommandBuffer cmd = VK_NULL_HANDLE;
  vkAllocateCommandBuffers(dev->device, &allocInfo, &cmd);
  return cmd;
}

static void free_temp_cmd(vulkan_Device *dev, VkCommandBuffer cmd) {
  if (cmd)
    vkFreeCommandBuffers(dev->device, dev->command_pool, 1, &cmd);
}

/* ----------------------------------------------------------------------------
   Compute Type
   ------------------------------------------------------------------------- */
static void vulkan_Compute_dealloc(vulkan_Compute *self) {
  if (self->py_device) {
    VkDevice device = self->py_device->device;
    if (self->pipeline)
      vkDestroyPipeline(device, self->pipeline, NULL);
    if (self->pipeline_layout)
      vkDestroyPipelineLayout(device, self->pipeline_layout, NULL);
    if (self->descriptor_pool)
      vkDestroyDescriptorPool(device, self->descriptor_pool, NULL);
    if (self->descriptor_set_layout)
      vkDestroyDescriptorSetLayout(device, self->descriptor_set_layout, NULL);
    if (self->shader_module)
      vkDestroyShaderModule(device, self->shader_module, NULL);
    if (self->dispatch_fence)
      vkDestroyFence(device, self->dispatch_fence, NULL);
    Py_DECREF(self->py_device);
  }
  Py_XDECREF(self->py_cbv_list);
  Py_XDECREF(self->py_srv_list);
  Py_XDECREF(self->py_uav_list);
  Py_XDECREF(self->py_samplers_list);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

PyTypeObject vulkan_Compute_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Compute",
    .tp_basicsize = sizeof(vulkan_Compute),
    .tp_dealloc = (destructor)vulkan_Compute_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

/* ----------------------------------------------------------------------------
   Helper: submit and wait (with fence)
   ------------------------------------------------------------------------- */
static VkResult submit_and_wait_fence(vulkan_Device *dev, VkCommandBuffer cmd,
                                      VkFence fence) {
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  VkResult res = vkQueueSubmit(dev->queue, 1, &submit, fence);
  if (res != VK_SUCCESS)
    return res;

  Py_BEGIN_ALLOW_THREADS;
  vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
  vkResetFences(dev->device, 1, &fence);
  Py_END_ALLOW_THREADS;
  return VK_SUCCESS;
}

/* ----------------------------------------------------------------------------
   vulkan_Compute_dispatch
   ------------------------------------------------------------------------- */
PyObject *vulkan_Compute_dispatch(vulkan_Compute *self, PyObject *args) {
  uint32_t x, y, z;
  Py_buffer push = {0};
  if (!PyArg_ParseTuple(args, "III|y*", &x, &y, &z, &push))
    return NULL;

  if (push.len > 0) {
    if (push.len > self->push_constant_size || (push.len % 4) != 0) {
      PyBuffer_Release(&push);
      return PyErr_Format(PyExc_ValueError,
                          "Invalid push constant size: %u, expected max %u "
                          "with 4 bytes alignment",
                          (unsigned)push.len, self->push_constant_size);
    }
  }

  vulkan_Device *dev = self->py_device;
  VkCommandBuffer cmd = allocate_temp_cmd(dev);
  if (!cmd) {
    if (push.buf)
      PyBuffer_Release(&push);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to allocate command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  if (push.len > 0)
    vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, (uint32_t)push.len, push.buf);

  vkCmdDispatch(cmd, x, y, z);
  vkEndCommandBuffer(cmd);

  if (push.buf)
    PyBuffer_Release(&push);

  VkFence fence = self->dispatch_fence;
  vkResetFences(dev->device, 1, &fence);
  VkResult res = submit_and_wait_fence(dev, cmd, fence);
  free_temp_cmd(dev, cmd);
  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError, "Dispatch submission failed: %d",
                        res);

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_Compute_dispatch_indirect
   ------------------------------------------------------------------------- */
PyObject *vulkan_Compute_dispatch_indirect(vulkan_Compute *self,
                                           PyObject *args) {
  PyObject *indirect_obj;
  uint32_t offset;
  Py_buffer push = {0};
  if (!PyArg_ParseTuple(args, "OI|y*", &indirect_obj, &offset, &push))
    return NULL;

  if (!PyObject_TypeCheck(indirect_obj, &vulkan_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Buffer object");
    return NULL;
  }

  vulkan_Resource *indirect = (vulkan_Resource *)indirect_obj;
  if (!indirect->buffer) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
    return NULL;
  }

  if (push.len > 0) {
    if (push.len > self->push_constant_size || (push.len % 4) != 0) {
      PyBuffer_Release(&push);
      return PyErr_Format(PyExc_ValueError,
                          "Invalid push constant size: %u, expected max %u "
                          "with 4 bytes alignment",
                          (unsigned)push.len, self->push_constant_size);
    }
  }

  vulkan_Device *dev = self->py_device;
  VkCommandBuffer cmd = allocate_temp_cmd(dev);
  if (!cmd) {
    if (push.buf)
      PyBuffer_Release(&push);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to allocate command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  if (push.len > 0)
    vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, (uint32_t)push.len, push.buf);

  vkCmdDispatchIndirect(cmd, indirect->buffer, offset);
  vkEndCommandBuffer(cmd);

  if (push.buf)
    PyBuffer_Release(&push);

  VkFence fence = self->dispatch_fence;
  vkResetFences(dev->device, 1, &fence);
  VkResult res = submit_and_wait_fence(dev, cmd, fence);
  free_temp_cmd(dev, cmd);
  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError,
                        "Indirect dispatch submission failed: %d", res);

  Py_RETURN_NONE;
}

PyObject *vulkan_device_get_timestamps(vulkan_Device *dev, uint32_t count) {
  if (!dev->supports_timestamps) {
    Py_RETURN_NONE;
  }
  if (count > dev->timestamp_count)
    count = dev->timestamp_count;

  uint64_t *data = (uint64_t *)PyMem_Malloc(count * sizeof(uint64_t));
  if (!data)
    return PyErr_NoMemory();

  VkResult res =
      vkGetQueryPoolResults(dev->device, dev->timestamp_pool, 0, count,
                            count * sizeof(uint64_t), data, sizeof(uint64_t),
                            VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT);
  if (res != VK_SUCCESS && res != VK_NOT_READY) {
    PyMem_Free(data);
    return PyErr_Format(PyExc_RuntimeError,
                        "Failed to get timestamp results: %d", res);
  }

  PyObject *list = PyList_New(count);
  for (uint32_t i = 0; i < count; i++) {
    double ns = (double)data[i] * dev->timestamp_period;
    PyList_SetItem(list, i, PyFloat_FromDouble(ns));
  }
  PyMem_Free(data);
  return list;
}

PyObject *vulkan_Compute_dispatch_indirect_batch(vulkan_Compute *self,
                                                 PyObject *args) {
  PyObject *indirect_obj;
  uint32_t offset, count, stride;
  Py_buffer push = {0};
  if (!PyArg_ParseTuple(args, "OIII|y*", &indirect_obj, &offset, &count,
                        &stride, &push))
    return NULL;

  if (!PyObject_TypeCheck(indirect_obj, &vulkan_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Buffer object");
    return NULL;
  }

  vulkan_Resource *indirect = (vulkan_Resource *)indirect_obj;
  if (!indirect->buffer) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a buffer");
    return NULL;
  }

  vulkan_Device *dev = self->py_device;
  VkCommandBuffer cmd = allocate_temp_cmd(dev);
  if (!cmd) {
    if (push.buf)
      PyBuffer_Release(&push);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to allocate command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  if (push.len > 0)
    vkCmdPushConstants(cmd, self->pipeline_layout, VK_SHADER_STAGE_COMPUTE_BIT,
                       0, (uint32_t)push.len, push.buf);

  for (uint32_t i = 0; i < count; i++) {
    vkCmdDispatchIndirect(cmd, indirect->buffer, offset + i * stride);
  }

  vkEndCommandBuffer(cmd);

  if (push.buf)
    PyBuffer_Release(&push);

  VkFence fence = self->dispatch_fence;
  vkResetFences(dev->device, 1, &fence);
  VkResult res = submit_and_wait_fence(dev, cmd, fence);
  free_temp_cmd(dev, cmd);
  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError,
                        "Batch indirect dispatch failed: %d", res);

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_Compute_dispatch_sequence
   ------------------------------------------------------------------------- */
PyObject *vulkan_Compute_dispatch_sequence(vulkan_Compute *self, PyObject *args,
                                           PyObject *kwds) {
  static const char *kwlist[] = {"sequence",   "copy_src",      "copy_dst",
                                 "copy_slice", "present_image", "timestamps",
                                 NULL};
  PyObject *sequence_list;
  PyObject *copy_src_obj = Py_None;
  PyObject *copy_dst_obj = Py_None;
  int copy_slice = 0;
  PyObject *present_obj = Py_None;
  int enable_timestamps = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|OOiOp", (char **)kwlist,
                                   &PyList_Type, &sequence_list, &copy_src_obj,
                                   &copy_dst_obj, &copy_slice, &present_obj,
                                   &enable_timestamps))
    return NULL;

  Py_ssize_t num_items = PyList_Size(sequence_list);

  vulkan_Resource *src_buf = NULL;
  vulkan_Resource *dst_img = NULL;
  if (copy_src_obj != Py_None && copy_dst_obj != Py_None) {
    if (!PyObject_TypeCheck(copy_src_obj, &vulkan_Resource_Type) ||
        !PyObject_TypeCheck(copy_dst_obj, &vulkan_Resource_Type)) {
      PyErr_SetString(PyExc_TypeError,
                      "copy_src and copy_dst must be Resource objects");
      return NULL;
    }
    src_buf = (vulkan_Resource *)copy_src_obj;
    dst_img = (vulkan_Resource *)copy_dst_obj;
    if (!src_buf->buffer) {
      PyErr_SetString(PyExc_TypeError, "copy_src must be a Buffer");
      return NULL;
    }
    if (!dst_img->image) {
      PyErr_SetString(PyExc_TypeError, "copy_dst must be a Texture");
      return NULL;
    }
    if (copy_slice < 0 || (uint32_t)copy_slice >= dst_img->slices) {
      PyErr_Format(PyExc_ValueError, "copy_slice %d out of range [0, %u)",
                   copy_slice, dst_img->slices);
      return NULL;
    }
  }

  vulkan_Resource *present_image = NULL;
  if (present_obj != Py_None) {
    if (!PyObject_TypeCheck(present_obj, &vulkan_Resource_Type)) {
      PyErr_SetString(PyExc_TypeError, "present_image must be a Texture");
      return NULL;
    }
    present_image = (vulkan_Resource *)present_obj;
    if (!present_image->image) {
      PyErr_SetString(PyExc_TypeError, "present_image must be a Texture");
      return NULL;
    }
  }

  vulkan_Device *dev = NULL;
  vulkan_Compute *first_comp = NULL;
  VkFence fence = VK_NULL_HANDLE;

  if (num_items > 0) {
    PyObject *first_tuple = PyList_GetItem(sequence_list, 0);
    if (!PyTuple_Check(first_tuple) || PyTuple_Size(first_tuple) != 5) {
      PyErr_Format(
          PyExc_TypeError,
          "sequence item 0 must be a 5-tuple (compute, x, y, z, push)");
      return NULL;
    }
    PyObject *comp_obj = PyTuple_GetItem(first_tuple, 0);
    if (!PyObject_TypeCheck(comp_obj, &vulkan_Compute_Type)) {
      PyErr_SetString(PyExc_TypeError,
                      "First element of tuple must be a Compute object");
      return NULL;
    }
    first_comp = (vulkan_Compute *)comp_obj;
    dev = first_comp->py_device;
    fence = first_comp->dispatch_fence;
  } else {
    if (src_buf && dst_img) {
      dev = src_buf->py_device;
      if (dev != dst_img->py_device) {
        PyErr_SetString(PyExc_ValueError,
                        "copy_src and copy_dst belong to different devices");
        return NULL;
      }
    } else if (present_image) {
      dev = present_image->py_device;
    } else {
      PyErr_SetString(PyExc_ValueError,
                      "No compute objects and no valid resources provided");
      return NULL;
    }
  }

  struct DispatchItem {
    vulkan_Compute *comp;
    uint32_t x, y, z;
    PyObject *push_obj;
  };
  std::vector<DispatchItem> items;
  items.reserve(num_items);

  for (Py_ssize_t i = 0; i < num_items; i++) {
    PyObject *tuple = PyList_GetItem(sequence_list, i);
    if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 5) {
      PyErr_Format(
          PyExc_TypeError,
          "sequence item %zd must be a 5-tuple (compute, x, y, z, push)", i);
      return NULL;
    }

    PyObject *comp_obj = PyTuple_GetItem(tuple, 0);
    if (!PyObject_TypeCheck(comp_obj, &vulkan_Compute_Type)) {
      PyErr_Format(PyExc_TypeError,
                   "Item %zd: first element must be a Compute object", i);
      return NULL;
    }

    vulkan_Compute *comp = (vulkan_Compute *)comp_obj;
    if (comp->py_device != dev) {
      PyErr_Format(PyExc_ValueError,
                   "Item %zd: Compute object belongs to a different device", i);
      return NULL;
    }

    uint32_t x, y, z;
    PyObject *push_obj;
    if (!PyArg_ParseTuple(tuple, "OIII|O", &comp_obj, &x, &y, &z, &push_obj)) {
      return NULL;
    }

    if (push_obj != Py_None) {
      Py_buffer view;
      if (PyObject_GetBuffer(push_obj, &view, PyBUF_SIMPLE) < 0) {
        return NULL;
      }
      if (view.len > 0) {
        if (view.len > comp->push_constant_size || (view.len % 4) != 0) {
          PyBuffer_Release(&view);
          PyErr_Format(PyExc_ValueError,
                       "Item %zd: Invalid push constant size (expected max %u, "
                       "multiple of 4)",
                       i, comp->push_constant_size);
          return NULL;
        }
      }
      PyBuffer_Release(&view);
    }

    items.push_back({comp, x, y, z, push_obj});
  }

  bool use_timestamps = enable_timestamps && dev->supports_timestamps;
  uint32_t ts_idx = 0;
  uint32_t total_ts = 0;
  const uint32_t ts_top = 0;
  uint32_t ts_copy_before = 0, ts_copy_after = 0;
  std::vector<uint32_t> ts_dispatch_before, ts_dispatch_after;
  uint32_t ts_present_before = 0, ts_present_after = 0, ts_bottom = 0;

  if (use_timestamps) {
    total_ts = 1 + 2 + (uint32_t)items.size() * 2 + (present_image ? 2 : 0) + 1;
    if (dev->timestamp_count < total_ts) {
      use_timestamps = false;
    } else {
      ts_idx = 1;
      ts_copy_before = ts_idx++;
      ts_copy_after = ts_idx++;
      ts_dispatch_before.resize(items.size());
      ts_dispatch_after.resize(items.size());
      for (size_t i = 0; i < items.size(); i++) {
        ts_dispatch_before[i] = ts_idx++;
        ts_dispatch_after[i] = ts_idx++;
      }
      if (present_image) {
        ts_present_before = ts_idx++;
        ts_present_after = ts_idx++;
      }
      ts_bottom = ts_idx++;
    }
  }

  VkCommandBuffer cmd = allocate_temp_cmd(dev);
  if (!cmd) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to allocate command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  if (use_timestamps) {
    vkCmdResetQueryPool(cmd, dev->timestamp_pool, 0, total_ts);
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                        dev->timestamp_pool, ts_top);
  }

  if (src_buf && dst_img) {
    if (use_timestamps) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                          dev->timestamp_pool, ts_copy_before);
    }

    VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
    barrier.image = dst_img->image;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.baseArrayLayer = (uint32_t)copy_slice;
    barrier.subresourceRange.layerCount = 1;
    barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.srcAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;

    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 1,
                         &barrier);

    VkBufferImageCopy region = {0};
    region.bufferOffset = 0;
    region.imageSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.imageSubresource.baseArrayLayer = (uint32_t)copy_slice;
    region.imageSubresource.layerCount = 1;
    region.imageExtent = dst_img->image_extent;

    vkCmdCopyBufferToImage(cmd, src_buf->buffer, dst_img->image,
                           VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

    barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.dstAccessMask =
        VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                         NULL, 1, &barrier);

    if (use_timestamps) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                          dev->timestamp_pool, ts_copy_after);
    }
  } else if (use_timestamps) {
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                        dev->timestamp_pool, ts_copy_before);
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                        dev->timestamp_pool, ts_copy_after);
  }

  for (size_t i = 0; i < items.size(); i++) {
    vulkan_Compute *comp = items[i].comp;

    if (use_timestamps) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                          dev->timestamp_pool, ts_dispatch_before[i]);
    }

    vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, comp->pipeline);
    vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                            comp->pipeline_layout, 0, 1, &comp->descriptor_set,
                            0, NULL);

    if (items[i].push_obj != Py_None) {
      Py_buffer view;
      if (PyObject_GetBuffer(items[i].push_obj, &view, PyBUF_SIMPLE) < 0) {
        vkEndCommandBuffer(cmd);
        free_temp_cmd(dev, cmd);
        return NULL;
      }
      if (view.len > 0)
        vkCmdPushConstants(cmd, comp->pipeline_layout,
                           VK_SHADER_STAGE_COMPUTE_BIT, 0, (uint32_t)view.len,
                           view.buf);
      PyBuffer_Release(&view);
    }

    vkCmdDispatch(cmd, items[i].x, items[i].y, items[i].z);

    if (use_timestamps) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                          dev->timestamp_pool, ts_dispatch_after[i]);
    }

    if (i < items.size() - 1 || present_image) {
      VkMemoryBarrier barrier = {VK_STRUCTURE_TYPE_MEMORY_BARRIER};
      barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
      barrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;

      vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                           VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 1, &barrier,
                           0, NULL, 0, NULL);
    }
  }

  if (present_image) {
    if (use_timestamps) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                          dev->timestamp_pool, ts_present_before);
    }

    VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
    barrier.image = present_image->image;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.layerCount = 1;
    barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
    barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    barrier.dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;

    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0, 0, NULL, 0,
                         NULL, 1, &barrier);

    if (use_timestamps) {
      vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                          dev->timestamp_pool, ts_present_after);
    }
  }

  if (use_timestamps) {
    vkCmdWriteTimestamp(cmd, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                        dev->timestamp_pool, ts_bottom);
  }

  vkEndCommandBuffer(cmd);

  VkFence wait_fence = fence;
  VkFence temp_fence = VK_NULL_HANDLE;
  if (wait_fence == VK_NULL_HANDLE) {
    VkFenceCreateInfo finfo = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
    if (vkCreateFence(dev->device, &finfo, NULL, &temp_fence) != VK_SUCCESS) {
      free_temp_cmd(dev, cmd);
      return PyErr_Format(Compushady_ComputeError,
                          "Failed to create temporary fence");
    }
    wait_fence = temp_fence;
  } else {
    vkResetFences(dev->device, 1, &wait_fence);
  }

  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  VkResult res = vkQueueSubmit(dev->queue, 1, &submit, wait_fence);
  if (res != VK_SUCCESS) {
    if (temp_fence != VK_NULL_HANDLE)
      vkDestroyFence(dev->device, temp_fence, NULL);
    free_temp_cmd(dev, cmd);
    return PyErr_Format(Compushady_ComputeError, "Queue submission failed: %d",
                        res);
  }

  Py_BEGIN_ALLOW_THREADS;
  vkWaitForFences(dev->device, 1, &wait_fence, VK_TRUE, UINT64_MAX);
  Py_END_ALLOW_THREADS;

  if (temp_fence != VK_NULL_HANDLE)
    vkDestroyFence(dev->device, temp_fence, NULL);
  free_temp_cmd(dev, cmd);

  if (use_timestamps) {
    PyObject *ts_list = vulkan_device_get_timestamps(dev, total_ts);
    if (!ts_list) {
      return NULL;
    }
    PyObject *result = PyTuple_New(2);
    Py_INCREF(Py_None);
    PyTuple_SetItem(result, 0, Py_None);
    PyTuple_SetItem(result, 1, ts_list);
    return result;
  }

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_Compute_dispatch_tiles
   ------------------------------------------------------------------------- */
PyObject *vulkan_Compute_dispatch_tiles(vulkan_Compute *self, PyObject *args) {
  PyObject *tiles_list;
  uint32_t tile_width, tile_height;
  if (!PyArg_ParseTuple(args, "O!II", &PyList_Type, &tiles_list, &tile_width,
                        &tile_height))
    return NULL;

  Py_ssize_t num_tiles = PyList_Size(tiles_list);
  if (num_tiles == 0) {
    Py_RETURN_NONE;
  }

  vulkan_Device *dev = self->py_device;
  VkCommandBuffer cmd = allocate_temp_cmd(dev);
  if (!cmd) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to allocate command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  vkCmdBindPipeline(cmd, VK_PIPELINE_BIND_POINT_COMPUTE, self->pipeline);
  vkCmdBindDescriptorSets(cmd, VK_PIPELINE_BIND_POINT_COMPUTE,
                          self->pipeline_layout, 0, 1, &self->descriptor_set, 0,
                          NULL);

  uint32_t groups_x = (tile_width + 7) / 8;
  uint32_t groups_y = (tile_height + 7) / 8;

  for (Py_ssize_t i = 0; i < num_tiles; i++) {
    PyObject *tuple = PyList_GetItem(tiles_list, i);
    if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 3) {
      vkEndCommandBuffer(cmd);
      free_temp_cmd(dev, cmd);
      return PyErr_Format(PyExc_TypeError,
                          "Tile entry must be a 3-tuple (tx, ty, push_data)");
    }

    uint32_t tx, ty;
    PyObject *push_obj;
    if (!PyArg_ParseTuple(tuple, "IIO", &tx, &ty, &push_obj)) {
      vkEndCommandBuffer(cmd);
      free_temp_cmd(dev, cmd);
      return NULL;
    }

    Py_buffer push_view;
    if (PyObject_GetBuffer(push_obj, &push_view, PyBUF_SIMPLE) < 0) {
      vkEndCommandBuffer(cmd);
      free_temp_cmd(dev, cmd);
      return NULL;
    }

    if (push_view.len > 0) {
      if ((uint32_t)push_view.len > self->push_constant_size ||
          (push_view.len % 4) != 0) {
        PyBuffer_Release(&push_view);
        vkEndCommandBuffer(cmd);
        free_temp_cmd(dev, cmd);
        return PyErr_Format(PyExc_ValueError,
                            "Invalid push constant size: %zd, expected max %u "
                            "with 4 bytes alignment",
                            push_view.len, self->push_constant_size);
      }
      vkCmdPushConstants(cmd, self->pipeline_layout,
                         VK_SHADER_STAGE_COMPUTE_BIT, 0,
                         (uint32_t)push_view.len, push_view.buf);
    }
    PyBuffer_Release(&push_view);

    vkCmdDispatch(cmd, groups_x, groups_y, 1);

    if (i < num_tiles - 1) {
      VkMemoryBarrier barrier = {VK_STRUCTURE_TYPE_MEMORY_BARRIER};
      barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
      barrier.dstAccessMask = VK_ACCESS_SHADER_READ_BIT;
      vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                           VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 1, &barrier,
                           0, NULL, 0, NULL);
    }
  }

  vkEndCommandBuffer(cmd);

  VkFence fence = self->dispatch_fence;
  vkResetFences(dev->device, 1, &fence);

  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  VkResult res = vkQueueSubmit(dev->queue, 1, &submit, fence);
  if (res != VK_SUCCESS) {
    free_temp_cmd(dev, cmd);
    return PyErr_Format(Compushady_ComputeError, "Queue submission failed: %d",
                        res);
  }

  Py_BEGIN_ALLOW_THREADS;
  vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
  Py_END_ALLOW_THREADS;

  free_temp_cmd(dev, cmd);
  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   bind_cbv, bind_srv, bind_uav (unchanged)
   ------------------------------------------------------------------------- */
PyObject *vulkan_Compute_bind_cbv(vulkan_Compute *self, PyObject *args) {
  uint32_t index;
  PyObject *resource_obj;
  if (!PyArg_ParseTuple(args, "IO", &index, &resource_obj))
    return NULL;

  if (!self->bindless) {
    return PyErr_Format(PyExc_ValueError,
                        "Compute pipeline is not in bindless mode");
  }

  if (!PyObject_TypeCheck(resource_obj, &vulkan_Resource_Type))
    return PyErr_Format(PyExc_ValueError, "Expected a Resource object");

  vulkan_Resource *res = (vulkan_Resource *)resource_obj;
  if (!res->buffer)
    return PyErr_Format(PyExc_ValueError, "Expected a Buffer object");

  if (index >= self->bindless)
    return PyErr_Format(PyExc_ValueError, "Invalid bind index %u (max: %u)",
                        index, self->bindless - 1);

  VkWriteDescriptorSet write = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
  write.dstSet = self->descriptor_set;
  write.dstBinding = index;
  write.descriptorCount = 1;
  write.descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
  write.pBufferInfo = &res->descriptor_buffer_info;

  vkUpdateDescriptorSets(self->py_device->device, 1, &write, 0, NULL);

  Py_INCREF(resource_obj);
  PyList_SetItem(self->py_cbv_list, index, resource_obj);

  Py_RETURN_NONE;
}

PyObject *vulkan_Compute_bind_srv(vulkan_Compute *self, PyObject *args) {
  uint32_t index;
  PyObject *resource_obj;
  if (!PyArg_ParseTuple(args, "IO", &index, &resource_obj))
    return NULL;

  if (!self->bindless) {
    return PyErr_Format(PyExc_ValueError,
                        "Compute pipeline is not in bindless mode");
  }

  if (!PyObject_TypeCheck(resource_obj, &vulkan_Resource_Type))
    return PyErr_Format(PyExc_ValueError, "Expected a Resource object");

  vulkan_Resource *res = (vulkan_Resource *)resource_obj;

  VkDescriptorType type;
  if (res->buffer) {
    type = res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                            : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
  } else {
    type = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
  }

  VkWriteDescriptorSet write = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
  write.dstSet = self->descriptor_set;
  write.dstBinding = 1024 + index;
  write.descriptorCount = 1;
  write.descriptorType = type;
  if (res->buffer) {
    if (res->buffer_view)
      write.pTexelBufferView = &res->buffer_view;
    else
      write.pBufferInfo = &res->descriptor_buffer_info;
  } else {
    write.pImageInfo = &res->descriptor_image_info;
  }

  vkUpdateDescriptorSets(self->py_device->device, 1, &write, 0, NULL);

  Py_INCREF(resource_obj);
  PyList_SetItem(self->py_srv_list, index, resource_obj);

  Py_RETURN_NONE;
}

PyObject *vulkan_Compute_bind_uav(vulkan_Compute *self, PyObject *args) {
  uint32_t index;
  PyObject *resource_obj;
  if (!PyArg_ParseTuple(args, "IO", &index, &resource_obj))
    return NULL;

  if (!self->bindless) {
    return PyErr_Format(PyExc_ValueError,
                        "Compute pipeline is not in bindless mode");
  }

  if (!PyObject_TypeCheck(resource_obj, &vulkan_Resource_Type))
    return PyErr_Format(PyExc_ValueError, "Expected a Resource object");

  vulkan_Resource *res = (vulkan_Resource *)resource_obj;

  VkDescriptorType type;
  if (res->buffer) {
    type = res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                            : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
  } else {
    type = VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
  }

  VkWriteDescriptorSet write = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
  write.dstSet = self->descriptor_set;
  write.dstBinding = 2048 + index;
  write.descriptorCount = 1;
  write.descriptorType = type;
  if (res->buffer) {
    if (res->buffer_view)
      write.pTexelBufferView = &res->buffer_view;
    else
      write.pBufferInfo = &res->descriptor_buffer_info;
  } else {
    write.pImageInfo = &res->descriptor_image_info;
  }

  vkUpdateDescriptorSets(self->py_device->device, 1, &write, 0, NULL);

  Py_INCREF(resource_obj);
  PyList_SetItem(self->py_uav_list, index, resource_obj);

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Method table
   ------------------------------------------------------------------------- */
PyMethodDef vulkan_Compute_methods[] = {
    {"dispatch", (PyCFunction)vulkan_Compute_dispatch, METH_VARARGS,
     "Execute a Compute Pipeline"},
    {"dispatch_indirect", (PyCFunction)vulkan_Compute_dispatch_indirect,
     METH_VARARGS, "Execute an Indirect Compute Pipeline"},
    {"dispatch_indirect_batch",
     (PyCFunction)vulkan_Compute_dispatch_indirect_batch, METH_VARARGS,
     "Execute multiple indirect dispatches from a buffer"},
    {"dispatch_sequence", (PyCFunction)vulkan_Compute_dispatch_sequence,
     METH_VARARGS | METH_KEYWORDS,
     "Execute a sequence of dispatches with optional pre-copy"},
    {"dispatch_tiles", (PyCFunction)vulkan_Compute_dispatch_tiles, METH_VARARGS,
     "Dispatch multiple tiles with per‑tile push constants"},
    {"bind_cbv", (PyCFunction)vulkan_Compute_bind_cbv, METH_VARARGS,
     "Bind a CBV to a Bindless Compute Pipeline"},
    {"bind_srv", (PyCFunction)vulkan_Compute_bind_srv, METH_VARARGS,
     "Bind an SRV to a Bindless Compute Pipeline"},
    {"bind_uav", (PyCFunction)vulkan_Compute_bind_uav, METH_VARARGS,
     "Bind an UAV to a Bindless Compute Pipeline"},
    {NULL, NULL, 0, NULL}};