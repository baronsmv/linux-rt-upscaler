#include "vk_device.h"
#include "vk_utils.h"
#include <cmath>
#include <cstring>
#include <unordered_set>

// Forward declarations of Python type objects
extern PyTypeObject vk_Heap_Type;
extern PyTypeObject vk_Resource_Type;
extern PyTypeObject vk_Compute_Type;
extern PyTypeObject vk_Swapchain_Type;
extern PyTypeObject vk_Sampler_Type;

// Forward declarations of methods from other modules
extern PyMethodDef vk_Resource_methods[];
extern PyMethodDef vk_Compute_methods[];
extern PyMethodDef vk_Swapchain_methods[];

/* ----------------------------------------------------------------------------
   Forward declaration of the actual compute creation implementation
   ------------------------------------------------------------------------- */
extern PyObject *vk_Device_create_compute_impl(vk_Device *self, PyObject *args, PyObject *kwds);

/* ----------------------------------------------------------------------------
   Python method: create_compute (forwarding to implementation in vk_compute.cpp)
   ------------------------------------------------------------------------- */
PyObject *vk_Device_create_compute(vk_Device *self, PyObject *args, PyObject *kwds) {
    return vk_Device_create_compute_impl(self, args, kwds);
}

/* ----------------------------------------------------------------------------
   Forward declaration of the actual swapchain creation implementation
   ------------------------------------------------------------------------- */
