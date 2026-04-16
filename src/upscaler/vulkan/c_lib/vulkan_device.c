/**
 * @file vulkan_device.c
 * @brief Implementation of the Vulkan device Python type.
 *
 * This module provides the Device class with methods to create resources
 * (heaps, buffers, textures, samplers, compute pipelines, swapchains) and
 * manage the underlying logical device.
 */

#include "vulkan_device.h"
#include "vulkan_compute.h"
#include "vulkan_swapchain.h"
#include "vulkan_utils.h"
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------------------------------
   Device member table
   ------------------------------------------------------------------------- */
static PyMemberDef VkComp_Device_members[] = {
    {"name", Py_T_OBJECT_EX, offsetof(VkComp_Device, name), 0, "Device name"},
    {"dedicated_video_memory", Py_T_ULONGLONG,
     offsetof(VkComp_Device, dedicated_video_memory), 0,
     "Dedicated video memory in bytes"},
    {"dedicated_system_memory", Py_T_ULONGLONG,
     offsetof(VkComp_Device, dedicated_system_memory), 0,
     "Dedicated system memory in bytes"},
    {"shared_system_memory", Py_T_ULONGLONG,
     offsetof(VkComp_Device, shared_system_memory), 0,
     "Shared system memory in bytes"},
    {"vendor_id", Py_T_UINT, offsetof(VkComp_Device, vendor_id), 0,
     "PCI vendor ID"},
    {"device_id", Py_T_UINT, offsetof(VkComp_Device, device_id), 0,
     "PCI device ID"},
    {"is_hardware", Py_T_BOOL, offsetof(VkComp_Device, is_hardware), 0,
     "True if hardware accelerated"},
    {"is_discrete", Py_T_BOOL, offsetof(VkComp_Device, is_discrete), 0,
     "True if discrete GPU"},
    {NULL}};

/* -------------------------------------------------------------------------
   Method table for the Device type
   ------------------------------------------------------------------------- */
static PyMethodDef VkComp_Device_methods[] = {
    {"create_heap", (PyCFunction)VkComp_Device_CreateHeap, METH_VARARGS,
     "Create a memory heap."},
    {"create_buffer", (PyCFunction)VkComp_Device_CreateBuffer, METH_VARARGS,
     "Create a buffer resource."},
    {"create_texture2d", (PyCFunction)VkComp_Device_CreateTexture2D,
     METH_VARARGS, "Create a 2D texture resource."},
    {"create_sampler", (PyCFunction)VkComp_Device_CreateSampler, METH_VARARGS,
     "Create a sampler object."},
    {"create_compute", (PyCFunction)VkComp_Device_CreateCompute,
     METH_VARARGS | METH_KEYWORDS, "Create a compute pipeline."},
    {"create_swapchain", (PyCFunction)VkComp_Device_CreateSwapchain,
     METH_VARARGS, "Create a swapchain for presentation."},
    {"get_debug_messages", (PyCFunction)VkComp_Device_GetDebugMessages,
     METH_NOARGS, "Retrieve accumulated debug messages (if debug enabled)."},
    {"set_buffer_pool_size", (PyCFunction)VkComp_Device_SetBufferPoolSize,
     METH_VARARGS, "Set the size of the staging buffer pool."},
    {"wait_idle", (PyCFunction)VkComp_Device_WaitIdle, METH_NOARGS,
     "Wait for all GPU work to finish."},
    {NULL, NULL, 0, NULL}};

/* -------------------------------------------------------------------------
   Device type definition
   ------------------------------------------------------------------------- */
PyTypeObject VkComp_Device_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Device",
    .tp_basicsize = sizeof(VkComp_Device),
    .tp_dealloc = (destructor)VkComp_Device_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = VkComp_Device_methods,
    .tp_members = VkComp_Device_members,
    .tp_new = VkComp_Device_New,
};

/* -------------------------------------------------------------------------
   Internal helper: create logical device and supporting objects
   ------------------------------------------------------------------------- */
