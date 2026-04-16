#include "vulkan_common.h"
#include <cmath>
#include <cstring>
#include <string>
#include <unordered_map>
#include <vector>

/* ----------------------------------------------------------------------------
   Static helpers
   ------------------------------------------------------------------------- */
static uint32_t get_memory_type_index(VkPhysicalDeviceMemoryProperties *props,
                                      VkMemoryPropertyFlags flags) {
  for (uint32_t i = 0; i < props->memoryTypeCount; i++) {
    if ((props->memoryTypes[i].propertyFlags & flags) == flags)
      return i;
  }
  return 0;
}

/* ----------------------------------------------------------------------------
   vulkan_device_init_timestamps
   ------------------------------------------------------------------------- */
bool vulkan_device_init_timestamps(vulkan_Device *dev, uint32_t max_queries) {
  if (!dev->device)
    return false;
  VkPhysicalDeviceProperties props;
  vkGetPhysicalDeviceProperties(dev->physical_device, &props);
  if (props.limits.timestampComputeAndGraphics == VK_FALSE) {
    dev->supports_timestamps = false;
    return false;
  }
  VkQueryPoolCreateInfo pool_info = {VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO};
  pool_info.queryType = VK_QUERY_TYPE_TIMESTAMP;
  pool_info.queryCount = max_queries;
  VkResult res =
      vkCreateQueryPool(dev->device, &pool_info, NULL, &dev->timestamp_pool);
  if (res != VK_SUCCESS) {
    dev->supports_timestamps = false;
    return false;
  }
  dev->timestamp_count = max_queries;
  dev->timestamp_period = props.limits.timestampPeriod;
  dev->supports_timestamps = true;
  return true;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_get_device
   ------------------------------------------------------------------------- */
vulkan_Device *vulkan_Device_get_device(vulkan_Device *self) {
  if (self->device)
    return self;

  VkPhysicalDevice phys = self->physical_device;
  vkGetPhysicalDeviceMemoryProperties(phys, &self->mem_props);
  vkGetPhysicalDeviceFeatures(phys, &self->features);

  vulkan_device_init_timestamps(self, 128);

  // Find a queue family that supports graphics (and thus compute)
  uint32_t qf_count;
  vkGetPhysicalDeviceQueueFamilyProperties(phys, &qf_count, nullptr);
  VkQueueFamilyProperties *qfs = (VkQueueFamilyProperties *)PyMem_Malloc(
      qf_count * sizeof(VkQueueFamilyProperties));
  vkGetPhysicalDeviceQueueFamilyProperties(phys, &qf_count, qfs);

  uint32_t qf_index = 0;
  for (; qf_index < qf_count; qf_index++) {
    if (qfs[qf_index].queueFlags & VK_QUEUE_GRAPHICS_BIT)
      break;
  }
  PyMem_Free(qfs);
  if (qf_index == qf_count) {
    PyErr_SetString(PyExc_RuntimeError, "No suitable queue family found");
    return NULL;
  }

  float priority = 1.0f;
  VkDeviceQueueCreateInfo qinfo = {VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
  qinfo.queueFamilyIndex = qf_index;
  qinfo.queueCount = 1;
  qinfo.pQueuePriorities = &priority;

  std::vector<const char *> extensions;
  if (vulkan_supports_swapchain)
    extensions.push_back(VK_KHR_SWAPCHAIN_EXTENSION_NAME);

  VkDeviceCreateInfo dinfo = {VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
  dinfo.queueCreateInfoCount = 1;
  dinfo.pQueueCreateInfos = &qinfo;
  dinfo.enabledExtensionCount = (uint32_t)extensions.size();
  dinfo.ppEnabledExtensionNames = extensions.data();

  VkDevice device;
  if (vkCreateDevice(phys, &dinfo, nullptr, &device) != VK_SUCCESS)
    return NULL;

  vkGetDeviceQueue(device, qf_index, 0, &self->queue);
  self->device = device;
  self->queue_family_index = qf_index;

  VkCommandPoolCreateInfo pinfo = {VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
  pinfo.queueFamilyIndex = qf_index;
  pinfo.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
  vkCreateCommandPool(device, &pinfo, nullptr, &self->command_pool);

  VkCommandBufferAllocateInfo ainfo = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
  ainfo.commandPool = self->command_pool;
  ainfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
  ainfo.commandBufferCount = 1;
  vkAllocateCommandBuffers(device, &ainfo, &self->command_buffer);

  // Initialize staging buffer pool if requested
  if (self->buffer_pool_size > 0) {
    self->staging_pool.count = self->buffer_pool_size;
    self->staging_pool.buffers =
        (VkBuffer *)PyMem_Malloc(sizeof(VkBuffer) * self->buffer_pool_size);
    self->staging_pool.memories = (VkDeviceMemory *)PyMem_Malloc(
        sizeof(VkDeviceMemory) * self->buffer_pool_size);
    self->staging_pool.sizes = (VkDeviceSize *)PyMem_Malloc(
        sizeof(VkDeviceSize) * self->buffer_pool_size);
    self->staging_pool.next = 0;
    for (int i = 0; i < self->buffer_pool_size; i++) {
      // create buffers of a reasonable size (e.g., 256KB)
      VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
      binfo.size = 2 * 1024 * 1024;
      binfo.usage =
          VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;
      vkCreateBuffer(device, &binfo, NULL, &self->staging_pool.buffers[i]);
      VkMemoryRequirements req;
      vkGetBufferMemoryRequirements(device, self->staging_pool.buffers[i],
                                    &req);
      VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
      alloc.allocationSize = req.size;
      alloc.memoryTypeIndex = vulkan_get_memory_type_index_by_flag(
          &self->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
      vkAllocateMemory(device, &alloc, NULL, &self->staging_pool.memories[i]);
      vkBindBufferMemory(device, self->staging_pool.buffers[i],
                         self->staging_pool.memories[i], 0);
      self->staging_pool.sizes[i] = 2 * 1024 * 1024;
    }
  }

  return self;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_create_heap
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_create_heap(vulkan_Device *self, PyObject *args) {
  int heap_type;
  uint64_t size;

  if (!PyArg_ParseTuple(args, "iK", &heap_type, &size))
    return NULL;

  if (!size)
    return PyErr_Format(Compushady_HeapError, "zero size heap");

  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device)
    return NULL;

  VkMemoryPropertyFlagBits mem_flag = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
  switch (heap_type) {
  case 0: // DEFAULT
    break;
  case 1: // UPLOAD
    mem_flag = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT;
    break;
  case 2: // READBACK
    mem_flag = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT;
    break;
  default:
    return PyErr_Format(Compushady_HeapError, "Invalid heap type: %d",
                        heap_type);
  }

  vulkan_Heap *py_heap = PyObject_New(vulkan_Heap, &vulkan_Heap_Type);
  if (!py_heap)
    return PyErr_NoMemory();
  memset((char *)py_heap + sizeof(PyObject), 0,
         sizeof(vulkan_Heap) - sizeof(PyObject));
  py_heap->py_device = py_device;
  Py_INCREF(py_heap->py_device);

  VkMemoryAllocateInfo alloc_info = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
  alloc_info.allocationSize = size;
  alloc_info.memoryTypeIndex =
      get_memory_type_index(&self->mem_props, mem_flag);

  VkResult result =
      vkAllocateMemory(py_device->device, &alloc_info, NULL, &py_heap->memory);
  if (result != VK_SUCCESS) {
    Py_DECREF(py_heap);
    return PyErr_Format(Compushady_HeapError,
                        "unable to create vulkan Heap memory");
  }

  py_heap->heap_type = heap_type;
  py_heap->size = size;

  return (PyObject *)py_heap;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_create_buffer
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_create_buffer(vulkan_Device *self, PyObject *args) {
  int heap_type;
  uint64_t size;
  uint32_t stride;
  int format;
  PyObject *py_heap;
  uint64_t heap_offset;
  PyObject *py_sparse;

  if (!PyArg_ParseTuple(args, "iKIiOKO", &heap_type, &size, &stride, &format,
                        &py_heap, &heap_offset, &py_sparse))
    return NULL;

  if (!size)
    return PyErr_Format(Compushady_BufferError, "zero size buffer");

  if (format > 0 && vulkan_formats.find(format) == vulkan_formats.end())
    return PyErr_Format(Compushady_BufferError, "invalid pixel format");

  bool sparse = py_sparse && PyObject_IsTrue(py_sparse);

  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device)
    return NULL;

  if (sparse && !py_device->supports_sparse)
    return PyErr_Format(PyExc_ValueError, "sparse resources are not supported");

  VkBufferCreateInfo buffer_info = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
  buffer_info.size = size;
  buffer_info.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
  buffer_info.usage =
      VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
      VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT | VK_BUFFER_USAGE_STORAGE_BUFFER_BIT |
      VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT |
      VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT |
      VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT;
  if (sparse) {
    buffer_info.flags = VK_BUFFER_CREATE_SPARSE_BINDING_BIT |
                        VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT |
                        VK_BUFFER_CREATE_SPARSE_ALIASED_BIT;
  }

  VkMemoryPropertyFlagBits mem_flag = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
  switch (heap_type) {
  case 0:
    break; // DEFAULT
  case 1:
    mem_flag = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT;
    break; // UPLOAD
  case 2:
    mem_flag = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT;
    break; // READBACK
  default:
    return PyErr_Format(Compushady_BufferError, "Invalid heap type: %d",
                        heap_type);
  }

  vulkan_Resource *py_resource =
      PyObject_New(vulkan_Resource, &vulkan_Resource_Type);
  if (!py_resource)
    return PyErr_NoMemory();
  memset((char *)py_resource + sizeof(PyObject), 0,
         sizeof(vulkan_Resource) - sizeof(PyObject));
  py_resource->py_device = py_device;
  Py_INCREF(py_resource->py_device);

  VkResult result = vkCreateBuffer(py_device->device, &buffer_info, NULL,
                                   &py_resource->buffer);
  if (result != VK_SUCCESS) {
    Py_DECREF(py_resource);
    return PyErr_Format(Compushady_BufferError,
                        "unable to create vulkan Buffer");
  }

  VkMemoryRequirements mem_req;
  vkGetBufferMemoryRequirements(py_device->device, py_resource->buffer,
                                &mem_req);

  if (sparse) {
    py_resource->tile_width = (uint32_t)mem_req.alignment;
    py_resource->tile_height = 1;
    py_resource->tile_depth = 1;
    py_resource->tiles_x =
        (uint32_t)ceil((double)mem_req.size / mem_req.alignment);
    py_resource->tiles_y = 1;
    py_resource->tiles_z = 1;
    heap_offset = 0;
  } else if (py_heap && py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &vulkan_Heap_Type))
      return PyErr_Format(PyExc_ValueError, "Expected a Heap object");
    vulkan_Heap *heap = (vulkan_Heap *)py_heap;
    if (heap->py_device != py_device)
      return PyErr_Format(Compushady_BufferError,
                          "Cannot use heap from a different device");
    if (heap->heap_type != heap_type)
      return PyErr_Format(Compushady_BufferError, "Unsupported heap type");
    if (heap_offset + mem_req.size > heap->size)
      return PyErr_Format(
          Compushady_BufferError,
          "supplied heap is not big enough for the resource size");
    py_resource->memory = heap->memory;
    py_resource->py_heap = heap;
    Py_INCREF(py_resource->py_heap);
  } else {
    VkMemoryAllocateInfo alloc_info = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc_info.allocationSize = mem_req.size;
    alloc_info.memoryTypeIndex =
        get_memory_type_index(&self->mem_props, mem_flag);
    result = vkAllocateMemory(py_device->device, &alloc_info, NULL,
                              &py_resource->memory);
    if (result != VK_SUCCESS) {
      Py_DECREF(py_resource);
      return PyErr_Format(Compushady_BufferError,
                          "unable to create vulkan Buffer memory");
    }
    heap_offset = 0;
  }

  if (!sparse) {
    result = vkBindBufferMemory(py_device->device, py_resource->buffer,
                                py_resource->memory, heap_offset);
    if (result != VK_SUCCESS) {
      Py_DECREF(py_resource);
      return PyErr_Format(Compushady_BufferError,
                          "unable to bind vulkan Buffer memory");
    }
  }

  if (format > 0) {
    py_resource->format = vulkan_formats[format].first;
    VkBufferViewCreateInfo view_info = {
        VK_STRUCTURE_TYPE_BUFFER_VIEW_CREATE_INFO};
    view_info.format = py_resource->format;
    view_info.buffer = py_resource->buffer;
    view_info.range = VK_WHOLE_SIZE;
    result = vkCreateBufferView(py_device->device, &view_info, NULL,
                                &py_resource->buffer_view);
    if (result != VK_SUCCESS) {
      Py_DECREF(py_resource);
      return PyErr_Format(Compushady_BufferError,
                          "unable to create vulkan Buffer View");
    }
  }

  py_resource->size = size;
  py_resource->heap_offset = heap_offset;
  py_resource->stride = stride;
  py_resource->descriptor_buffer_info.buffer = py_resource->buffer;
  py_resource->descriptor_buffer_info.range = size;
  py_resource->heap_size = mem_req.size;
  py_resource->slices = 1;
  py_resource->heap_type = heap_type;

  return (PyObject *)py_resource;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_create_texture2d
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_create_texture2d(vulkan_Device *self, PyObject *args) {
  uint32_t width, height;
  VkFormat format;
  PyObject *py_heap;
  uint64_t heap_offset;
  uint32_t slices;
  PyObject *py_sparse;

  if (!PyArg_ParseTuple(args, "IIiOKIO", &width, &height, &format, &py_heap,
                        &heap_offset, &slices, &py_sparse))
    return NULL;

  if (!width || !height || !slices)
    return PyErr_Format(PyExc_ValueError, "invalid dimensions or slices");

  if (vulkan_formats.find(format) == vulkan_formats.end())
    return PyErr_Format(PyExc_ValueError, "invalid pixel format");

  bool sparse = py_sparse && PyObject_IsTrue(py_sparse);

  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device)
    return NULL;

  if (sparse && !py_device->supports_sparse)
    return PyErr_Format(PyExc_ValueError, "sparse resources are not supported");

  vulkan_Resource *py_resource =
      PyObject_New(vulkan_Resource, &vulkan_Resource_Type);
  if (!py_resource)
    return PyErr_NoMemory();
  memset((char *)py_resource + sizeof(PyObject), 0,
         sizeof(vulkan_Resource) - sizeof(PyObject));
  py_resource->py_device = py_device;
  Py_INCREF(py_resource->py_device);

  py_resource->image = vulkan_create_image(py_device->device, VK_IMAGE_TYPE_2D,
                                           vulkan_formats[format].first, width,
                                           height, 1, slices, sparse);
  if (!py_resource->image) {
    Py_DECREF(py_resource);
    return PyErr_Format(Compushady_Texture2DError,
                        "Failed to create Vulkan image");
  }

  VkMemoryRequirements mem_req;
  vkGetImageMemoryRequirements(py_device->device, py_resource->image, &mem_req);

  if (sparse) {
    uint32_t sparse_req_count = 0;
    vkGetImageSparseMemoryRequirements(py_device->device, py_resource->image,
                                       &sparse_req_count, NULL);
    std::vector<VkSparseImageMemoryRequirements> sparse_reqs(sparse_req_count);
    vkGetImageSparseMemoryRequirements(py_device->device, py_resource->image,
                                       &sparse_req_count, sparse_reqs.data());
    for (auto &req : sparse_reqs) {
      if (req.formatProperties.aspectMask & VK_IMAGE_ASPECT_COLOR_BIT) {
        py_resource->tile_width = req.formatProperties.imageGranularity.width;
        py_resource->tile_height = req.formatProperties.imageGranularity.height;
        py_resource->tile_depth = req.formatProperties.imageGranularity.depth;
        py_resource->tiles_x =
            (uint32_t)ceil((double)width / py_resource->tile_width);
        py_resource->tiles_y =
            (uint32_t)ceil((double)height / py_resource->tile_height);
        py_resource->tiles_z = 1;
        break;
      }
    }
    heap_offset = 0;
  } else if (py_heap && py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &vulkan_Heap_Type))
      return PyErr_Format(PyExc_ValueError, "Expected a Heap object");
    vulkan_Heap *heap = (vulkan_Heap *)py_heap;
    if (heap->py_device != py_device)
      return PyErr_Format(Compushady_Texture2DError,
                          "Cannot use heap from a different device");
    if (heap->heap_type != 0)
      return PyErr_Format(Compushady_Texture2DError, "Unsupported heap type");
    if (heap_offset + mem_req.size > heap->size)
      return PyErr_Format(Compushady_Texture2DError, "heap not big enough");
    py_resource->memory = heap->memory;
    py_resource->py_heap = heap;
    Py_INCREF(py_resource->py_heap);
  } else {
    VkMemoryAllocateInfo alloc_info = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc_info.allocationSize = mem_req.size;
    alloc_info.memoryTypeIndex = get_memory_type_index(
        &self->mem_props, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    VkResult result = vkAllocateMemory(py_device->device, &alloc_info, NULL,
                                       &py_resource->memory);
    if (result != VK_SUCCESS) {
      Py_DECREF(py_resource);
      return PyErr_Format(PyExc_MemoryError,
                          "unable to create vulkan Image memory");
    }
    heap_offset = 0;
  }

  if (!sparse) {
    VkResult result = vkBindImageMemory(py_device->device, py_resource->image,
                                        py_resource->memory, heap_offset);
    if (result != VK_SUCCESS) {
      Py_DECREF(py_resource);
      return PyErr_Format(PyExc_MemoryError,
                          "unable to bind vulkan Image memory");
    }
  }

  VkImageViewCreateInfo view_info = {VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
  view_info.image = py_resource->image;
  view_info.viewType =
      slices > 1 ? VK_IMAGE_VIEW_TYPE_2D_ARRAY : VK_IMAGE_VIEW_TYPE_2D;
  view_info.format = vulkan_formats[format].first;
  view_info.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  view_info.subresourceRange.levelCount = 1;
  view_info.subresourceRange.layerCount = slices;

  VkResult result = vkCreateImageView(py_device->device, &view_info, NULL,
                                      &py_resource->image_view);
  if (result != VK_SUCCESS) {
    Py_DECREF(py_resource);
    return PyErr_Format(PyExc_MemoryError,
                        "unable to create vulkan Image View");
  }

  if (!vulkan_texture_set_layout(py_device, py_resource->image,
                                 VK_IMAGE_LAYOUT_UNDEFINED,
                                 VK_IMAGE_LAYOUT_GENERAL, slices)) {
    Py_DECREF(py_resource);
    return PyErr_Format(PyExc_MemoryError, "unable to set vulkan Image layout");
  }

  py_resource->image_extent.width = width;
  py_resource->image_extent.height = height;
  py_resource->image_extent.depth = 1;
  py_resource->descriptor_image_info.imageView = py_resource->image_view;
  py_resource->descriptor_image_info.imageLayout = VK_IMAGE_LAYOUT_GENERAL;
  py_resource->row_pitch = width * vulkan_formats[format].second;
  py_resource->size = py_resource->row_pitch * height;
  py_resource->heap_offset = heap_offset;
  py_resource->format = view_info.format;
  py_resource->heap_size = mem_req.size;
  py_resource->slices = slices;
  py_resource->heap_type = 0; // DEFAULT

  return (PyObject *)py_resource;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_create_sampler
   ------------------------------------------------------------------------- */
#define COMPUSHADY_VULKAN_SAMPLER_ADDRESS_MODE(ret, var, field)                \
  if (var == 0)                                                                \
    ret = VK_SAMPLER_ADDRESS_MODE_REPEAT;                                      \
  else if (var == 1)                                                           \
    ret = VK_SAMPLER_ADDRESS_MODE_MIRRORED_REPEAT;                             \
  else if (var == 2)                                                           \
    ret = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;                               \
  else                                                                         \
    return PyErr_Format(Compushady_SamplerError,                               \
                        "unsupported address mode for " field)

PyObject *vulkan_Device_create_sampler(vulkan_Device *self, PyObject *args) {
  int addr_u, addr_v, addr_w, filter_min, filter_mag;
  if (!PyArg_ParseTuple(args, "iiiii", &addr_u, &addr_v, &addr_w, &filter_min,
                        &filter_mag))
    return NULL;

  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device)
    return NULL;

  VkSamplerCreateInfo sampler_info = {VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
  COMPUSHADY_VULKAN_SAMPLER_ADDRESS_MODE(sampler_info.addressModeU, addr_u,
                                         "U");
  COMPUSHADY_VULKAN_SAMPLER_ADDRESS_MODE(sampler_info.addressModeV, addr_v,
                                         "V");
  COMPUSHADY_VULKAN_SAMPLER_ADDRESS_MODE(sampler_info.addressModeW, addr_w,
                                         "W");

  if (filter_min == 0 && filter_mag == 0) {
    sampler_info.minFilter = VK_FILTER_NEAREST;
    sampler_info.magFilter = VK_FILTER_NEAREST;
    sampler_info.mipmapMode = VK_SAMPLER_MIPMAP_MODE_NEAREST;
  } else if (filter_min == 1 && filter_mag == 0) {
    sampler_info.minFilter = VK_FILTER_LINEAR;
    sampler_info.magFilter = VK_FILTER_NEAREST;
    sampler_info.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
  } else if (filter_min == 0 && filter_mag == 1) {
    sampler_info.minFilter = VK_FILTER_NEAREST;
    sampler_info.magFilter = VK_FILTER_LINEAR;
    sampler_info.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
  } else if (filter_min == 1 && filter_mag == 1) {
    sampler_info.minFilter = VK_FILTER_LINEAR;
    sampler_info.magFilter = VK_FILTER_LINEAR;
    sampler_info.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
  } else {
    return PyErr_Format(Compushady_SamplerError, "unsupported filter");
  }

  vulkan_Sampler *py_sampler =
      PyObject_New(vulkan_Sampler, &vulkan_Sampler_Type);
  if (!py_sampler)
    return PyErr_NoMemory();
  memset((char *)py_sampler + sizeof(PyObject), 0,
         sizeof(vulkan_Sampler) - sizeof(PyObject));
  py_sampler->py_device = py_device;
  Py_INCREF(py_sampler->py_device);

  VkResult result = vkCreateSampler(py_device->device, &sampler_info, NULL,
                                    &py_sampler->sampler);
  if (result != VK_SUCCESS) {
    Py_DECREF(py_sampler);
    return PyErr_Format(Compushady_SamplerError,
                        "unable to create vulkan Sampler");
  }

  py_sampler->descriptor_image_info.sampler = py_sampler->sampler;
  return (PyObject *)py_sampler;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_create_compute (full bindless + SPIR-V patching)
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_create_compute(vulkan_Device *self, PyObject *args,
                                       PyObject *kwds) {
  const char *kwlist[] = {"shader",   "cbv",       "srv",      "uav",
                          "samplers", "push_size", "bindless", NULL};
  Py_buffer view;
  PyObject *cbv_list = NULL, *srv_list = NULL, *uav_list = NULL,
           *samplers_list = NULL;
  uint32_t push_size = 0;
  uint32_t bindless = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "y*|OOOOII", (char **)kwlist,
                                   &view, &cbv_list, &srv_list, &uav_list,
                                   &samplers_list, &push_size, &bindless))
    return NULL;

  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device) {
    PyBuffer_Release(&view);
    return NULL;
  }

  // Collect resources
  std::vector<vulkan_Resource *> cbv, srv, uav;
  std::vector<vulkan_Sampler *> samplers;
  if (!compushady_check_descriptors(
          &vulkan_Resource_Type, cbv_list, cbv, srv_list, srv, uav_list, uav,
          &vulkan_Sampler_Type, samplers_list, samplers)) {
    PyBuffer_Release(&view);
    return NULL;
  }

  if (bindless > 0 && !py_device->supports_bindless) {
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_ValueError, "Bindless not supported");
  }

  std::vector<VkDescriptorSetLayoutBinding> layout_bindings;
#ifdef VK_EXT_descriptor_indexing
  std::vector<VkDescriptorBindingFlags> layout_bindings_flags;
#endif
  std::vector<VkDescriptorPoolSize> pool_sizes;
  std::unordered_map<VkDescriptorType, std::vector<void *>> descriptors;
  std::vector<VkWriteDescriptorSet> write_descriptor_sets;

  VkShaderModuleCreateInfo shader_info = {
      VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
  shader_info.codeSize = view.len;
  shader_info.pCode = (uint32_t *)view.buf;

  uint32_t binding_offset = 0;

  if (bindless == 0) {
    for (auto *res : cbv) {
      descriptors[VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER].push_back(res);
      VkDescriptorSetLayoutBinding lb = {};
      lb.binding = binding_offset++;
      lb.descriptorCount = 1;
      lb.descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
      lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
      layout_bindings.push_back(lb);
    }
    binding_offset = 1024;
    for (auto *res : srv) {
      VkDescriptorType type =
          res->buffer
              ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                                  : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER)
              : VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
      descriptors[type].push_back(res);
      VkDescriptorSetLayoutBinding lb = {};
      lb.binding = binding_offset++;
      lb.descriptorCount = 1;
      lb.descriptorType = type;
      lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
      layout_bindings.push_back(lb);
    }
    binding_offset = 2048;
    for (auto *res : uav) {
      VkDescriptorType type =
          res->buffer
              ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                                  : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER)
              : VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
      descriptors[type].push_back(res);
      VkDescriptorSetLayoutBinding lb = {};
      lb.binding = binding_offset++;
      lb.descriptorCount = 1;
      lb.descriptorType = type;
      lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
      layout_bindings.push_back(lb);
    }
  } else {
    // Bindless mode (simplified but functional)
    if (cbv.size() > bindless || srv.size() > bindless ||
        uav.size() > bindless) {
      PyBuffer_Release(&view);
      return PyErr_Format(PyExc_ValueError,
                          "Too many initial resources for bindless");
    }
#ifdef VK_EXT_descriptor_indexing
    VkDescriptorBindingFlags flags =
        VK_DESCRIPTOR_BINDING_PARTIALLY_BOUND_BIT |
        VK_DESCRIPTOR_BINDING_UPDATE_AFTER_BIND_BIT;
    for (uint32_t i = 0; i < bindless; i++) {
      VkDescriptorSetLayoutBinding lb = {};
      lb.binding = i;
      lb.descriptorCount = 1;
      lb.descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
      lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
      layout_bindings.push_back(lb);
      layout_bindings_flags.push_back(flags);
    }
    for (uint32_t i = 0; i < bindless; i++) {
      VkDescriptorSetLayoutBinding lb = {};
      lb.binding = 1024 + i;
      lb.descriptorCount = 1;
      lb.descriptorType = VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
      lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
      layout_bindings.push_back(lb);
      layout_bindings_flags.push_back(flags);
    }
    for (uint32_t i = 0; i < bindless; i++) {
      VkDescriptorSetLayoutBinding lb = {};
      lb.binding = 2048 + i;
      lb.descriptorCount = 1;
      lb.descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
      lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
      layout_bindings.push_back(lb);
      layout_bindings_flags.push_back(flags);
    }
#endif
  }

  // Samplers
  binding_offset = 3072;
  for (auto *samp : samplers) {
    descriptors[VK_DESCRIPTOR_TYPE_SAMPLER].push_back(samp);
    VkDescriptorSetLayoutBinding lb = {};
    lb.binding = binding_offset++;
    lb.descriptorCount = 1;
    lb.descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER;
    lb.stageFlags = VK_SHADER_STAGE_COMPUTE_BIT;
    layout_bindings.push_back(lb);
  }

  // SPIR-V patching for BGRA UAVs
  if (!py_device->features.shaderStorageImageReadWithoutFormat) {
    binding_offset = 2048;
    for (auto *res : uav) {
      if (res->image && (res->format == VK_FORMAT_B8G8R8A8_UNORM ||
                         res->format == VK_FORMAT_B8G8R8A8_SRGB)) {
        uint32_t *patched = vulkan_patch_spirv_unknown_uav(
            (uint32_t *)view.buf, view.len, binding_offset);
        if (patched) {
          if (shader_info.pCode != view.buf)
            PyMem_Free((void *)shader_info.pCode);
          shader_info.pCode = patched;
          shader_info.codeSize += 12;
        }
      }
      binding_offset++;
    }
  }

  // Entry point
  const char *entry =
      vulkan_get_spirv_entry_point(shader_info.pCode, shader_info.codeSize);
  if (!entry) {
    if (shader_info.pCode != view.buf)
      PyMem_Free((void *)shader_info.pCode);
    PyBuffer_Release(&view);
    return PyErr_Format(PyExc_ValueError, "Invalid SPIR-V");
  }

  // Create shader module
  VkShaderModule shader_module;
  VkResult res = vkCreateShaderModule(py_device->device, &shader_info, NULL,
                                      &shader_module);
  if (shader_info.pCode != view.buf)
    PyMem_Free((void *)shader_info.pCode);
  PyBuffer_Release(&view);
  if (res != VK_SUCCESS)
    return PyErr_Format(Compushady_ComputeError,
                        "Shader module creation failed");

  // Allocate Compute object
  vulkan_Compute *comp = PyObject_New(vulkan_Compute, &vulkan_Compute_Type);
  if (!comp) {
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    return PyErr_NoMemory();
  }
  memset((char *)comp + sizeof(PyObject), 0,
         sizeof(vulkan_Compute) - sizeof(PyObject));
  comp->py_device = py_device;
  Py_INCREF(py_device);
  comp->shader_module = shader_module;
  comp->push_constant_size = push_size;
  comp->bindless = bindless;

  // Create dispatch fence
  VkFenceCreateInfo finfo = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
  if (vkCreateFence(py_device->device, &finfo, NULL, &comp->dispatch_fence) !=
      VK_SUCCESS) {
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    Py_DECREF(comp);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to create dispatch fence");
  }

  // Descriptor set layout
  VkDescriptorSetLayoutCreateInfo dsl_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
  dsl_info.bindingCount = (uint32_t)layout_bindings.size();
  dsl_info.pBindings = layout_bindings.data();
#ifdef VK_EXT_descriptor_indexing
  VkDescriptorSetLayoutBindingFlagsCreateInfo flags_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_BINDING_FLAGS_CREATE_INFO};
  if (bindless) {
    flags_info.bindingCount = (uint32_t)layout_bindings_flags.size();
    flags_info.pBindingFlags = layout_bindings_flags.data();
    dsl_info.pNext = &flags_info;
    dsl_info.flags = VK_DESCRIPTOR_SET_LAYOUT_CREATE_UPDATE_AFTER_BIND_POOL_BIT;
  }