extern PyObject *vk_Device_create_swapchain_impl(vk_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: create_swapchain (forwarding to implementation in vk_swapchain.cpp)
   ------------------------------------------------------------------------- */
PyObject *vk_Device_create_swapchain(vk_Device *self, PyObject *args) {
    return vk_Device_create_swapchain_impl(self, args);
}

/* ----------------------------------------------------------------------------
   vk_Device_dealloc
   ------------------------------------------------------------------------- */
void vk_Device_dealloc(vk_Device *self) {
    Py_XDECREF(self->name);
    if (self->device) {
        vkDeviceWaitIdle(self->device);

        // Destroy staging pool
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
            vkFreeCommandBuffers(self->device, self->command_pool, 1, &self->internal_cmd_buffer);
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

/* ----------------------------------------------------------------------------
   vk_Device_get_initialized – creates logical device and associated objects
   ------------------------------------------------------------------------- */
vk_Device *vk_Device_get_initialized(vk_Device *self) {
    if (self->device != VK_NULL_HANDLE)
        return self;

    if (!vk_instance_ensure())
        return nullptr;

    VkPhysicalDevice phys = self->physical_device;

    // Query physical device properties and features
    vkGetPhysicalDeviceMemoryProperties(phys, &self->mem_props);
    vkGetPhysicalDeviceFeatures(phys, &self->features);

    // Vulkan 1.2 features
    VkPhysicalDeviceVulkan12Features features12 = {
        VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES
    };
    VkPhysicalDeviceFeatures2 features2 = {
        VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2,
        &features12
    };
    vkGetPhysicalDeviceFeatures2(phys, &features2);
    self->features12 = features12;

    // Determine bindless support (descriptor indexing)
    self->supports_bindless = features12.descriptorIndexing &&
                              features12.shaderSampledImageArrayNonUniformIndexing &&
                              features12.shaderStorageImageArrayNonUniformIndexing &&
                              features12.shaderUniformBufferArrayNonUniformIndexing &&
                              features12.shaderStorageBufferArrayNonUniformIndexing;

    // Sparse support
    self->supports_sparse = self->features.sparseBinding &&
                            self->features.sparseResidencyBuffer &&
                            self->features.sparseResidencyImage2D;

    // Find a queue family that supports compute (and optionally graphics)
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
        PyErr_SetString(PyExc_RuntimeError, "No queue family with compute support found");
        return nullptr;
    }
    self->queue_family_index = qf_index;

    // Create logical device
    float queue_priority = 1.0f;
    VkDeviceQueueCreateInfo qinfo = { VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO };
    qinfo.queueFamilyIndex = qf_index;
    qinfo.queueCount = 1;
    qinfo.pQueuePriorities = &queue_priority;

    std::vector<const char *> extensions;
    if (vk_supports_swapchain)
        extensions.push_back(VK_KHR_SWAPCHAIN_EXTENSION_NAME);

    // Enable required features
    VkPhysicalDeviceFeatures enabled_features = {};
    enabled_features.shaderStorageImageReadWithoutFormat = self->features.shaderStorageImageReadWithoutFormat;
    enabled_features.shaderStorageImageWriteWithoutFormat = self->features.shaderStorageImageWriteWithoutFormat;
    enabled_features.sparseBinding = self->features.sparseBinding;
    enabled_features.sparseResidencyBuffer = self->features.sparseResidencyBuffer;
    enabled_features.sparseResidencyImage2D = self->features.sparseResidencyImage2D;

    VkDeviceCreateInfo dinfo = { VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO };
    dinfo.pNext = &features12;   // Vulkan 1.2 features
    dinfo.queueCreateInfoCount = 1;
    dinfo.pQueueCreateInfos = &qinfo;
    dinfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
    dinfo.ppEnabledExtensionNames = extensions.data();
    dinfo.pEnabledFeatures = &enabled_features;

    VkResult res = vkCreateDevice(phys, &dinfo, nullptr, &self->device);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Failed to create logical device (error %d)", res);
        return nullptr;
    }

    vkGetDeviceQueue(self->device, qf_index, 0, &self->queue);

    // Command pool
    VkCommandPoolCreateInfo pinfo = { VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO };
    pinfo.queueFamilyIndex = qf_index;
    pinfo.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
    vkCreateCommandPool(self->device, &pinfo, nullptr, &self->command_pool);

    // Internal command buffer for short operations
    VkCommandBufferAllocateInfo ainfo = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO };
    ainfo.commandPool = self->command_pool;
    ainfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    ainfo.commandBufferCount = 1;
    vkAllocateCommandBuffers(self->device, &ainfo, &self->internal_cmd_buffer);

    // Pipeline cache (shared across all pipelines on this device)
    VkPipelineCacheCreateInfo cinfo = { VK_STRUCTURE_TYPE_PIPELINE_CACHE_CREATE_INFO };
    vkCreatePipelineCache(self->device, &cinfo, nullptr, &self->pipeline_cache);

    // Timestamp support
    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(phys, &props);
    if (props.limits.timestampComputeAndGraphics) {
        VkQueryPoolCreateInfo qpinfo = { VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO };
        qpinfo.queryType = VK_QUERY_TYPE_TIMESTAMP;
        qpinfo.queryCount = 128;
        if (vkCreateQueryPool(self->device, &qpinfo, nullptr, &self->timestamp_pool) == VK_SUCCESS) {
            self->timestamp_count = 128;
            self->timestamp_period = props.limits.timestampPeriod;
            self->supports_timestamps = true;
        }
    }

    // Staging buffer pool (default 4 buffers of 2 MiB)
    self->staging_pool.count = 4;
    self->staging_pool.buffers = static_cast<VkBuffer *>(PyMem_Malloc(sizeof(VkBuffer) * 4));
    self->staging_pool.memories = static_cast<VkDeviceMemory *>(PyMem_Malloc(sizeof(VkDeviceMemory) * 4));
    self->staging_pool.sizes = static_cast<VkDeviceSize *>(PyMem_Malloc(sizeof(VkDeviceSize) * 4));
    self->staging_pool.next = 0;

    for (int i = 0; i < 4; ++i) {
        VkBufferCreateInfo binfo = { VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO };
        binfo.size = 2 * 1024 * 1024;
        binfo.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;
        vkCreateBuffer(self->device, &binfo, nullptr, &self->staging_pool.buffers[i]);

        VkMemoryRequirements req;
        vkGetBufferMemoryRequirements(self->device, self->staging_pool.buffers[i], &req);
        VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
        alloc.allocationSize = req.size;
        alloc.memoryTypeIndex = vk_find_memory_type_index(&self->mem_props,
            VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
        vkAllocateMemory(self->device, &alloc, nullptr, &self->staging_pool.memories[i]);
        vkBindBufferMemory(self->device, self->staging_pool.buffers[i],
                           self->staging_pool.memories[i], 0);
        self->staging_pool.sizes[i] = 2 * 1024 * 1024;
    }

    return self;
}

/* ----------------------------------------------------------------------------
   Python method: create_heap
   ------------------------------------------------------------------------- */
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
        case 0: break; // DEFAULT
        case 1: mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT; break; // UPLOAD
        case 2: mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_CACHED_BIT; break; // READBACK
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

    VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
    alloc.allocationSize = size;
    alloc.memoryTypeIndex = vk_find_memory_type_index(&dev->mem_props, mem_flags);

    VkResult res = vkAllocateMemory(dev->device, &alloc, nullptr, &heap->memory);
    if (res != VK_SUCCESS) {
        Py_DECREF(heap);
        PyErr_Format(vk_HeapError, "Failed to allocate heap memory (error %d)", res);
        return nullptr;
    }

    return reinterpret_cast<PyObject *>(heap);
}