static VkResult create_logical_device(VkComp_Device *dev) {
  /* Enable Vulkan 1.3 features */
  VkPhysicalDeviceVulkan13Features vk13_features = {
      .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES,
      .synchronization2 = VK_TRUE,
      .dynamicRendering = VK_TRUE,
      .maintenance4 = VK_TRUE,
  };

  VkPhysicalDeviceFeatures2 features2 = {
      .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2,
      .pNext = &vk13_features,
  };
  vkGetPhysicalDeviceFeatures2(dev->physical_device, &features2);

  /* Find a queue family with compute + graphics support */
  uint32_t qf_count = 0;
  vkGetPhysicalDeviceQueueFamilyProperties(dev->physical_device, &qf_count,
                                           NULL);
  VkQueueFamilyProperties *qf_props =
      PyMem_Malloc(qf_count * sizeof(VkQueueFamilyProperties));
  if (!qf_props)
    return VK_ERROR_OUT_OF_HOST_MEMORY;
  vkGetPhysicalDeviceQueueFamilyProperties(dev->physical_device, &qf_count,
                                           qf_props);

  uint32_t qf_index = 0;
  for (; qf_index < qf_count; ++qf_index) {
    if ((qf_props[qf_index].queueFlags &
         (VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT)) ==
        (VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT)) {
      break;
    }
  }
  if (qf_index == qf_count) {
    /* Fallback to any queue that supports compute */
    for (qf_index = 0; qf_index < qf_count; ++qf_index) {
      if (qf_props[qf_index].queueFlags & VK_QUEUE_COMPUTE_BIT)
        break;
    }
  }
  PyMem_Free(qf_props);
  if (qf_index == qf_count)
    return VK_ERROR_INITIALIZATION_FAILED;

  dev->queue_family_index = qf_index;

  float priority = 1.0f;
  VkDeviceQueueCreateInfo qci = {
      .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
      .queueFamilyIndex = qf_index,
      .queueCount = 1,
      .pQueuePriorities = &priority,
  };

  const char *extensions[] = {
      VK_KHR_SWAPCHAIN_EXTENSION_NAME,
  };
  uint32_t ext_count = dev->supports_swapchain ? 1 : 0;

  VkDeviceCreateInfo dci = {
      .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
      .pNext = &vk13_features,
      .queueCreateInfoCount = 1,
      .pQueueCreateInfos = &qci,
      .enabledExtensionCount = ext_count,
      .ppEnabledExtensionNames = extensions,
  };

  VkResult res = vkCreateDevice(dev->physical_device, &dci, NULL, &dev->device);
  if (res != VK_SUCCESS)
    return res;

  vkGetDeviceQueue(dev->device, qf_index, 0, &dev->queue);
  dev->vulkan13_features = vk13_features;
  dev->features = features2.features;

  /* Command pool */
  VkCommandPoolCreateInfo cpci = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
      .flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
      .queueFamilyIndex = qf_index,
  };
  res = vkCreateCommandPool(dev->device, &cpci, NULL, &dev->command_pool);
  if (res != VK_SUCCESS)
    return res;

  /* Timeline semaphore */
  VkSemaphoreTypeCreateInfo stci = {
      .sType = VK_STRUCTURE_TYPE_SEMAPHORE_TYPE_CREATE_INFO,
      .semaphoreType = VK_SEMAPHORE_TYPE_TIMELINE,
      .initialValue = 0,
  };
  VkSemaphoreCreateInfo sci = {
      .sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO,
      .pNext = &stci,
  };
  vkCreateSemaphore(dev->device, &sci, NULL, &dev->timeline_semaphore);

  /* Timestamp queries */
  vkGetPhysicalDeviceProperties(dev->physical_device, &dev->props);
  if (dev->props.limits.timestampComputeAndGraphics) {
    dev->supports_timestamps = VK_TRUE;
    dev->timestamp_period = dev->props.limits.timestampPeriod;
    dev->timestamp_count = 128;
    VkQueryPoolCreateInfo qpci = {
        .sType = VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO,
        .queryType = VK_QUERY_TYPE_TIMESTAMP,
        .queryCount = dev->timestamp_count,
    };
    vkCreateQueryPool(dev->device, &qpci, NULL, &dev->timestamp_pool);
  }

  /* Feature flags – bindless (descriptor indexing) */
  VkPhysicalDeviceDescriptorIndexingFeatures indexing_features = {
      .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DESCRIPTOR_INDEXING_FEATURES,
  };
  VkPhysicalDeviceFeatures2 features2_bindless = {
      .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2,
      .pNext = &indexing_features,
  };
  vkGetPhysicalDeviceFeatures2(dev->physical_device, &features2_bindless);
  dev->supports_bindless =
      indexing_features.descriptorBindingPartiallyBound &&
      indexing_features.runtimeDescriptorArray &&
      indexing_features.shaderSampledImageArrayNonUniformIndexing;

  dev->supports_sparse =
      dev->features.sparseBinding && dev->features.sparseResidencyBuffer;

  return VK_SUCCESS;
}

/* -------------------------------------------------------------------------
   Public: ensure device is active (lazy creation)
   ------------------------------------------------------------------------- */
VkComp_Device *VkComp_Device_GetActive(VkComp_Device *self) {
  if (self->device)
    return self;
  VkResult res = create_logical_device(self);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError,
                 "Failed to create Vulkan logical device: %d", res);
    return NULL;
  }
  return self;
}

/* -------------------------------------------------------------------------
   Python constructor (called when device objects are created during
   enumeration)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_New(PyTypeObject *type, PyObject *args,
                            PyObject *kwds) {
  VkComp_Device *self = (VkComp_Device *)type->tp_alloc(type, 0);
  if (!self)
    return NULL;
  memset((char *)self + sizeof(PyObject), 0,
         sizeof(VkComp_Device) - sizeof(PyObject));
  return (PyObject *)self;
}

/* -------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
void VkComp_Device_Dealloc(VkComp_Device *self) {
  Py_XDECREF(self->name);
  if (self->device) {
    vkDeviceWaitIdle(self->device);
    if (self->staging_pool.count > 0) {
      for (uint32_t i = 0; i < self->staging_pool.count; ++i) {
        vkDestroyBuffer(self->device, self->staging_pool.buffers[i], NULL);
        vkFreeMemory(self->device, self->staging_pool.memories[i], NULL);
      }
      PyMem_Free(self->staging_pool.buffers);
      PyMem_Free(self->staging_pool.memories);
      PyMem_Free(self->staging_pool.sizes);
    }
    if (self->timestamp_pool)
      vkDestroyQueryPool(self->device, self->timestamp_pool, NULL);
    if (self->timeline_semaphore)
      vkDestroySemaphore(self->device, self->timeline_semaphore, NULL);
    if (self->command_pool)
      vkDestroyCommandPool(self->device, self->command_pool, NULL);
    vkDestroyDevice(self->device, NULL);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* -------------------------------------------------------------------------
   Command buffer helpers
   ------------------------------------------------------------------------- */
