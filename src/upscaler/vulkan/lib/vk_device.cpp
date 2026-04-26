/**
 * @file vk_device.cpp
 * @brief Vulkan logical device encapsulation.
 *
 * This module implements the `vk.Device` Python type - the central hub for
 * all Vulkan resource creation. A `vk_Device` wraps a single physical device
 * and, on first use, creates a logical device, a single graphics/compute
 * queue, a command pool, a pipeline cache, optional timestamp pool, and a
 * small staging buffer pool for efficient host-device transfers.
 *
 * The initialisation is **lazy**: calling `vk_Device_get_initialized()` will
 * transparently set up the logical device and ancillary objects on the first
 * call. Subsequent calls return immediately. This avoids expensive device
 * creation at import / discovery time.
 *
 * Resource creation methods (`create_heap`, `create_buffer`,
 * `create_texture2d`, `create_sampler`, `create_compute`, `create_swapchain`)
 * all require a ready device and will initialise it automatically.
 *
 * Synchronisation:
 *   - `wait_idle()` drains the queue synchronously.
 *   - `wait_for_fences()` exposes a generic multi-fence wait with timeout;
 *      it is the building block for frame-level synchronisation.
 *
 * Memory management:
 *   - Heaps (`vk.Heap`) are simple VkDeviceMemory blocks exposed to Python
 *      for manual sub-allocation.
 *   - Buffers and textures can either own their memory or be bound to a heap.
 *   - A small pool of reusable staging buffers (mappable, host-coherent)
 *      supports efficient uploads / downloads.
 */

#include "vk_device.h"
#include "vk_instance.h"
#include "vk_utils.h"
#include <cmath>
#include <cstring>
#include <unordered_set>

/* -------------------------------------------------------------------------
 * Forward declarations - types and helpers defined in other modules
 * ------------------------------------------------------------------------- */
extern PyTypeObject vk_Heap_Type;
extern PyTypeObject vk_Resource_Type;
extern PyTypeObject vk_Compute_Type;
extern PyTypeObject vk_Swapchain_Type;
extern PyTypeObject vk_Sampler_Type;

extern PyMethodDef vk_Resource_methods[];
extern PyMethodDef vk_Compute_methods[];
extern PyMethodDef vk_Swapchain_methods[];

// Actual implementations live in vk_compute.cpp and vk_swapchain.cpp
extern PyObject *vk_Device_create_compute_impl(vk_Device *self, PyObject *args,
                                               PyObject *kwds);
extern PyObject *vk_Device_create_swapchain_impl(vk_Device *self,
                                                 PyObject *args);

/* -------------------------------------------------------------------------
 * Forwarding wrappers - kept thin so that the bulk of the code resides
 * in the respective module.
 * ------------------------------------------------------------------------- */
PyObject *vk_Device_create_compute(vk_Device *self, PyObject *args,
                                   PyObject *kwds) {
  return vk_Device_create_compute_impl(self, args, kwds);
}

PyObject *vk_Device_create_swapchain(vk_Device *self, PyObject *args) {
  return vk_Device_create_swapchain_impl(self, args);
}

// =============================================================================
//  Internal helpers
// =============================================================================

/**
 * Allocate a `VkDeviceMemory` block of @p size bytes with the required
 * memory property flags. On failure a Python exception is set.
 *
 * @param dev        Fully initialised device.
 * @param size       Size in bytes.
 * @param mem_flags  Required `VkMemoryPropertyFlags`.
 * @param out_memory Receives the allocated memory handle.
 * @return `true` on success, `false` with Python exception.
 */
static bool allocate_device_memory(vk_Device *dev, VkDeviceSize size,
                                   VkMemoryPropertyFlags mem_flags,
                                   VkDeviceMemory *out_memory) {
  uint32_t mem_type_idx = vk_find_memory_type_index(&dev->mem_props, mem_flags);
  if (mem_type_idx == UINT32_MAX) {
    PyErr_Format(vk_HeapError, "No suitable memory type found for flags 0x%x",
                 mem_flags);
    return false;
  }

  VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
  alloc.allocationSize = size;
  alloc.memoryTypeIndex = mem_type_idx;

  VkResult res = vkAllocateMemory(dev->device, &alloc, nullptr, out_memory);
  if (res != VK_SUCCESS) {
    PyErr_Format(vk_HeapError, "Failed to allocate %llu bytes (error %d)", size,
                 res);
    return false;
  }
  return true;
}

/**
 * Create a raw `VkImage` without binding memory or creating an image view.
 * Useful as a building block for `create_texture2d`.
 *
 * @param device          Logical device.
 * @param type            Image type (1D, 2D, 3D).
 * @param format          Image format.
 * @param width,height,
 *        depth           Image dimensions.
 * @param slices          Number of array layers.
 * @param sparse          Create with sparse residency flags.
 * @return The newly created image, or `VK_NULL_HANDLE` on error.
 */