/* ----------------------------------------------------------------------------
   Helper to create a VkImage
   ------------------------------------------------------------------------- */
static VkImage create_vk_image(VkDevice device, VkImageType type, VkFormat format,
                               uint32_t width, uint32_t height, uint32_t depth,
                               uint32_t slices, bool sparse) {
    VkImageCreateInfo info = { VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO };
    info.imageType = type;
    info.format = format;
    info.extent = { width, height, depth };
    info.mipLevels = 1;
    info.arrayLayers = slices;
    info.samples = VK_SAMPLE_COUNT_1_BIT;
    info.tiling = VK_IMAGE_TILING_OPTIMAL;
    info.usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT |
                 VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_STORAGE_BIT;
    info.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    if (sparse) {
        info.flags = VK_IMAGE_CREATE_SPARSE_BINDING_BIT |
                     VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT |
                     VK_IMAGE_CREATE_SPARSE_ALIASED_BIT;
    }

    VkImage image;
    VkResult res = vkCreateImage(device, &info, nullptr, &image);
    if (res != VK_SUCCESS)
        return VK_NULL_HANDLE;
    return image;
}

/* ----------------------------------------------------------------------------
   Python method: create_buffer
   ------------------------------------------------------------------------- */
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
        PyErr_SetString(PyExc_ValueError, "Sparse resources not supported on this device");
        return nullptr;
    }

    VkMemoryPropertyFlags mem_flags = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT;
    switch (heap_type) {
        case 0: break;
        case 1: mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT; break;
        case 2: mem_flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_CACHED_BIT; break;
        default:
            PyErr_Format(vk_BufferError, "Invalid heap type %d", heap_type);
            return nullptr;
    }

    // Validate format
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

    VkBufferCreateInfo binfo = { VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO };
    binfo.size = size;
    binfo.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT |
                  VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT | VK_BUFFER_USAGE_STORAGE_BUFFER_BIT |
                  VK_BUFFER_USAGE_UNIFORM_TEXEL_BUFFER_BIT | VK_BUFFER_USAGE_STORAGE_TEXEL_BUFFER_BIT |
                  VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT;
    if (sparse) {
        binfo.flags = VK_BUFFER_CREATE_SPARSE_BINDING_BIT |
                      VK_BUFFER_CREATE_SPARSE_RESIDENCY_BIT |
                      VK_BUFFER_CREATE_SPARSE_ALIASED_BIT;
    }

    if (vkCreateBuffer(dev->device, &binfo, nullptr, &res->buffer) != VK_SUCCESS) {
        Py_DECREF(res);
        PyErr_SetString(vk_BufferError, "Failed to create buffer");
        return nullptr;
    }

    VkMemoryRequirements mem_req;
    vkGetBufferMemoryRequirements(dev->device, res->buffer, &mem_req);
    res->heap_size = mem_req.size;

    if (sparse) {
        res->tile_width = static_cast<uint32_t>(mem_req.alignment);
        res->tile_height = 1;
        res->tile_depth = 1;
        res->tiles_x = static_cast<uint32_t>((mem_req.size + mem_req.alignment - 1) / mem_req.alignment);
        res->tiles_y = 1;
        res->tiles_z = 1;
        // Sparse binding is done separately; we don't allocate memory yet.
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
        VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
        alloc.allocationSize = mem_req.size;
        alloc.memoryTypeIndex = vk_find_memory_type_index(&dev->mem_props, mem_flags);
        if (vkAllocateMemory(dev->device, &alloc, nullptr, &res->memory) != VK_SUCCESS) {
            Py_DECREF(res);
            PyErr_SetString(vk_BufferError, "Failed to allocate buffer memory");
            return nullptr;
        }
    }

    if (!sparse) {
        if (vkBindBufferMemory(dev->device, res->buffer, res->memory, res->heap_offset) != VK_SUCCESS) {
            Py_DECREF(res);
            PyErr_SetString(vk_BufferError, "Failed to bind buffer memory");
            return nullptr;
        }
    }

    // Create buffer view if format provided
    if (format > 0) {
        res->format = vk_format_map[format].first;
        VkBufferViewCreateInfo vinfo = { VK_STRUCTURE_TYPE_BUFFER_VIEW_CREATE_INFO };
        vinfo.buffer = res->buffer;
        vinfo.format = res->format;
        vinfo.range = VK_WHOLE_SIZE;
        if (vkCreateBufferView(dev->device, &vinfo, nullptr, &res->buffer_view) != VK_SUCCESS) {
            Py_DECREF(res);
            PyErr_SetString(vk_BufferError, "Failed to create buffer view");
            return nullptr;
        }
    }

    res->descriptor_buffer_info.buffer = res->buffer;
    res->descriptor_buffer_info.offset = 0;
    res->descriptor_buffer_info.range = size;

    return reinterpret_cast<PyObject *>(res);
}