VkResult VkComp_Device_AllocateCmd(VkComp_Device *device,
                                   VkCommandBuffer *pCmd) {
  VkCommandBufferAllocateInfo alloc_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
      .commandPool = device->command_pool,
      .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
      .commandBufferCount = 1,
  };
  return vkAllocateCommandBuffers(device->device, &alloc_info, pCmd);
}

void VkComp_Device_FreeCmd(VkComp_Device *device, VkCommandBuffer cmd) {
  if (cmd)
    vkFreeCommandBuffers(device->device, device->command_pool, 1, &cmd);
}

VkResult VkComp_Device_SubmitAndWait(VkComp_Device *device, VkCommandBuffer cmd,
                                     VkFence fence) {
  uint64_t signal_value = ++device->timeline_value;

  VkTimelineSemaphoreSubmitInfo timeline_info = {
      .sType = VK_STRUCTURE_TYPE_TIMELINE_SEMAPHORE_SUBMIT_INFO,
      .signalSemaphoreValueCount = 1,
      .pSignalSemaphoreValues = &signal_value,
  };

  VkSubmitInfo submit_info = {
      .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
      .pNext = &timeline_info,
      .commandBufferCount = 1,
      .pCommandBuffers = &cmd,
      .signalSemaphoreCount = 1,
      .pSignalSemaphores = &device->timeline_semaphore,
  };

  VkResult res = vkQueueSubmit(device->queue, 1, &submit_info, fence);
  if (res != VK_SUCCESS)
    return res;

  VkSemaphoreWaitInfo wait_info = {
      .sType = VK_STRUCTURE_TYPE_SEMAPHORE_WAIT_INFO,
      .semaphoreCount = 1,
      .pSemaphores = &device->timeline_semaphore,
      .pValues = &signal_value,
  };

  Py_BEGIN_ALLOW_THREADS res =
      vkWaitSemaphores(device->device, &wait_info, UINT64_MAX);
  Py_END_ALLOW_THREADS

      if (fence != VK_NULL_HANDLE) {
    vkResetFences(device->device, 1, &fence);
  }
  return res;
}

/* -------------------------------------------------------------------------
   Staging buffer pool management
   ------------------------------------------------------------------------- */
VkResult VkComp_Device_AcquireStagingBuffer(VkComp_Device *device,
                                            VkDeviceSize size,
                                            VkBuffer *pBuffer,
                                            VkDeviceMemory *pMemory,
                                            VkBool32 *pFromPool) {
  if (device->staging_pool.count > 0) {
    /* Check if the requested size fits in our fixed‑size pool buffers */
    if (size > device->staging_pool.fixed_size) {
      /* Fallback to fresh allocation */
      goto allocate_fresh;
    }
    uint32_t idx = device->staging_pool.next;
    device->staging_pool.next = (idx + 1) % device->staging_pool.count;
    *pBuffer = device->staging_pool.buffers[idx];
    *pMemory = device->staging_pool.memories[idx];
    *pFromPool = VK_TRUE;
    return VK_SUCCESS;
  }

allocate_fresh:
  /* Allocate a one‑off staging buffer */
  VkBufferCreateInfo buffer_info = {
      .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
      .size = size,
      .usage =
          VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
      .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
  };
  VkResult res = vkCreateBuffer(device->device, &buffer_info, NULL, pBuffer);
  if (res != VK_SUCCESS)
    return res;

  VkMemoryRequirements mem_req;
  vkGetBufferMemoryRequirements(device->device, *pBuffer, &mem_req);
  uint32_t mem_type =
      vkcomp_find_memory_type(&device->mem_props, mem_req.memoryTypeBits,
                              VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                                  VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
  VkMemoryAllocateInfo alloc_info = {
      .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
      .allocationSize = mem_req.size,
      .memoryTypeIndex = mem_type,
  };
  res = vkAllocateMemory(device->device, &alloc_info, NULL, pMemory);
  if (res != VK_SUCCESS) {
    vkDestroyBuffer(device->device, *pBuffer, NULL);
    return res;
  }
  vkBindBufferMemory(device->device, *pBuffer, *pMemory, 0);
  *pFromPool = VK_FALSE;
  return VK_SUCCESS;
}

void VkComp_Device_ReleaseStagingBuffer(VkComp_Device *device, VkBuffer buffer,
                                        VkDeviceMemory memory,
                                        VkBool32 fromPool) {
  if (!fromPool) {
    vkDestroyBuffer(device->device, buffer, NULL);
    vkFreeMemory(device->device, memory, NULL);
  }
  /* If from pool, do nothing – it will be reused. */
}

/* -------------------------------------------------------------------------
   Python method: create_heap(heap_type, size) -> Heap
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateHeap(VkComp_Device *self, PyObject *args) {
  int heap_type;
  unsigned long long size;
  if (!PyArg_ParseTuple(args, "iK", &heap_type, &size))
    return NULL;

  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;

  if (size == 0) {
    PyErr_SetString(VkComp_HeapError, "Heap size cannot be zero");
    return NULL;
  }

  VkMemoryPropertyFlags mem_flags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
  if (heap_type == 1 /* UPLOAD */ || heap_type == 2 /* READBACK */) {
    mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
  }

  VkComp_Heap *heap = PyObject_New(VkComp_Heap, &VkComp_Heap_Type);
  if (!heap)
    return PyErr_NoMemory();
  memset((char *)heap + sizeof(PyObject), 0,
         sizeof(VkComp_Heap) - sizeof(PyObject));
  heap->device = dev;
  Py_INCREF(dev);
  heap->heap_type = heap_type;
  heap->size = size;

  VkMemoryAllocateInfo alloc_info = {
      .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
      .allocationSize = size,
      .memoryTypeIndex =
          vkcomp_find_memory_type(&dev->mem_props, 0xFFFFFFFF, mem_flags),
  };
  VkResult res =
      vkAllocateMemory(dev->device, &alloc_info, NULL, &heap->memory);
  if (res != VK_SUCCESS) {
    Py_DECREF(heap);
    PyErr_Format(VkComp_HeapError, "Failed to allocate heap memory: %d", res);
    return NULL;
  }

  return (PyObject *)heap;
}