static VkImage create_vk_image(VkDevice device, VkImageType type,
                               VkFormat format, uint32_t width, uint32_t height,
                               uint32_t depth, uint32_t slices, bool sparse) {
  VkImageCreateInfo info = {VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
  info.imageType = type;
  info.format = format;
  info.extent = {width, height, depth};
  info.mipLevels = 1;
  info.arrayLayers = slices;
  info.samples = VK_SAMPLE_COUNT_1_BIT;
  info.tiling = VK_IMAGE_TILING_OPTIMAL;
  info.usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT |
               VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT |
               VK_IMAGE_USAGE_STORAGE_BIT;
  info.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;

  if (sparse) {
    info.flags = VK_IMAGE_CREATE_SPARSE_BINDING_BIT |
                 VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT |
                 VK_IMAGE_CREATE_SPARSE_ALIASED_BIT;
  }

  VkImage image;
  VkResult res = vkCreateImage(device, &info, nullptr, &image);
  return (res == VK_SUCCESS) ? image : VK_NULL_HANDLE;
}

// =============================================================================
//  Lifecycle - allocation and deallocation
// =============================================================================

/**
 * Destroy all Vulkan objects owned by the device and free Python resources.
 * The queue is idled first to ensure no command is in flight.
 */
void vk_Device_dealloc(vk_Device *self) {
  Py_XDECREF(self->name);
  if (self->device) {
    vkDeviceWaitIdle(self->device);

    // Release the staging buffer pool
    if (self->staging_pool.count > 0) {
      for (int i = 0; i < self->staging_pool.count; i++) {
        vkDestroyBuffer(self->device, self->staging_pool.buffers[i], nullptr);
        vkFreeMemory(self->device, self->staging_pool.memories[i], nullptr);
      }
      PyMem_Free(self->staging_pool.buffers);
      PyMem_Free(self->staging_pool.memories);
      PyMem_Free(self->staging_pool.sizes);
    }

    if (self->internal_cmd_buffer)
      vkFreeCommandBuffers(self->device, self->command_pool, 1,
                           &self->internal_cmd_buffer);
    if (self->command_pool)
      vkDestroyCommandPool(self->device, self->command_pool, nullptr);
    if (self->pipeline_cache)
      vkDestroyPipelineCache(self->device, self->pipeline_cache, nullptr);
    if (self->timestamp_pool)
      vkDestroyQueryPool(self->device, self->timestamp_pool, nullptr);
    vkDestroyDevice(self->device, nullptr);
  }
  Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/**
 * Ensure that `self` has a fully operational logical device and associated
 * resources (command pool, queue, staging pool, ...). This is the only place
 * where the logical device is created; it is idempotent and thread-safe
 * because it returns early when `self->device` is already valid.
 *
 * @return `self` on success, `NULL` with a Python exception on failure.
 */
vk_Device *vk_Device_get_initialized(vk_Device *self) {
  if (self->device != VK_NULL_HANDLE)
    return self; // already initialised

  if (!vk_instance_ensure())
    return nullptr; // Python exception already set

  VkPhysicalDevice phys = self->physical_device;

  // ---- Query physical device properties and features ----
  vkGetPhysicalDeviceMemoryProperties(phys, &self->mem_props);
  vkGetPhysicalDeviceFeatures(phys, &self->features);

  VkPhysicalDeviceVulkan12Features features12 = {
      VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES};
  VkPhysicalDeviceFeatures2 features2 = {
      VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2, &features12};
  vkGetPhysicalDeviceFeatures2(phys, &features2);
  self->features12 = features12;

  // Determine optional feature support flags
  self->supports_bindless =
      features12.descriptorIndexing &&
      features12.shaderSampledImageArrayNonUniformIndexing &&
      features12.shaderStorageImageArrayNonUniformIndexing &&
      features12.shaderUniformBufferArrayNonUniformIndexing &&
      features12.shaderStorageBufferArrayNonUniformIndexing;
  self->supports_sparse = self->features.sparseBinding &&
                          self->features.sparseResidencyBuffer &&
                          self->features.sparseResidencyImage2D;

  // ---- Select a queue family with graphics+compute ----
  uint32_t qf_count;
  vkGetPhysicalDeviceQueueFamilyProperties(phys, &qf_count, nullptr);
  std::vector<VkQueueFamilyProperties> qf_props(qf_count);
  vkGetPhysicalDeviceQueueFamilyProperties(phys, &qf_count, qf_props.data());

  uint32_t qf_index = 0;
  for (; qf_index < qf_count; ++qf_index) {
    if (qf_props[qf_index].queueFlags & VK_QUEUE_GRAPHICS_BIT)
      break;
  }
  if (qf_index == qf_count) {
    PyErr_SetString(PyExc_RuntimeError,
                    "No queue family with graphics support found");
    return nullptr;
  }
  self->queue_family_index = qf_index;

  // ---- Create logical device ----
  float queue_priority = 1.0f;
  VkDeviceQueueCreateInfo qinfo = {VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
  qinfo.queueFamilyIndex = qf_index;
  qinfo.queueCount = 1;
  qinfo.pQueuePriorities = &queue_priority;

  std::vector<const char *> extensions;
  if (vk_supports_swapchain)
    extensions.push_back(VK_KHR_SWAPCHAIN_EXTENSION_NAME);

  // Enable features that are actually available
  VkPhysicalDeviceFeatures enabled_features = {};
  enabled_features.shaderStorageImageReadWithoutFormat =
      self->features.shaderStorageImageReadWithoutFormat;
  enabled_features.shaderStorageImageWriteWithoutFormat =
      self->features.shaderStorageImageWriteWithoutFormat;
  enabled_features.sparseBinding = self->features.sparseBinding;
  enabled_features.sparseResidencyBuffer = self->features.sparseResidencyBuffer;
  enabled_features.sparseResidencyImage2D =
      self->features.sparseResidencyImage2D;

  VkDeviceCreateInfo dinfo = {VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
  dinfo.pNext = &features12;
  dinfo.queueCreateInfoCount = 1;
  dinfo.pQueueCreateInfos = &qinfo;
  dinfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
  dinfo.ppEnabledExtensionNames = extensions.data();
  dinfo.pEnabledFeatures = &enabled_features;

  VkResult res = vkCreateDevice(phys, &dinfo, nullptr, &self->device);
  VK_CHECK_OR_RETURN_NULL(res, PyExc_RuntimeError,
                          "Failed to create logical device");

  vkGetDeviceQueue(self->device, qf_index, 0, &self->queue);

  // ---- Command pool (one for the whole device) ----
  VkCommandPoolCreateInfo pinfo = {VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
  pinfo.queueFamilyIndex = qf_index;
  pinfo.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
  vkCreateCommandPool(self->device, &pinfo, nullptr, &self->command_pool);

  // A single, persistent internal command buffer for short sync operations.
  VkCommandBufferAllocateInfo ainfo = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
  ainfo.commandPool = self->command_pool;
  ainfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
  ainfo.commandBufferCount = 1;
  vkAllocateCommandBuffers(self->device, &ainfo, &self->internal_cmd_buffer);

  // ---- Pipeline cache (shared across all pipelines) ----
  VkPipelineCacheCreateInfo cinfo = {
      VK_STRUCTURE_TYPE_PIPELINE_CACHE_CREATE_INFO};
  vkCreatePipelineCache(self->device, &cinfo, nullptr, &self->pipeline_cache);

  // ---- Timestamp query pool (if supported) ----
  VkPhysicalDeviceProperties props;
  vkGetPhysicalDeviceProperties(phys, &props);
  if (props.limits.timestampComputeAndGraphics) {
    VkQueryPoolCreateInfo qpinfo = {VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO};
    qpinfo.queryType = VK_QUERY_TYPE_TIMESTAMP;
    qpinfo.queryCount = 128;
    if (vkCreateQueryPool(self->device, &qpinfo, nullptr,
                          &self->timestamp_pool) == VK_SUCCESS) {
      self->timestamp_count = 128;
      self->timestamp_period = props.limits.timestampPeriod;
      self->supports_timestamps = true;
    }
  }

  // ---- Staging buffer pool (reusable, host-visible/coherent) ----
  const int DEFAULT_POOL_SIZE = 4;
  const VkDeviceSize DEFAULT_BUFFER_SIZE = 2 * 1024 * 1024; // 2 MiB
  self->staging_pool.count = DEFAULT_POOL_SIZE;
  self->staging_pool.buffers =
      (VkBuffer *)PyMem_Malloc(sizeof(VkBuffer) * DEFAULT_POOL_SIZE);
  self->staging_pool.memories = (VkDeviceMemory *)PyMem_Malloc(
      sizeof(VkDeviceMemory) * DEFAULT_POOL_SIZE);
  self->staging_pool.sizes =
      (VkDeviceSize *)PyMem_Malloc(sizeof(VkDeviceSize) * DEFAULT_POOL_SIZE);
  if (!self->staging_pool.buffers || !self->staging_pool.memories ||
      !self->staging_pool.sizes) {
    PyErr_NoMemory();
    return nullptr;
  }
  self->staging_pool.next = 0;

  for (int i = 0; i < DEFAULT_POOL_SIZE; ++i) {
    VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    binfo.size = DEFAULT_BUFFER_SIZE;
    binfo.usage =
        VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    vkCreateBuffer(self->device, &binfo, nullptr,
                   &self->staging_pool.buffers[i]);

    VkMemoryRequirements req;
    vkGetBufferMemoryRequirements(self->device, self->staging_pool.buffers[i],
                                  &req);
    VkMemoryAllocateInfo alloc = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    alloc.allocationSize = req.size;
    alloc.memoryTypeIndex = vk_find_memory_type_index(
        &self->mem_props, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                              VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    vkAllocateMemory(self->device, &alloc, nullptr,
                     &self->staging_pool.memories[i]);
    vkBindBufferMemory(self->device, self->staging_pool.buffers[i],
                       self->staging_pool.memories[i], 0);
    self->staging_pool.sizes[i] = DEFAULT_BUFFER_SIZE;
  }

  return self;
}

// =============================================================================
//  Python-facing methods - resource creation
// =============================================================================

/**
 * Create a memory heap that can be used to sub-allocate resources.
 *
 * Args:
 *   heap_type (int): `0` = DEFAULT (device local), `1` = UPLOAD (host
 *      visible & coherent), `2` = READBACK (host visible, coherent, cached).
 *   size (int): Size in bytes.
 *
 * Returns:
 *   A new `vk.Heap` object.
 */
PyObject *vk_Device_create_heap(vk_Device *self, PyObject *args) {
  int heap_type;
  uint64_t size;

  if (!PyArg_ParseTuple(args, "iK", &heap_type, &size))
    return nullptr;
  if (size == 0) {
    PyErr_SetString(vk_HeapError, "Heap size cannot be zero");
    return nullptr;
  }

  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;

  VkMemoryPropertyFlags mem_flags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
  switch (heap_type) {
  case 0: /* DEFAULT */
    break;
  case 1: /* UPLOAD */
    mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
    break;
  case 2: /* READBACK */
    mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT |
                VK_MEMORY_PROPERTY_HOST_CACHED_BIT;
    break;
  default:
    PyErr_Format(vk_HeapError, "Invalid heap type %d", heap_type);
    return nullptr;
  }

  vk_Heap *heap = PyObject_New(vk_Heap, &vk_Heap_Type);
  if (!heap)
    return PyErr_NoMemory();
  VK_CLEAR_OBJECT(heap);
  heap->py_device = dev;
  Py_INCREF(dev);
  heap->heap_type = heap_type;
  heap->size = size;

  if (!allocate_device_memory(dev, size, mem_flags, &heap->memory)) {
    Py_DECREF(heap);
    return nullptr;
  }
  return reinterpret_cast<PyObject *>(heap);
}

/**
 * Create a buffer resource.
 *
 * Args:
 *   heap_type (int): Memory placement (`0` = DEFAULT, `1` = UPLOAD,
 *      `2` = READBACK).
 *   size (int): Buffer size in bytes.
 *   stride (int): Element stride (used for formatted buffers).
 *   format (int): Pixel format constant (e.g., `R32G32B32A32_FLOAT`), or 0
 *      for an unformatted buffer.
 *   heap (vk.Heap or None): Optional heap to sub-allocate from.
 *   heap_offset (int): Byte offset inside the heap.
 *   sparse (bool): Create as a sparse resource (requires support).
 *
 * Returns:
 *   A `vk.Resource` representing the buffer.
 */
PyObject *vk_Device_create_buffer(vk_Device *self, PyObject *args) {
  int heap_type;
  uint64_t size;
  uint32_t stride;
  int format;
  PyObject *py_heap = nullptr;
  uint64_t heap_offset = 0;
  PyObject *py_sparse = nullptr;

  if (!PyArg_ParseTuple(args, "iKIi|OKO", &heap_type, &size, &stride, &format,
                        &py_heap, &heap_offset, &py_sparse))
    return nullptr;

  if (size == 0) {
    PyErr_SetString(vk_BufferError, "Buffer size cannot be zero");
    return nullptr;
  }

  bool sparse = py_sparse && PyObject_IsTrue(py_sparse);
  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;

  if (sparse && !dev->supports_sparse) {
    PyErr_SetString(PyExc_ValueError,
                    "Sparse resources not supported on this device");
    return nullptr;
  }

  VkMemoryPropertyFlags mem_flags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
  switch (heap_type) {
  case 0:
    break;
  case 1:
    mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
    break;
  case 2:
    mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT |
                VK_MEMORY_PROPERTY_HOST_CACHED_BIT;
    break;
  default:
    PyErr_Format(vk_BufferError, "Invalid heap type %d", heap_type);
    return nullptr;
  }

  if (format > 0 && vk_format_map.find(format) == vk_format_map.end()) {
    PyErr_Format(vk_BufferError, "Invalid pixel format %d", format);
    return nullptr;
  }

  vk_Resource *res = PyObject_New(vk_Resource, &vk_Resource_Type);
  if (!res)
    return PyErr_NoMemory();
  VK_CLEAR_OBJECT(res);
  res->py_device = dev;
  Py_INCREF(dev);
  res->heap_type = heap_type;
  res->size = size;
  res->stride = stride;
  res->slices = 1;

  // Buffer usage: we need almost everything so that it can be used as
  // constant buffer, storage buffer, texel buffer, or transfer source/dest.
  VkBufferCreateInfo binfo = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
  binfo.size = size;
  binfo.usage =
      VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT |
      VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT | VK_BUFFER_USAGE_STORAGE_BUFFER_BIT |
      VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT |
      VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT |
      VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT;
  if (sparse) {
    binfo.flags = VK_BUFFER_CREATE_SPARSE_BINDING_BIT |
                  VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT |
                  VK_BUFFER_CREATE_SPARSE_ALIASED_BIT;
  }

  VK_CHECK_OR_RETURN_NULL(
      vkCreateBuffer(dev->device, &binfo, nullptr, &res->buffer),
      vk_BufferError, "Failed to create buffer");

  VkMemoryRequirements mem_req;
  vkGetBufferMemoryRequirements(dev->device, res->buffer, &mem_req);
  res->heap_size = mem_req.size;

  if (sparse) {
    res->tile_width = static_cast<uint32_t>(mem_req.alignment);
    res->tile_height = 1;
    res->tile_depth = 1;
    res->tiles_x =
        (uint32_t)((mem_req.size + mem_req.alignment - 1) / mem_req.alignment);
    res->tiles_y = 1;
    res->tiles_z = 1;
    // Sparse binding is handled by the caller later.
  } else if (py_heap && py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &vk_Heap_Type)) {
      Py_DECREF(res);
      PyErr_SetString(PyExc_TypeError, "Expected a Heap object");
      return nullptr;
    }
    vk_Heap *heap = reinterpret_cast<vk_Heap *>(py_heap);
    if (heap->py_device != dev) {
      Py_DECREF(res);
      PyErr_SetString(vk_BufferError, "Heap belongs to a different device");
      return nullptr;
    }
    if (heap->heap_type != heap_type) {
      Py_DECREF(res);
      PyErr_SetString(vk_BufferError, "Heap type mismatch");
      return nullptr;
    }
    if (heap_offset + mem_req.size > heap->size) {
      Py_DECREF(res);
      PyErr_SetString(vk_BufferError, "Heap is too small for this resource");
      return nullptr;
    }
    res->memory = heap->memory;
    res->py_heap = heap;
    Py_INCREF(heap);
    res->heap_offset = heap_offset;
  } else {
    if (!allocate_device_memory(dev, mem_req.size, mem_flags, &res->memory)) {
      Py_DECREF(res);
      return nullptr;
    }
  }

  if (!sparse) {
    VK_CHECK_OR_RETURN_NULL(vkBindBufferMemory(dev->device, res->buffer,
                                               res->memory, res->heap_offset),
                            vk_BufferError, "Failed to bind buffer memory");
  }

  // If a pixel format was requested, create a buffer view for formatted access.
  if (format > 0) {
    res->format = vk_format_map[format].first;
    VkBufferViewCreateInfo vinfo = {VK_STRUCTURE_TYPE_BUFFER_VIEW_CREATE_INFO};
    vinfo.buffer = res->buffer;
    vinfo.format = res->format;
    vinfo.range = VK_WHOLE_SIZE;
    VK_CHECK_OR_RETURN_NULL(
        vkCreateBufferView(dev->device, &vinfo, nullptr, &res->buffer_view),
        vk_BufferError, "Failed to create buffer view");
  }

  // Pre-fill the descriptor info that will be used when the resource is
  // bound to a compute pipeline.
  res->descriptor_buffer_info.buffer = res->buffer;
  res->descriptor_buffer_info.offset = 0;
  res->descriptor_buffer_info.range = size;

  return reinterpret_cast<PyObject *>(res);
}

/**
 * Create a 2D texture (or 2D array) resource.
 *
 * Args:
 *   width, height (int): Dimensions in pixels.
 *   format (int): Pixel format constant (e.g., `R8G8B8A8_UNORM`).
 *   heap (vk.Heap or None): Optional heap to sub-allocate from.
 *   heap_offset (int): Byte offset within the heap.
 *   slices (int): Number of array layers (default 1).
 *   sparse (bool): Create as a sparse resource.
 *   force_array (bool): If true, always use an array view even for a single
 * slice.
 *
 * Returns:
 *   A `vk.Resource` object representing the image.
 */
PyObject *vk_Device_create_texture2d(vk_Device *self, PyObject *args) {
  uint32_t width, height;
  int format;
  PyObject *py_heap = nullptr;
  uint64_t heap_offset = 0;
  uint32_t slices = 1;
  PyObject *py_sparse = nullptr;
  int force_array = 0;

  if (!PyArg_ParseTuple(args, "IIi|OKIOp", &width, &height, &format, &py_heap,
                        &heap_offset, &slices, &py_sparse, &force_array))
    return nullptr;

  if (width == 0 || height == 0 || slices == 0) {
    PyErr_SetString(vk_Texture2DError, "Invalid dimensions or slices");
    return nullptr;
  }

  if (vk_format_map.find(format) == vk_format_map.end()) {
    PyErr_Format(vk_Texture2DError, "Invalid pixel format %d", format);
    return nullptr;
  }

  bool sparse = py_sparse && PyObject_IsTrue(py_sparse);
  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;

  if (sparse && !dev->supports_sparse) {
    PyErr_SetString(PyExc_ValueError, "Sparse resources not supported");
    return nullptr;
  }

  VkFormat vk_format = vk_format_map[format].first;
  uint32_t bpp = vk_format_map[format].second;

  vk_Resource *res = PyObject_New(vk_Resource, &vk_Resource_Type);
  if (!res)
    return PyErr_NoMemory();
  VK_CLEAR_OBJECT(res);
  res->py_device = dev;
  Py_INCREF(dev);
  res->image_extent = {width, height, 1};
  res->slices = slices;
  res->row_pitch = width * bpp;
  res->size = res->row_pitch * height;
  res->format = vk_format;
  res->heap_type = 0; // textures are always device-local

  res->image = create_vk_image(dev->device, VK_IMAGE_TYPE_2D, vk_format, width,
                               height, 1, slices, sparse);
  if (res->image == VK_NULL_HANDLE) {
    Py_DECREF(res);
    PyErr_SetString(vk_Texture2DError, "Failed to create image");
    return nullptr;
  }

  VkMemoryRequirements mem_req;
  vkGetImageMemoryRequirements(dev->device, res->image, &mem_req);
  res->heap_size = mem_req.size;

  if (sparse) {
    // Retrieve tile granularity from the implementation.
    uint32_t sparse_req_count = 0;
    vkGetImageSparseMemoryRequirements(dev->device, res->image,
                                       &sparse_req_count, nullptr);
    std::vector<VkSparseImageMemoryRequirements> sparse_reqs(sparse_req_count);
    vkGetImageSparseMemoryRequirements(dev->device, res->image,
                                       &sparse_req_count, sparse_reqs.data());
    for (const auto &req : sparse_reqs) {
      if (req.formatProperties.aspectMask & VK_IMAGE_ASPECT_COLOR_BIT) {
        res->tile_width = req.formatProperties.imageGranularity.width;
        res->tile_height = req.formatProperties.imageGranularity.height;
        res->tile_depth = req.formatProperties.imageGranularity.depth;
        res->tiles_x = (width + res->tile_width - 1) / res->tile_width;
        res->tiles_y = (height + res->tile_height - 1) / res->tile_height;
        res->tiles_z = 1;
        break;
      }
    }
    // Memory is bound per-tile later.
  } else if (py_heap && py_heap != Py_None) {
    if (!PyObject_TypeCheck(py_heap, &vk_Heap_Type)) {
      Py_DECREF(res);
      PyErr_SetString(PyExc_TypeError, "Expected a Heap object");
      return nullptr;
    }
    vk_Heap *heap = reinterpret_cast<vk_Heap *>(py_heap);
    if (heap->py_device != dev) {
      Py_DECREF(res);
      PyErr_SetString(vk_Texture2DError, "Heap belongs to a different device");
      return nullptr;
    }
    if (heap->heap_type != 0) {
      Py_DECREF(res);
      PyErr_SetString(vk_Texture2DError,
                      "Heap must be DEFAULT type for textures");
      return nullptr;
    }
    if (heap_offset + mem_req.size > heap->size) {
      Py_DECREF(res);
      PyErr_SetString(vk_Texture2DError, "Heap is too small");
      return nullptr;
    }
    res->memory = heap->memory;
    res->py_heap = heap;
    Py_INCREF(heap);
    res->heap_offset = heap_offset;
  } else {
    if (!allocate_device_memory(dev, mem_req.size,
                                VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT,
                                &res->memory)) {
      Py_DECREF(res);
      return nullptr;
    }
  }

  if (!sparse) {
    VK_CHECK_OR_RETURN_NULL(vkBindImageMemory(dev->device, res->image,
                                              res->memory, res->heap_offset),
                            vk_Texture2DError, "Failed to bind image memory");
  }

  // Create the image view (2D or 2D array)
  VkImageViewCreateInfo vinfo = {VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
  vinfo.image = res->image;
  vinfo.viewType = (slices > 1 || force_array) ? VK_IMAGE_VIEW_TYPE_2D_ARRAY
                                               : VK_IMAGE_VIEW_TYPE_2D;
  vinfo.format = vk_format;
  vinfo.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  vinfo.subresourceRange.levelCount = 1;
  vinfo.subresourceRange.layerCount = slices;
  VK_CHECK_OR_RETURN_NULL(
      vkCreateImageView(dev->device, &vinfo, nullptr, &res->image_view),
      vk_Texture2DError, "Failed to create image view");

  // Transition the image to GENERAL layout so compute shaders can read/write.
  if (!vk_execute_one_time_commands(dev, [&](VkCommandBuffer cmd) {
        vk_cmd_transition_for_compute(cmd, res->image, 0, slices);
      })) {
    Py_DECREF(res);
    return nullptr; // Python exception already set
  }

  res->descriptor_image_info.imageView = res->image_view;
  res->descriptor_image_info.imageLayout = VK_IMAGE_LAYOUT_GENERAL;

  return reinterpret_cast<PyObject *>(res);
}

/**
 * Create a sampler object.
 *
 * Args:
 *   address_u/v/w (int): Address mode for U/V/W (`0` = wrap, `1` = mirror,
 *      `2` = clamp).
 *   filter_min (int): Minification filter (`0` = point, `1` = linear).
 *   filter_mag (int): Magnification filter (`0` = point, `1` = linear).
 *
 * Returns:
 *   A new `vk.Sampler` object.
 */
PyObject *vk_Device_create_sampler(vk_Device *self, PyObject *args) {
  int addr_u, addr_v, addr_w, filter_min, filter_mag;
  if (!PyArg_ParseTuple(args, "iiiii", &addr_u, &addr_v, &addr_w, &filter_min,
                        &filter_mag))
    return nullptr;

  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;

  auto addr_mode = [](int mode) -> VkSamplerAddressMode {
    switch (mode) {
    case 0:
      return VK_SAMPLER_ADDRESS_MODE_REPEAT;
    case 1:
      return VK_SAMPLER_ADDRESS_MODE_MIRRORED_REPEAT;
    case 2:
      return VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    default:
      return VK_SAMPLER_ADDRESS_MODE_REPEAT;
    }
  };

  VkSamplerCreateInfo sinfo = {VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
  sinfo.addressModeU = addr_mode(addr_u);
  sinfo.addressModeV = addr_mode(addr_v);
  sinfo.addressModeW = addr_mode(addr_w);

  // Map (min, mag) to Vulkan filter modes.
  if (filter_min == 0 && filter_mag == 0) {
    sinfo.minFilter = VK_FILTER_NEAREST;
    sinfo.magFilter = VK_FILTER_NEAREST;
    sinfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_NEAREST;
  } else if (filter_min == 1 && filter_mag == 0) {
    sinfo.minFilter = VK_FILTER_LINEAR;
    sinfo.magFilter = VK_FILTER_NEAREST;
    sinfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
  } else if (filter_min == 0 && filter_mag == 1) {
    sinfo.minFilter = VK_FILTER_NEAREST;
    sinfo.magFilter = VK_FILTER_LINEAR;
    sinfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
  } else if (filter_min == 1 && filter_mag == 1) {
    sinfo.minFilter = VK_FILTER_LINEAR;
    sinfo.magFilter = VK_FILTER_LINEAR;
    sinfo.mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR;
  } else {
    PyErr_SetString(vk_SamplerError, "Invalid filter combination");
    return nullptr;
  }

  vk_Sampler *sampler = PyObject_New(vk_Sampler, &vk_Sampler_Type);
  if (!sampler)
    return PyErr_NoMemory();
  VK_CLEAR_OBJECT(sampler);
  sampler->py_device = dev;
  Py_INCREF(dev);

  VK_CHECK_OR_RETURN_NULL(
      vkCreateSampler(dev->device, &sinfo, nullptr, &sampler->sampler),
      vk_SamplerError, "Failed to create sampler");

  sampler->descriptor_image_info.sampler = sampler->sampler;
  return reinterpret_cast<PyObject *>(sampler);
}

// =============================================================================
//  Debug & configuration helpers
// =============================================================================

/**
 * Return a list of debug messages collected since the last call.
 * Each message is a Python string.
 */
PyObject *vk_Device_get_debug_messages(vk_Device * /*self*/,
                                       PyObject * /*ignored*/) {
  PyObject *list = PyList_New(0);
  if (!list)
    return nullptr;
  for (const auto &msg : vk_debug_messages) {
    PyObject *py_msg = PyUnicode_FromString(msg.c_str());
    if (!py_msg) {
      Py_DECREF(list);
      return nullptr;
    }
    PyList_Append(list, py_msg);
    Py_DECREF(py_msg);
  }
  vk_debug_messages.clear();
  return list;
}

/**
 * Set the number of reusable staging buffers in the device's pool.
 * The actual reallocation occurs on the next acquire; existing buffers
 * are not resized.
 *
 * Args:
 *   size (int): New pool size (number of buffers).
 */
PyObject *vk_Device_set_buffer_pool_size(vk_Device *self, PyObject *args) {
  int size;
  if (!PyArg_ParseTuple(args, "i", &size))
    return nullptr;
  self->staging_pool.count = size;
  Py_RETURN_NONE;
}

// =============================================================================
//  Synchronisation methods
// =============================================================================

/**
 * Wait until the device queue is completely idle.
 * This is a blunt tool; prefer `wait_for_fences()` for per-frame sync.
 */
PyObject *vk_Device_wait_idle(vk_Device *self, PyObject * /*ignored*/) {
  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;
  VkResult res = vkQueueWaitIdle(dev->queue);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "vkQueueWaitIdle failed: %d", res);
    return nullptr;
  }
  Py_RETURN_NONE;
}

/**
 * Wait for one or all of a list of fences to be signalled.
 *
 * Args:
 *   fences (list of int): Native fence handles (as returned by
 *      `Swapchain.get_last_fence()`).
 *   wait_all (bool): If `True`, wait until *all* fences are signalled;
 *      otherwise return when *any* fence is signalled. Default `True`.
 *   timeout_ns (int): Timeout in nanoseconds (default `UINT64_MAX`).
 *
 * Returns:
 *   `True` if the fence(s) were signalled, `False` on timeout.
 *   Raises `RuntimeError` on Vulkan error.
 *
 * This is a blocking call, but the GIL is released while waiting.
 */
PyObject *vk_Device_wait_for_fences(vk_Device *self, PyObject *args) {
  PyObject *fence_list;
  int wait_all = 1;
  unsigned long long timeout_ns = UINT64_MAX;

  if (!PyArg_ParseTuple(args, "O!|pK", &PyList_Type, &fence_list, &wait_all,
                        &timeout_ns))
    return nullptr;

  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;

  Py_ssize_t count = PyList_Size(fence_list);
  std::vector<VkFence> fences(count);
  for (Py_ssize_t i = 0; i < count; ++i) {
    PyObject *item = PyList_GetItem(fence_list, i);
    if (item == Py_None) {
      fences[i] = VK_NULL_HANDLE;
      continue;
    }
    VkFence fence = (VkFence)PyLong_AsVoidPtr(item);
    if (PyErr_Occurred()) {
      PyErr_SetString(PyExc_TypeError, "Fence handle must be an integer");
      return nullptr;
    }
    fences[i] = fence;
  }

  VkResult res;
  Py_BEGIN_ALLOW_THREADS res =
      vkWaitForFences(dev->device, static_cast<uint32_t>(count), fences.data(),
                      wait_all ? VK_TRUE : VK_FALSE, timeout_ns);
  Py_END_ALLOW_THREADS

      if (res == VK_TIMEOUT) {
    Py_RETURN_FALSE;
  }
  else if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "vkWaitForFences failed: %d", res);
    return nullptr;
  }
  Py_RETURN_TRUE;
}

// =============================================================================
//  Type definition
// =============================================================================

static PyMethodDef vk_Device_methods[] = {
    {"create_heap", (PyCFunction)vk_Device_create_heap, METH_VARARGS,
     "Create a memory heap for sub-allocation.\n\n"
     "Args: heap_type (0=default, 1=upload, 2=readback), size (bytes)."},

    {"create_buffer", (PyCFunction)vk_Device_create_buffer, METH_VARARGS,
     "Create a buffer resource.\n\n"
     "Args: heap_type, size, stride, format, [heap=None, heap_offset=0, "
     "sparse=False]."},

    {"create_texture2d", (PyCFunction)vk_Device_create_texture2d, METH_VARARGS,
     "Create a 2D texture (or array) resource.\n\n"
     "Args: width, height, format, [heap=None, heap_offset=0, slices=1, "
     "sparse=False, force_array=False]."},

    {"create_sampler", (PyCFunction)vk_Device_create_sampler, METH_VARARGS,
     "Create a sampler object.\n\n"
     "Args: addr_u, addr_v, addr_w, filter_min, filter_mag."},

    {"create_compute", (PyCFunction)vk_Device_create_compute,
     METH_VARARGS | METH_KEYWORDS,
     "Create a compute pipeline.\n\n"
     "Args: shader (bytes), cbv=[], srv=[], uav=[], samplers=[], "
     "push_size=0, bindless=0."},

    {"create_swapchain", (PyCFunction)vk_Device_create_swapchain, METH_VARARGS,
     "Create a swapchain for presentation.\n\n"
     "Args: window_tuple=(display_ptr, window_ptr), format, num_buffers=3, "
     "width=0, height=0, present_mode='fifo'."},

    {"get_debug_messages", (PyCFunction)vk_Device_get_debug_messages,
     METH_NOARGS, "Return and clear the list of Vulkan debug messages."},

    {"set_buffer_pool_size", (PyCFunction)vk_Device_set_buffer_pool_size,
     METH_VARARGS, "Set the number of reusable staging buffers in the pool."},

    {"wait_idle", (PyCFunction)vk_Device_wait_idle, METH_NOARGS,
     "Wait until all GPU work on this device has finished."},

    {"wait_for_fences", (PyCFunction)vk_Device_wait_for_fences, METH_VARARGS,
     "Wait for one or more fences.\n\n"
     "Args: fences (list of int handles), wait_all (bool, default True), "
     "timeout_ns (int, default UINT64_MAX).\n"
     "Returns True if signalled, False on timeout."},

    {nullptr, nullptr, 0, nullptr}};

static PyMemberDef vk_Device_members[] = {
    {"name", T_STRING, offsetof(vk_Device, name), 0,
     "Human-readable device name."},
    {"dedicated_video_memory", T_ULONGLONG,
     offsetof(vk_Device, dedicated_video_memory), 0,
     "Dedicated video memory (bytes)."},
    {"dedicated_system_memory", T_ULONGLONG,
     offsetof(vk_Device, dedicated_system_memory), 0,
     "Dedicated system memory (bytes)."},
    {"shared_system_memory", T_ULONGLONG,
     offsetof(vk_Device, shared_system_memory), 0,
     "Shared system memory (bytes)."},
    {"vendor_id", T_UINT, offsetof(vk_Device, vendor_id), 0, "PCI vendor ID."},
    {"device_id", T_UINT, offsetof(vk_Device, device_id), 0, "PCI device ID."},
    {"is_hardware", T_BOOL, offsetof(vk_Device, is_hardware), 0,
     "True if the device is a hardware GPU (not CPU or virtual)."},
    {"is_discrete", T_BOOL, offsetof(vk_Device, is_discrete), 0,
     "True if the device is a discrete GPU (separate card)."},
    {nullptr}};

PyTypeObject vk_Device_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0).tp_name = "vulkan.Device",
    .tp_basicsize = sizeof(vk_Device),
    .tp_dealloc = (destructor)vk_Device_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Device_methods,
    .tp_members = vk_Device_members,
};