/* ----------------------------------------------------------------------------
   Python method: create_texture2d
   ------------------------------------------------------------------------- */
PyObject *vk_Device_create_texture2d(vk_Device *self, PyObject *args) {
    uint32_t width, height;
    int format;
    PyObject *py_heap = nullptr;
    uint64_t heap_offset = 0;
    uint32_t slices = 1;
    PyObject *py_sparse = nullptr;

    if (!PyArg_ParseTuple(args, "IIi|OKIO", &width, &height, &format,
                          &py_heap, &heap_offset, &slices, &py_sparse))
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
    res->image_extent = { width, height, 1 };
    res->slices = slices;
    res->row_pitch = width * bpp;
    res->size = res->row_pitch * height;
    res->format = vk_format;
    res->heap_type = 0; // textures are always device-local

    res->image = create_vk_image(dev->device, VK_IMAGE_TYPE_2D, vk_format,
                                 width, height, 1, slices, sparse);
    if (res->image == VK_NULL_HANDLE) {
        Py_DECREF(res);
        PyErr_SetString(vk_Texture2DError, "Failed to create image");
        return nullptr;
    }

    VkMemoryRequirements mem_req;
    vkGetImageMemoryRequirements(dev->device, res->image, &mem_req);
    res->heap_size = mem_req.size;

    if (sparse) {
        // Query sparse image memory requirements
        uint32_t sparse_req_count = 0;
        vkGetImageSparseMemoryRequirements(dev->device, res->image, &sparse_req_count, nullptr);
        std::vector<VkSparseImageMemoryRequirements> sparse_reqs(sparse_req_count);
        vkGetImageSparseMemoryRequirements(dev->device, res->image, &sparse_req_count, sparse_reqs.data());
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
            PyErr_SetString(vk_Texture2DError, "Heap must be DEFAULT type for textures");
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
        VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
        alloc.allocationSize = mem_req.size;
        alloc.memoryTypeIndex = vk_find_memory_type_index(&dev->mem_props, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
        if (vkAllocateMemory(dev->device, &alloc, nullptr, &res->memory) != VK_SUCCESS) {
            Py_DECREF(res);
            PyErr_SetString(vk_Texture2DError, "Failed to allocate image memory");
            return nullptr;
        }
    }

    if (!sparse) {
        if (vkBindImageMemory(dev->device, res->image, res->memory, res->heap_offset) != VK_SUCCESS) {
            Py_DECREF(res);
            PyErr_SetString(vk_Texture2DError, "Failed to bind image memory");
            return nullptr;
        }
    }

    // Create image view
    VkImageViewCreateInfo vinfo = { VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO };
    vinfo.image = res->image;
    vinfo.viewType = slices > 1 ? VK_IMAGE_VIEW_TYPE_2D_ARRAY : VK_IMAGE_VIEW_TYPE_2D;
    vinfo.format = vk_format;
    vinfo.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    vinfo.subresourceRange.levelCount = 1;
    vinfo.subresourceRange.layerCount = slices;

    if (vkCreateImageView(dev->device, &vinfo, nullptr, &res->image_view) != VK_SUCCESS) {
        Py_DECREF(res);
        PyErr_SetString(vk_Texture2DError, "Failed to create image view");
        return nullptr;
    }

    // Transition to GENERAL layout
    VkCommandBuffer cmd = dev->internal_cmd_buffer;
    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);
    vk_image_barrier(cmd, res->image,
                     VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_GENERAL,
                     VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                     0, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                     0, 1, 0, slices);
    vkEndCommandBuffer(cmd);

    if (vk_execute_command_buffer(dev, cmd, VK_NULL_HANDLE, 0, nullptr, nullptr, 0, nullptr) != VK_SUCCESS) {
        Py_DECREF(res);
        PyErr_SetString(vk_Texture2DError, "Failed to transition image layout");
        return nullptr;
    }

    res->descriptor_image_info.imageView = res->image_view;
    res->descriptor_image_info.imageLayout = VK_IMAGE_LAYOUT_GENERAL;

    return reinterpret_cast<PyObject *>(res);
}