/* -------------------------------------------------------------------------
   Python method: create_buffer(...) -> Resource
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateBuffer(VkComp_Device *self, PyObject *args) {
  int heap_type, format;
  unsigned long long size;
  unsigned int stride;
  PyObject *py_heap = Py_None;
  unsigned long long heap_offset = 0;
  PyObject *py_sparse = Py_False;

  if (!PyArg_ParseTuple(args, "iKIi|OKO", &heap_type, &size, &stride, &format,
                        &py_heap, &heap_offset, &py_sparse))
    return NULL;

  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;

  if (size == 0) {
    PyErr_SetString(VkComp_BufferError, "Buffer size cannot be zero");
    return NULL;
  }

  VkBool32 sparse = PyObject_IsTrue(py_sparse);
  if (sparse && !dev->supports_sparse) {
    PyErr_SetString(VkComp_BufferError,
                    "Sparse buffers not supported on this device");
    return NULL;
  }

  VkBufferCreateInfo buffer_info = {
      .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
      .size = size,
      .usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
               VK_BUFFER_USAGE_TRANSFER_DST_BIT |
               VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT |
               VK_BUFFER_USAGE_STORAGE_BUFFER_BIT |
               VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT |
               VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT |
               VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT,
      .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
  };
  if (sparse) {
    buffer_info.flags = VK_BUFFER_CREATE_SPARSE_BINDING_BIT |
                        VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT;
  }

  VkComp_Resource *res_obj =
      PyObject_New(VkComp_Resource, &VkComp_Resource_Type);
  if (!res_obj)
    return PyErr_NoMemory();
  memset((char *)res_obj + sizeof(PyObject), 0,
         sizeof(VkComp_Resource) - sizeof(PyObject));
  res_obj->device = dev;
  Py_INCREF(dev);
  res_obj->size = size;
  res_obj->stride = stride;
  res_obj->heap_type = heap_type;

  VkResult vr =
      vkCreateBuffer(dev->device, &buffer_info, NULL, &res_obj->buffer);
  if (vr != VK_SUCCESS) {
    Py_DECREF(res_obj);
    PyErr_Format(VkComp_BufferError, "Failed to create buffer: %d", vr);
    return NULL;
  }

  VkMemoryRequirements mem_req;
  vkGetBufferMemoryRequirements(dev->device, res_obj->buffer, &mem_req);
  res_obj->heap_size = mem_req.size;

  if (sparse) {
    /* Sparse buffers: no memory bound initially; tile information stored */
    res_obj->tile_width = (uint32_t)mem_req.alignment;
    res_obj->tile_height = 1;
    res_obj->tile_depth = 1;
    res_obj->tiles_x =
        (uint32_t)((mem_req.size + mem_req.alignment - 1) / mem_req.alignment);
    res_obj->tiles_y = 1;
    res_obj->tiles_z = 1;
  } else if (py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &VkComp_Heap_Type)) {
      Py_DECREF(res_obj);
      PyErr_SetString(PyExc_TypeError, "Expected a Heap object");
      return NULL;
    }
    VkComp_Heap *heap = (VkComp_Heap *)py_heap;
    if (heap->device != dev) {
      Py_DECREF(res_obj);
      PyErr_SetString(VkComp_BufferError, "Heap belongs to a different device");
      return NULL;
    }
    if (heap->heap_type != heap_type) {
      Py_DECREF(res_obj);
      PyErr_SetString(VkComp_BufferError, "Heap type mismatch");
      return NULL;
    }
    if (heap_offset + mem_req.size > heap->size) {
      Py_DECREF(res_obj);
      PyErr_SetString(VkComp_BufferError, "Heap insufficient size");
      return NULL;
    }
    res_obj->memory = heap->memory;
    res_obj->heap = heap;
    Py_INCREF(heap);
    res_obj->heap_offset = heap_offset;
  } else {
    VkMemoryPropertyFlags mem_flags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
    if (heap_type == 1 /* UPLOAD */ || heap_type == 2 /* READBACK */) {
      mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                  VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
    }
    VkMemoryAllocateInfo alloc_info = {
        .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
        .allocationSize = mem_req.size,
        .memoryTypeIndex = vkcomp_find_memory_type(
            &dev->mem_props, mem_req.memoryTypeBits, mem_flags),
    };
    vr = vkAllocateMemory(dev->device, &alloc_info, NULL, &res_obj->memory);
    if (vr != VK_SUCCESS) {
      Py_DECREF(res_obj);
      PyErr_Format(VkComp_BufferError, "Failed to allocate buffer memory: %d",
                   vr);
      return NULL;
    }
    res_obj->heap_offset = 0;
  }

  if (!sparse) {
    vr = vkBindBufferMemory(dev->device, res_obj->buffer, res_obj->memory,
                            res_obj->heap_offset);
    if (vr != VK_SUCCESS) {
      Py_DECREF(res_obj);
      PyErr_Format(VkComp_BufferError, "Failed to bind buffer memory: %d", vr);
      return NULL;
    }
  }

  /* Create buffer view if format specified */
  if (format > 0 &&
      g_vulkan_format_table[format].vk_format != VK_FORMAT_UNDEFINED) {
    res_obj->format = g_vulkan_format_table[format].vk_format;
    VkBufferViewCreateInfo view_info = {
        .sType = VK_STRUCTURE_TYPE_BUFFER_VIEW_CREATE_INFO,
        .buffer = res_obj->buffer,
        .format = res_obj->format,
        .range = VK_WHOLE_SIZE,
    };
    vr = vkCreateBufferView(dev->device, &view_info, NULL,
                            &res_obj->buffer_view);
    if (vr != VK_SUCCESS) {
      Py_DECREF(res_obj);
      PyErr_Format(VkComp_BufferError, "Failed to create buffer view: %d", vr);
      return NULL;
    }
  }

  res_obj->descriptor_buffer_info.buffer = res_obj->buffer;
  res_obj->descriptor_buffer_info.offset = 0;
  res_obj->descriptor_buffer_info.range = size;
  res_obj->slices = 1;

  return (PyObject *)res_obj;
}