#endif
  if (vkCreateDescriptorSetLayout(py_device->device, &dsl_info, NULL,
                                  &comp->descriptor_set_layout) != VK_SUCCESS) {
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    Py_DECREF(comp);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to create descriptor set layout");
  }

  // Pipeline layout
  VkPipelineLayoutCreateInfo pl_info = {
      VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
  pl_info.setLayoutCount = 1;
  pl_info.pSetLayouts = &comp->descriptor_set_layout;
  VkPushConstantRange pc_range = {VK_SHADER_STAGE_COMPUTE_BIT, 0, push_size};
  if (push_size) {
    pl_info.pushConstantRangeCount = 1;
    pl_info.pPushConstantRanges = &pc_range;
  }
  if (vkCreatePipelineLayout(py_device->device, &pl_info, NULL,
                             &comp->pipeline_layout) != VK_SUCCESS) {
    vkDestroyDescriptorSetLayout(py_device->device, comp->descriptor_set_layout,
                                 NULL);
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    Py_DECREF(comp);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to create pipeline layout");
  }

  // Compute pipeline
  VkComputePipelineCreateInfo cp_info = {
      VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
  cp_info.stage.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
  cp_info.stage.stage = VK_SHADER_STAGE_COMPUTE_BIT;
  cp_info.stage.module = shader_module;
  cp_info.stage.pName = entry;
  cp_info.layout = comp->pipeline_layout;
  if (vkCreateComputePipelines(py_device->device, VK_NULL_HANDLE, 1, &cp_info,
                               NULL, &comp->pipeline) != VK_SUCCESS) {
    vkDestroyPipelineLayout(py_device->device, comp->pipeline_layout, NULL);
    vkDestroyDescriptorSetLayout(py_device->device, comp->descriptor_set_layout,
                                 NULL);
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    Py_DECREF(comp);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to create compute pipeline");
  }

  // Descriptor pool
  for (auto &pair : descriptors) {
    VkDescriptorPoolSize ps = {pair.first, (uint32_t)pair.second.size()};
    pool_sizes.push_back(ps);
  }
  VkDescriptorPoolCreateInfo dp_info = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
  dp_info.maxSets = 1;
  dp_info.poolSizeCount = (uint32_t)pool_sizes.size();
  dp_info.pPoolSizes = pool_sizes.data();
#ifdef VK_EXT_descriptor_indexing
  if (bindless)
    dp_info.flags = VK_DESCRIPTOR_POOL_CREATE_UPDATE_AFTER_BIND_BIT_EXT;
#endif
  if (vkCreateDescriptorPool(py_device->device, &dp_info, NULL,
                             &comp->descriptor_pool) != VK_SUCCESS) {
    vkDestroyPipeline(py_device->device, comp->pipeline, NULL);
    vkDestroyPipelineLayout(py_device->device, comp->pipeline_layout, NULL);
    vkDestroyDescriptorSetLayout(py_device->device, comp->descriptor_set_layout,
                                 NULL);
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    Py_DECREF(comp);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to create descriptor pool");
  }

  // Allocate descriptor set
  VkDescriptorSetAllocateInfo ds_alloc = {
      VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
  ds_alloc.descriptorPool = comp->descriptor_pool;
  ds_alloc.descriptorSetCount = 1;
  ds_alloc.pSetLayouts = &comp->descriptor_set_layout;
  if (vkAllocateDescriptorSets(py_device->device, &ds_alloc,
                               &comp->descriptor_set) != VK_SUCCESS) {
    vkDestroyDescriptorPool(py_device->device, comp->descriptor_pool, NULL);
    vkDestroyPipeline(py_device->device, comp->pipeline, NULL);
    vkDestroyPipelineLayout(py_device->device, comp->pipeline_layout, NULL);
    vkDestroyDescriptorSetLayout(py_device->device, comp->descriptor_set_layout,
                                 NULL);
    vkDestroyShaderModule(py_device->device, shader_module, NULL);
    Py_DECREF(comp);
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to allocate descriptor set");
  }

  // Write descriptors
  binding_offset = 0;
  for (auto *res : cbv) {
    VkWriteDescriptorSet w = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
    w.dstSet = comp->descriptor_set;
    w.dstBinding = binding_offset++;
    w.descriptorCount = 1;
    w.descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
    w.pBufferInfo = &res->descriptor_buffer_info;
    write_descriptor_sets.push_back(w);
  }
  binding_offset = 1024;
  for (auto *res : srv) {
    VkWriteDescriptorSet w = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
    w.dstSet = comp->descriptor_set;
    w.dstBinding = binding_offset++;
    w.descriptorCount = 1;
    w.descriptorType =
        res->buffer
            ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_UNIFORM_TEXEL_BUFFER
                                : VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER)
            : VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
    if (res->buffer) {
      if (res->buffer_view)
        w.pTexelBufferView = &res->buffer_view;
      else
        w.pBufferInfo = &res->descriptor_buffer_info;
    } else {
      w.pImageInfo = &res->descriptor_image_info;
    }
    write_descriptor_sets.push_back(w);
  }
  binding_offset = 2048;
  for (auto *res : uav) {
    VkWriteDescriptorSet w = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
    w.dstSet = comp->descriptor_set;
    w.dstBinding = binding_offset++;
    w.descriptorCount = 1;
    w.descriptorType =
        res->buffer
            ? (res->buffer_view ? VK_DESCRIPTOR_TYPE_STORAGE_TEXEL_BUFFER
                                : VK_DESCRIPTOR_TYPE_STORAGE_BUFFER)
            : VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
    if (res->buffer) {
      if (res->buffer_view)
        w.pTexelBufferView = &res->buffer_view;
      else
        w.pBufferInfo = &res->descriptor_buffer_info;
    } else {
      w.pImageInfo = &res->descriptor_image_info;
    }
    write_descriptor_sets.push_back(w);
  }
  binding_offset = 3072;
  for (auto *samp : samplers) {
    VkWriteDescriptorSet w = {VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
    w.dstSet = comp->descriptor_set;
    w.dstBinding = binding_offset++;
    w.descriptorCount = 1;
    w.descriptorType = VK_DESCRIPTOR_TYPE_SAMPLER;
    w.pImageInfo = &samp->descriptor_image_info;
    write_descriptor_sets.push_back(w);
  }
  if (!write_descriptor_sets.empty())
    vkUpdateDescriptorSets(py_device->device,
                           (uint32_t)write_descriptor_sets.size(),
                           write_descriptor_sets.data(), 0, NULL);

  // Initialize Python lists for bindless
  size_t num_cbv = bindless ? bindless : cbv.size();
  size_t num_srv = bindless ? bindless : srv.size();
  size_t num_uav = bindless ? bindless : uav.size();
  comp->py_cbv_list = PyList_New(num_cbv);
  comp->py_srv_list = PyList_New(num_srv);
  comp->py_uav_list = PyList_New(num_uav);
  comp->py_samplers_list = PyList_New(0);
  for (size_t i = 0; i < num_cbv; i++) {
    PyObject *item = (i < cbv.size()) ? (PyObject *)cbv[i] : Py_None;
    Py_INCREF(item);
    PyList_SetItem(comp->py_cbv_list, i, item);
  }
  for (size_t i = 0; i < num_srv; i++) {
    PyObject *item = (i < srv.size()) ? (PyObject *)srv[i] : Py_None;
    Py_INCREF(item);
    PyList_SetItem(comp->py_srv_list, i, item);
  }
  for (size_t i = 0; i < num_uav; i++) {
    PyObject *item = (i < uav.size()) ? (PyObject *)uav[i] : Py_None;
    Py_INCREF(item);
    PyList_SetItem(comp->py_uav_list, i, item);
  }
  for (auto *samp : samplers) {
    PyList_Append(comp->py_samplers_list, (PyObject *)samp);
  }

  return (PyObject *)comp;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_create_swapchain
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_create_swapchain(vulkan_Device *self, PyObject *args) {
  PyObject *py_window_handle;
  int format;
  uint32_t num_buffers;
  uint32_t width = 0, height = 0;
  const char *present_mode_str = "fifo";
  if (!PyArg_ParseTuple(args, "OiI|IIs", &py_window_handle, &format,
                        &num_buffers, &width, &height, &present_mode_str))
    return NULL;

  if (vulkan_formats.find(format) == vulkan_formats.end())
    return PyErr_Format(PyExc_ValueError, "invalid pixel format");

  if (!vulkan_supports_swapchain)
    return PyErr_Format(PyExc_Exception, "swapchain not supported");

  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device)
    return NULL;

  vulkan_Swapchain *sc = PyObject_New(vulkan_Swapchain, &vulkan_Swapchain_Type);
  if (!sc)
    return PyErr_NoMemory();
  memset((char *)sc + sizeof(PyObject), 0,
         sizeof(vulkan_Swapchain) - sizeof(PyObject));
  new (&sc->images) std::vector<VkImage>();
  sc->py_device = py_device;
  Py_INCREF(py_device);
  sc->suboptimal = false;
  sc->out_of_date = false;
  sc->image_count = 0;

  VkResult result;

  if (!PyTuple_Check(py_window_handle))
    return PyErr_Format(PyExc_ValueError, "window handle must be a tuple");

  unsigned long display_ptr, window_ptr;
  if (!PyArg_ParseTuple(py_window_handle, "KK", &display_ptr, &window_ptr)) {
    Py_DECREF(sc);
    return NULL;
  }

  VkXlibSurfaceCreateInfoKHR surf_info = {
      VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR};
  surf_info.dpy = (Display *)display_ptr;
  surf_info.window = (Window)window_ptr;
  if (vkCreateXlibSurfaceKHR(vulkan_instance, &surf_info, NULL, &sc->surface) !=
      VK_SUCCESS) {
    Py_DECREF(sc);
    return PyErr_Format(Compushady_SwapchainError,
                        "Failed to create Xlib surface");
  }

  VkBool32 supported;
  vkGetPhysicalDeviceSurfaceSupportKHR(
      self->physical_device, self->queue_family_index, sc->surface, &supported);
  if (!supported) {
    Py_DECREF(sc);
    return PyErr_Format(Compushady_SwapchainError, "Surface not supported");
  }

  VkSurfaceCapabilitiesKHR caps;
  vkGetPhysicalDeviceSurfaceCapabilitiesKHR(self->physical_device, sc->surface,
                                            &caps);
  VkExtent2D extent = caps.currentExtent;
  if (width)
    extent.width = width;
  if (height)
    extent.height = height;

  VkPresentModeKHR desired_mode;
  if (strcmp(present_mode_str, "immediate") == 0) {
    desired_mode = VK_PRESENT_MODE_IMMEDIATE_KHR;
  } else if (strcmp(present_mode_str, "mailbox") == 0) {
    desired_mode = VK_PRESENT_MODE_MAILBOX_KHR;
  } else if (strcmp(present_mode_str, "fifo") == 0) {
    desired_mode = VK_PRESENT_MODE_FIFO_KHR;
  } else {
    PyErr_Format(Compushady_SwapchainError,
                 "Invalid present_mode: '%s'. Must be 'fifo', 'mailbox', or "
                 "'immediate'.",
                 present_mode_str);
    Py_DECREF(sc);
    return NULL;
  }

  // Query available present modes for this surface
  uint32_t present_mode_count = 0;
  vkGetPhysicalDeviceSurfacePresentModesKHR(self->physical_device, sc->surface,
                                            &present_mode_count, NULL);
  VkPresentModeKHR *available_modes = (VkPresentModeKHR *)PyMem_Malloc(
      present_mode_count * sizeof(VkPresentModeKHR));
  if (!available_modes) {
    Py_DECREF(sc);
    return PyErr_NoMemory();
  }
  vkGetPhysicalDeviceSurfacePresentModesKHR(
      self->physical_device, sc->surface, &present_mode_count, available_modes);

  // Check if desired mode is supported; fallback to FIFO if not
  bool supported_mode = false;
  for (uint32_t i = 0; i < present_mode_count; i++) {
    if (available_modes[i] == desired_mode) {
      supported_mode = true;
      break;
    }
  }
  VkPresentModeKHR selected_mode =
      supported_mode ? desired_mode : VK_PRESENT_MODE_FIFO_KHR;
  PyMem_Free(available_modes);

  // Optional: log a debug message if falling back
  if (!supported_mode && vulkan_debug) {
    char msg[256];
    snprintf(
        msg, sizeof(msg),
        "[Compushady] Present mode '%s' not supported, falling back to FIFO",
        present_mode_str);
    vulkan_debug_messages.push_back(msg);
  }

  VkSwapchainCreateInfoKHR swapchain_info = {
      VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR};
  swapchain_info.surface = sc->surface;
  swapchain_info.minImageCount = num_buffers;
  swapchain_info.imageFormat = vulkan_formats[format].first;
  swapchain_info.imageColorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR;
  swapchain_info.imageExtent = extent;
  swapchain_info.imageArrayLayers = 1;
  swapchain_info.imageUsage = VK_IMAGE_USAGE_TRANSFER_DST_BIT;
  swapchain_info.preTransform = caps.currentTransform;
  swapchain_info.presentMode = selected_mode;
  swapchain_info.clipped = VK_TRUE;

  VkCompositeAlphaFlagBitsKHR compositeAlpha =
      VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
  if (!(caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR)) {
    if (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR)
      compositeAlpha = VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR;
    else {
      // Find first supported bit
      VkCompositeAlphaFlagBitsKHR bits[] = {
          VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
          VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR,
          VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR,
          VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR};
      compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR; // fallback
      for (auto bit : bits) {
        if (caps.supportedCompositeAlpha & bit) {
          compositeAlpha = bit;
          break;
        }
      }
    }
  }
  swapchain_info.compositeAlpha = compositeAlpha;

  result = vkCreateSwapchainKHR(py_device->device, &swapchain_info, NULL,
                                &sc->swapchain);
  if (result != VK_SUCCESS) {
    Py_DECREF(sc);
    return PyErr_Format(Compushady_SwapchainError,
                        "Failed to create swapchain");
  }

  vkGetSwapchainImagesKHR(py_device->device, sc->swapchain, &sc->image_count,
                          NULL);
  sc->images.resize(sc->image_count);
  vkGetSwapchainImagesKHR(py_device->device, sc->swapchain, &sc->image_count,
                          sc->images.data());
  sc->image_extent = extent;

  // Allocate fences
  sc->fences = (VkFence *)PyMem_Malloc(sizeof(VkFence) * sc->image_count);
  VkFenceCreateInfo finfo = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
  for (uint32_t i = 0; i < sc->image_count; i++) {
    vkCreateFence(py_device->device, &finfo, NULL, &sc->fences[i]);
  }

  VkSemaphoreCreateInfo sem_info = {VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO};
  vkCreateSemaphore(py_device->device, &sem_info, NULL, &sc->copy_semaphore);
  vkCreateSemaphore(py_device->device, &sem_info, NULL, &sc->present_semaphore);

  for (VkImage img : sc->images) {
    vulkan_texture_set_layout(py_device, img, VK_IMAGE_LAYOUT_UNDEFINED,
                              VK_IMAGE_LAYOUT_PRESENT_SRC_KHR, 1);
  }

  return (PyObject *)sc;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_get_debug_messages
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_get_debug_messages(vulkan_Device *self,
                                           PyObject *args) {
  PyObject *list = PyList_New(0);
  for (const auto &msg : vulkan_debug_messages)
    PyList_Append(list, PyUnicode_FromString(msg.c_str()));
  vulkan_debug_messages.clear();
  return list;
}

/* ----------------------------------------------------------------------------
   Device dealloc
   ------------------------------------------------------------------------- */
static void vulkan_Device_dealloc(vulkan_Device *self) {
  Py_XDECREF(self->name);
  if (self->device) {
    vkDeviceWaitIdle(self->device);
    if (self->staging_pool.count > 0) {
      for (int i = 0; i < self->staging_pool.count; i++) {
        vkDestroyBuffer(self->device, self->staging_pool.buffers[i], NULL);
        vkFreeMemory(self->device, self->staging_pool.memories[i], NULL);
      }
      PyMem_Free(self->staging_pool.buffers);
      PyMem_Free(self->staging_pool.memories);
      PyMem_Free(self->staging_pool.sizes);
    }
    if (self->command_buffer)
      vkFreeCommandBuffers(self->device, self->command_pool, 1,
                           &self->command_buffer);
    if (self->command_pool)
      vkDestroyCommandPool(self->device, self->command_pool, NULL);
    vkDestroyDevice(self->device, NULL);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* ----------------------------------------------------------------------------
   vulkan_Device_set_buffer_pool_size
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_set_buffer_pool_size(vulkan_Device *self,
                                             PyObject *args) {
  int size;
  if (!PyArg_ParseTuple(args, "i", &size))
    return NULL;
  self->buffer_pool_size = size;
  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_Device_wait_idle
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_wait_idle(vulkan_Device *self, PyObject *args) {
  vulkan_Device *py_device = vulkan_Device_get_device(self);
  if (!py_device)
    return NULL;
  VkResult result = vkQueueWaitIdle(py_device->queue);
  if (result != VK_SUCCESS) {
    return PyErr_Format(PyExc_RuntimeError, "vkQueueWaitIdle failed: %d",
                        result);
  }
  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Device type definition
   ------------------------------------------------------------------------- */
static PyMethodDef vulkan_Device_methods[] = {
    {"create_heap", (PyCFunction)vulkan_Device_create_heap, METH_VARARGS, NULL},
    {"create_buffer", (PyCFunction)vulkan_Device_create_buffer, METH_VARARGS,
     NULL},
    {"create_texture2d", (PyCFunction)vulkan_Device_create_texture2d,
     METH_VARARGS, NULL},
    {"create_sampler", (PyCFunction)vulkan_Device_create_sampler, METH_VARARGS,
     NULL},
    {"create_compute", (PyCFunction)vulkan_Device_create_compute,
     METH_VARARGS | METH_KEYWORDS, NULL},
    {"create_swapchain", (PyCFunction)vulkan_Device_create_swapchain,
     METH_VARARGS, NULL},
    {"get_debug_messages", (PyCFunction)vulkan_Device_get_debug_messages,
     METH_NOARGS, NULL},
    {"set_buffer_pool_size", (PyCFunction)vulkan_Device_set_buffer_pool_size,
     METH_VARARGS, NULL},
    {"wait_idle", (PyCFunction)vulkan_Device_wait_idle, METH_NOARGS, NULL},
    {NULL}};

static PyMemberDef vulkan_Device_members[] = {
    {"name", T_OBJECT_EX, offsetof(vulkan_Device, name), 0, NULL},
    {"dedicated_video_memory", T_ULONGLONG,
     offsetof(vulkan_Device, dedicated_video_memory), 0, NULL},
    {"dedicated_system_memory", T_ULONGLONG,
     offsetof(vulkan_Device, dedicated_system_memory), 0, NULL},
    {"shared_system_memory", T_ULONGLONG,
     offsetof(vulkan_Device, shared_system_memory), 0, NULL},
    {"vendor_id", T_UINT, offsetof(vulkan_Device, vendor_id), 0, NULL},
    {"device_id", T_UINT, offsetof(vulkan_Device, device_id), 0, NULL},
    {"is_hardware", T_BOOL, offsetof(vulkan_Device, is_hardware), 0, NULL},
    {"is_discrete", T_BOOL, offsetof(vulkan_Device, is_discrete), 0, NULL},
    {NULL}};

PyTypeObject vulkan_Device_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Device",
    .tp_basicsize = sizeof(vulkan_Device),
    .tp_dealloc = (destructor)vulkan_Device_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vulkan_Device_methods,
    .tp_members = vulkan_Device_members,
};