/* ----------------------------------------------------------------------------
   Python method: create_sampler
   ------------------------------------------------------------------------- */
PyObject *vk_Device_create_sampler(vk_Device *self, PyObject *args) {
    int addr_u, addr_v, addr_w, filter_min, filter_mag;
    if (!PyArg_ParseTuple(args, "iiiii", &addr_u, &addr_v, &addr_w, &filter_min, &filter_mag))
        return nullptr;

    vk_Device *dev = vk_Device_get_initialized(self);
    if (!dev)
        return nullptr;

    auto addr_mode = [](int mode) -> VkSamplerAddressMode {
        switch (mode) {
            case 0: return VK_SAMPLER_ADDRESS_MODE_REPEAT;
            case 1: return VK_SAMPLER_ADDRESS_MODE_MIRRORED_REPEAT;
            case 2: return VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
            default: return VK_SAMPLER_ADDRESS_MODE_REPEAT;
        }
    };

    VkSamplerCreateInfo sinfo = { VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO };
    sinfo.addressModeU = addr_mode(addr_u);
    sinfo.addressModeV = addr_mode(addr_v);
    sinfo.addressModeW = addr_mode(addr_w);

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

    if (vkCreateSampler(dev->device, &sinfo, nullptr, &sampler->sampler) != VK_SUCCESS) {
        Py_DECREF(sampler);
        PyErr_SetString(vk_SamplerError, "Failed to create sampler");
        return nullptr;
    }

    sampler->descriptor_image_info.sampler = sampler->sampler;
    return reinterpret_cast<PyObject *>(sampler);
}