/* -------------------------------------------------------------------------
   Python method: create_texture2d(...) -> Resource
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateTexture2D(VkComp_Device *self, PyObject *args) {
  unsigned int width, height, slices;
  int format;
  PyObject *py_heap = Py_None;
  unsigned long long heap_offset = 0;
  PyObject *py_sparse = Py_False;

  if (!PyArg_ParseTuple(args, "IIi|OKIO", &width, &height, &format, &py_heap,
                        &heap_offset, &slices, &py_sparse))
    return NULL;

  if (width == 0 || height == 0 || slices == 0) {
    PyErr_SetString(VkComp_Texture2DError,
                    "Dimensions and slices must be non-zero");
    return NULL;
  }

  if (g_vulkan_format_table[format].vk_format == VK_FORMAT_UNDEFINED) {
    PyErr_SetString(VkComp_Texture2DError, "Invalid pixel format");
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;

  VkBool32 sparse = PyObject_IsTrue(py_sparse);
  if (sparse && !dev->supports_sparse) {
    PyErr_SetString(VkComp_Texture2DError,
                    "Sparse textures not supported on this device");
    return NULL;
  }

  VkComp_Resource *res_obj =
      PyObject_New(VkComp_Resource, &VkComp_Resource_Type);
  if (!res_obj)
    return PyErr_NoMemory();
  memset((char *)res_obj + sizeof(PyObject), 0,
         sizeof(VkComp_Resource) - sizeof(PyObject));
  res_obj->device = dev;
  Py_INCREF(dev);
  res_obj->image_extent.width = width;
  res_obj->image_extent.height = height;
  res_obj->image_extent.depth = 1;
  res_obj->format = g_vulkan_format_table[format].vk_format;
  res_obj->slices = slices;
  res_obj->row_pitch = width * g_vulkan_format_table[format].bytes_per_pixel;
  res_obj->size = res_obj->row_pitch * height * slices;
  res_obj->heap_type = 0; /* Textures always device-local */

  VkImageCreateInfo image_info = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,
      .imageType = VK_IMAGE_TYPE_2D,
      .format = res_obj->format,
      .extent = {width, height, 1},
      .mipLevels = 1,
      .arrayLayers = slices,
      .samples = VK_SAMPLE_COUNT_1_BIT,
      .tiling = VK_IMAGE_TILING_OPTIMAL,
      .usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT |
               VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT |
               VK_IMAGE_USAGE_STORAGE_BIT,
      .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
      .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
  };
  if (sparse) {
    image_info.flags = VK_IMAGE_CREATE_SPARSE_BINDING_BIT |
                       VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT;
  }

  VkResult vr = vkCreateImage(dev->device, &image_info, NULL, &res_obj->image);
  if (vr != VK_SUCCESS) {
    Py_DECREF(res_obj);
    PyErr_Format(VkComp_Texture2DError, "Failed to create image: %d", vr);
    return NULL;
  }

  VkMemoryRequirements mem_req;
  vkGetImageMemoryRequirements(dev->device, res_obj->image, &mem_req);
  res_obj->heap_size = mem_req.size;

  if (sparse) {
    /* Get sparse image requirements to determine tile size */
    uint32_t sparse_req_count = 0;
    vkGetImageSparseMemoryRequirements(dev->device, res_obj->image,
                                       &sparse_req_count, NULL);
    VkSparseImageMemoryRequirements *sparse_reqs = PyMem_Malloc(
        sparse_req_count * sizeof(VkSparseImageMemoryRequirements));
    if (sparse_reqs) {
      vkGetImageSparseMemoryRequirements(dev->device, res_obj->image,
                                         &sparse_req_count, sparse_reqs);
      for (uint32_t i = 0; i < sparse_req_count; ++i) {
        if (sparse_reqs[i].formatProperties.aspectMask &
            VK_IMAGE_ASPECT_COLOR_BIT) {
          res_obj->tile_width =
              sparse_reqs[i].formatProperties.imageGranularity.width;
          res_obj->tile_height =
              sparse_reqs[i].formatProperties.imageGranularity.height;
          res_obj->tile_depth =
              sparse_reqs[i].formatProperties.imageGranularity.depth;
          res_obj->tiles_x =
              (width + res_obj->tile_width - 1) / res_obj->tile_width;
          res_obj->tiles_y =
              (height + res_obj->tile_height - 1) / res_obj->tile_height;
          res_obj->tiles_z = 1;
          break;
        }
      }
      PyMem_Free(sparse_reqs);
    }
  } else if (py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &VkComp_Heap_Type)) {
      Py_DECREF(res_obj);
      PyErr_SetString(PyExc_TypeError, "Expected a Heap object");
      return NULL;
    }
    VkComp_Heap *heap = (VkComp_Heap *)py_heap;
    if (heap->device != dev) {
      Py_DECREF(res_obj);
      PyErr_SetString(VkComp_Texture2DError,
                      "Heap belongs to a different device");
      return NULL;
    }
    if (heap->heap_type != 0) {
      Py_DECREF(res_obj);
      PyErr_SetString(VkComp_Texture2DError, "Textures require a DEFAULT heap");
      return NULL;
    }
    if (heap_offset + mem_req.size > heap->size) {
      Py_DECREF(res_obj);
      PyErr_SetString(VkComp_Texture2DError, "Heap insufficient size");
      return NULL;
    }
    res_obj->memory = heap->memory;
    res_obj->heap = heap;
    Py_INCREF(heap);
    res_obj->heap_offset = heap_offset;
  } else {
    VkMemoryAllocateInfo alloc_info = {
        .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
        .allocationSize = mem_req.size,
        .memoryTypeIndex =
            vkcomp_find_memory_type(&dev->mem_props, mem_req.memoryTypeBits,
                                    VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT),
    };
    vr = vkAllocateMemory(dev->device, &alloc_info, NULL, &res_obj->memory);
    if (vr != VK_SUCCESS) {
      Py_DECREF(res_obj);
      PyErr_Format(VkComp_Texture2DError, "Failed to allocate image memory: %d",
                   vr);
      return NULL;
    }
    res_obj->heap_offset = 0;
  }

  if (!sparse) {
    vr = vkBindImageMemory(dev->device, res_obj->image, res_obj->memory,
                           res_obj->heap_offset);
    if (vr != VK_SUCCESS) {
      Py_DECREF(res_obj);
      PyErr_Format(VkComp_Texture2DError, "Failed to bind image memory: %d",
                   vr);
      return NULL;
    }
  }

  /* Create image view */
  VkImageViewCreateInfo view_info = {
      .sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
      .image = res_obj->image,
      .viewType =
          slices > 1 ? VK_IMAGE_VIEW_TYPE_2D_ARRAY : VK_IMAGE_VIEW_TYPE_2D,
      .format = res_obj->format,
      .subresourceRange =
          {
              .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
              .baseMipLevel = 0,
              .levelCount = 1,
              .baseArrayLayer = 0,
              .layerCount = slices,
          },
  };
  vr = vkCreateImageView(dev->device, &view_info, NULL, &res_obj->image_view);
  if (vr != VK_SUCCESS) {
    Py_DECREF(res_obj);
    PyErr_Format(VkComp_Texture2DError, "Failed to create image view: %d", vr);
    return NULL;
  }

  /* Transition to GENERAL layout */
  if (!vkcomp_texture_set_layout(dev, res_obj->image, VK_IMAGE_LAYOUT_UNDEFINED,
                                 VK_IMAGE_LAYOUT_GENERAL, slices)) {
    Py_DECREF(res_obj);
    PyErr_SetString(VkComp_Texture2DError, "Failed to transition image layout");
    return NULL;
  }

  res_obj->descriptor_image_info.imageView = res_obj->image_view;
  res_obj->descriptor_image_info.imageLayout = VK_IMAGE_LAYOUT_GENERAL;

  return (PyObject *)res_obj;
}

/* -------------------------------------------------------------------------
   Python method: create_sampler(...) -> Sampler
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateSampler(VkComp_Device *self, PyObject *args) {
  int addr_u, addr_v, addr_w, filter_min, filter_mag;
  if (!PyArg_ParseTuple(args, "iiiii", &addr_u, &addr_v, &addr_w, &filter_min,
                        &filter_mag))
    return NULL;

  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;

  VkSamplerAddressMode mode_table[] = {
      VK_SAMPLER_ADDRESS_MODE_REPEAT,
      VK_SAMPLER_ADDRESS_MODE_MIRRORED_REPEAT,
      VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE,
  };
  if (addr_u < 0 || addr_u > 2 || addr_v < 0 || addr_v > 2 || addr_w < 0 ||
      addr_w > 2) {
    PyErr_SetString(VkComp_SamplerError, "Invalid address mode");
    return NULL;
  }

  VkFilter min_filter =
      (filter_min == 0) ? VK_FILTER_NEAREST : VK_FILTER_LINEAR;
  VkFilter mag_filter =
      (filter_mag == 0) ? VK_FILTER_NEAREST : VK_FILTER_LINEAR;
  VkSamplerMipmapMode mip_mode = (filter_min == 0)
                                     ? VK_SAMPLER_MIPMAP_MODE_NEAREST
                                     : VK_SAMPLER_MIPMAP_MODE_LINEAR;

  VkSamplerCreateInfo sampler_info = {
      .sType = VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO,
      .magFilter = mag_filter,
      .minFilter = min_filter,
      .mipmapMode = mip_mode,
      .addressModeU = mode_table[addr_u],
      .addressModeV = mode_table[addr_v],
      .addressModeW = mode_table[addr_w],
      .mipLodBias = 0.0f,
      .anisotropyEnable = VK_FALSE,
      .maxAnisotropy = 1.0f,
      .compareEnable = VK_FALSE,
      .minLod = 0.0f,
      .maxLod = 0.0f,
      .borderColor = VK_BORDER_COLOR_FLOAT_TRANSPARENT_BLACK,
      .unnormalizedCoordinates = VK_FALSE,
  };

  VkComp_Sampler *sampler = PyObject_New(VkComp_Sampler, &VkComp_Sampler_Type);
  if (!sampler)
    return PyErr_NoMemory();
  memset((char *)sampler + sizeof(PyObject), 0,
         sizeof(VkComp_Sampler) - sizeof(PyObject));
  sampler->device = dev;
  Py_INCREF(dev);

  VkResult vr =
      vkCreateSampler(dev->device, &sampler_info, NULL, &sampler->sampler);
  if (vr != VK_SUCCESS) {
    Py_DECREF(sampler);
    PyErr_Format(VkComp_SamplerError, "Failed to create sampler: %d", vr);
    return NULL;
  }

  sampler->descriptor_image_info.sampler = sampler->sampler;
  return (PyObject *)sampler;
}

/* -------------------------------------------------------------------------
   Python method: create_compute(...) -> Compute
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateCompute(VkComp_Device *self, PyObject *args,
                                      PyObject *kwds) {
  static char *kwlist[] = {"shader",   "cbv",       "srv",      "uav",
                           "samplers", "push_size", "bindless", NULL};
  Py_buffer shader_view;
  PyObject *cbv_list = NULL;
  PyObject *srv_list = NULL;
  PyObject *uav_list = NULL;
  PyObject *samplers_list = NULL;
  unsigned int push_size = 0;
  unsigned int bindless_max = 0;

  if (!PyArg_ParseTupleAndKeywords(
          args, kwds, "y*|OOOOII", kwlist, &shader_view, &cbv_list, &srv_list,
          &uav_list, &samplers_list, &push_size, &bindless_max))
    return NULL;

  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev) {
    PyBuffer_Release(&shader_view);
    return NULL;
  }

  VkComp_Compute *comp =
      VkComp_Compute_Create(dev, &shader_view, cbv_list, srv_list, uav_list,
                            samplers_list, push_size, bindless_max);
  PyBuffer_Release(&shader_view);
  return (PyObject *)comp;
}

/* -------------------------------------------------------------------------
   Python method: create_swapchain(...) -> Swapchain
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateSwapchain(VkComp_Device *self, PyObject *args) {
  PyObject *window_handle;
  int format;
  unsigned int num_buffers;
  unsigned int width = 0, height = 0;
  const char *present_mode = "fifo";

  if (!PyArg_ParseTuple(args, "OiI|IIs", &window_handle, &format, &num_buffers,
                        &width, &height, &present_mode))
    return NULL;

  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;

  return (PyObject *)VkComp_Swapchain_Create(
      dev, window_handle, format, num_buffers, width, height, present_mode);
}

/* -------------------------------------------------------------------------
   Python method: get_debug_messages() -> list of strings
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_GetDebugMessages(VkComp_Device *self, PyObject *args) {
  extern PyObject *vulkan_get_and_clear_debug_messages(void);
  return vulkan_get_and_clear_debug_messages();
}

/* -------------------------------------------------------------------------
   Python method: set_buffer_pool_size(size)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_SetBufferPoolSize(VkComp_Device *self, PyObject *args) {
  int size;
  if (!PyArg_ParseTuple(args, "i", &size))
    return NULL;
  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;

  /* Destroy existing pool */
  if (dev->staging_pool.count > 0) {
    for (uint32_t i = 0; i < dev->staging_pool.count; i++) {
      vkDestroyBuffer(dev->device, dev->staging_pool.buffers[i], NULL);
      vkFreeMemory(dev->device, dev->staging_pool.memories[i], NULL);
    }
    PyMem_Free(dev->staging_pool.buffers);
    PyMem_Free(dev->staging_pool.memories);
    PyMem_Free(dev->staging_pool.sizes);
    dev->staging_pool.count = 0;
  }

  if (size > 0) {
    dev->staging_pool.count = (uint32_t)size;
    dev->staging_pool.fixed_size = 2 * 1024 * 1024; /* 2 MB default */
    dev->staging_pool.next = 0;

    dev->staging_pool.buffers = PyMem_Malloc(size * sizeof(VkBuffer));
    dev->staging_pool.memories = PyMem_Malloc(size * sizeof(VkDeviceMemory));
    dev->staging_pool.sizes = PyMem_Malloc(size * sizeof(VkDeviceSize));
    if (!dev->staging_pool.buffers || !dev->staging_pool.memories ||
        !dev->staging_pool.sizes) {
      PyMem_Free(dev->staging_pool.buffers);
      PyMem_Free(dev->staging_pool.memories);
      PyMem_Free(dev->staging_pool.sizes);
      dev->staging_pool.count = 0;
      return PyErr_NoMemory();
    }

    for (uint32_t i = 0; i < dev->staging_pool.count; i++) {
      VkBufferCreateInfo buffer_info = {
          .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
          .size = dev->staging_pool.fixed_size,
          .usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
                   VK_BUFFER_USAGE_TRANSFER_DST_BIT,
          .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
      };
      VkResult res = vkCreateBuffer(dev->device, &buffer_info, NULL,
                                    &dev->staging_pool.buffers[i]);
      if (res != VK_SUCCESS) {
        /* cleanup on error */
        for (uint32_t j = 0; j < i; j++) {
          vkDestroyBuffer(dev->device, dev->staging_pool.buffers[j], NULL);
          vkFreeMemory(dev->device, dev->staging_pool.memories[j], NULL);
        }
        PyMem_Free(dev->staging_pool.buffers);
        PyMem_Free(dev->staging_pool.memories);
        PyMem_Free(dev->staging_pool.sizes);
        dev->staging_pool.count = 0;
        PyErr_Format(PyExc_RuntimeError, "Failed to create staging buffer: %d",
                     res);
        return NULL;
      }

      VkMemoryRequirements mem_req;
      vkGetBufferMemoryRequirements(dev->device, dev->staging_pool.buffers[i],
                                    &mem_req);
      uint32_t mem_type =
          vkcomp_find_memory_type(&dev->mem_props, mem_req.memoryTypeBits,
                                  VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                                      VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
      VkMemoryAllocateInfo alloc_info = {
          .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
          .allocationSize = mem_req.size,
          .memoryTypeIndex = mem_type,
      };
      res = vkAllocateMemory(dev->device, &alloc_info, NULL,
                             &dev->staging_pool.memories[i]);
      if (res != VK_SUCCESS) {
        vkDestroyBuffer(dev->device, dev->staging_pool.buffers[i], NULL);
        for (uint32_t j = 0; j < i; j++) {
          vkDestroyBuffer(dev->device, dev->staging_pool.buffers[j], NULL);
          vkFreeMemory(dev->device, dev->staging_pool.memories[j], NULL);
        }
        PyMem_Free(dev->staging_pool.buffers);
        PyMem_Free(dev->staging_pool.memories);
        PyMem_Free(dev->staging_pool.sizes);
        dev->staging_pool.count = 0;
        PyErr_Format(PyExc_RuntimeError,
                     "Failed to allocate staging memory: %d", res);
        return NULL;
      }
      vkBindBufferMemory(dev->device, dev->staging_pool.buffers[i],
                         dev->staging_pool.memories[i], 0);
      dev->staging_pool.sizes[i] = dev->staging_pool.fixed_size;
    }
  }
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   Python method: wait_idle()
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_WaitIdle(VkComp_Device *self, PyObject *args) {
  VkComp_Device *dev = VkComp_Device_GetActive(self);
  if (!dev)
    return NULL;
  vkQueueWaitIdle(dev->queue);
  Py_RETURN_NONE;
}