/* ----------------------------------------------------------------------------
   Python method: get_debug_messages
   ------------------------------------------------------------------------- */
PyObject *vk_Device_get_debug_messages(vk_Device *self, PyObject *ignored) {
    PyObject *list = PyList_New(0);
    for (const auto &msg : vk_debug_messages) {
        PyList_Append(list, PyUnicode_FromString(msg.c_str()));
    }
    vk_debug_messages.clear();
    return list;
}

/* ----------------------------------------------------------------------------
   Python method: set_buffer_pool_size
   ------------------------------------------------------------------------- */
PyObject *vk_Device_set_buffer_pool_size(vk_Device *self, PyObject *args) {
    int size;
    if (!PyArg_ParseTuple(args, "i", &size))
        return nullptr;
    // Update the pool size; actual reallocation happens on next acquire
    self->staging_pool.count = size;
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Python method: wait_idle
   ------------------------------------------------------------------------- */
PyObject *vk_Device_wait_idle(vk_Device *self, PyObject *ignored) {
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

/* ----------------------------------------------------------------------------
   Device type definition
   ------------------------------------------------------------------------- */
static PyMethodDef vk_Device_methods[] = {
    {"create_heap", (PyCFunction)vk_Device_create_heap, METH_VARARGS,
     "Create a memory heap for suballocation."},
    {"create_buffer", (PyCFunction)vk_Device_create_buffer, METH_VARARGS,
     "Create a buffer resource."},
    {"create_texture2d", (PyCFunction)vk_Device_create_texture2d, METH_VARARGS,
     "Create a 2D texture (or 2D array) resource."},
    {"create_sampler", (PyCFunction)vk_Device_create_sampler, METH_VARARGS,
     "Create a sampler object."},
    {"create_compute", (PyCFunction)vk_Device_create_compute, METH_VARARGS | METH_KEYWORDS,
     "Create a compute pipeline."},
    {"create_swapchain", (PyCFunction)vk_Device_create_swapchain, METH_VARARGS,
     "Create a swapchain for presentation."},
    {"get_debug_messages", (PyCFunction)vk_Device_get_debug_messages, METH_NOARGS,
     "Retrieve and clear Vulkan debug messages."},
    {"set_buffer_pool_size", (PyCFunction)vk_Device_set_buffer_pool_size, METH_VARARGS,
     "Set the number of staging buffers in the pool."},
    {"wait_idle", (PyCFunction)vk_Device_wait_idle, METH_NOARGS,
     "Wait for all GPU work to finish."},
    {nullptr, nullptr, 0, nullptr}
};

static PyMemberDef vk_Device_members[] = {
    {"name", T_STRING, offsetof(vk_Device, name), 0, "Device name"},
    {"dedicated_video_memory", T_ULONGLONG, offsetof(vk_Device, dedicated_video_memory), 0,
     "Dedicated video memory in bytes"},
    {"dedicated_system_memory", T_ULONGLONG, offsetof(vk_Device, dedicated_system_memory), 0,
     "Dedicated system memory in bytes"},
    {"shared_system_memory", T_ULONGLONG, offsetof(vk_Device, shared_system_memory), 0,
     "Shared system memory in bytes"},
    {"vendor_id", T_UINT, offsetof(vk_Device, vendor_id), 0, "PCI vendor ID"},
    {"device_id", T_UINT, offsetof(vk_Device, device_id), 0, "PCI device ID"},
    {"is_hardware", T_BOOL, offsetof(vk_Device, is_hardware), 0, "True if hardware device"},
    {"is_discrete", T_BOOL, offsetof(vk_Device, is_discrete), 0, "True if discrete GPU"},
    {nullptr}
};

PyTypeObject vk_Device_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Device",
    .tp_basicsize = sizeof(vk_Device),
    .tp_dealloc = (destructor)vk_Device_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Device_methods,
    .tp_members = vk_Device_members,
};