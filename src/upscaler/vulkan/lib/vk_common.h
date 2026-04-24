#ifndef VK_COMMON_H
#define VK_COMMON_H

#include <Python.h>
#include <mutex>
#include <string>
#include <structmember.h>
#include <unordered_map>
#include <vector>
#include <vulkan/vulkan.h>

// =========================================================================
//  Global Vulkan state (set up in vk_instance.cpp)
// =========================================================================
extern VkInstance vk_instance;
extern bool vk_supports_swapchain;
extern bool vk_debug_enabled;
extern std::unordered_map<uint32_t, std::pair<VkFormat, uint32_t>>
    vk_format_map;
extern std::vector<std::string> vk_debug_messages;

// =========================================================================
//  Python error objects (set up in vk_module.cpp)
// =========================================================================
extern PyObject *vk_Texture2DError;
extern PyObject *vk_BufferError;
extern PyObject *vk_ComputeError;
extern PyObject *vk_SwapchainError;
extern PyObject *vk_HeapError;
extern PyObject *vk_SamplerError;
extern PyObject *vk_Texture1DError;
extern PyObject *vk_Texture3DError;

// =========================================================================
//  Forward declarations of Python object types
// =========================================================================
typedef struct vk_Device vk_Device;
typedef struct vk_Heap vk_Heap;
typedef struct vk_Resource vk_Resource;
typedef struct vk_Compute vk_Compute;
typedef struct vk_Swapchain vk_Swapchain;
typedef struct vk_Sampler vk_Sampler;

// =========================================================================
//  Pixel format constants (matching Python module constants)
// =========================================================================
#define R32G32B32A32_FLOAT 2
#define R32G32B32A32_UINT 3
#define R32G32B32A32_SINT 4
#define R32G32B32_FLOAT 6
#define R32G32B32_UINT 7
#define R32G32B32_SINT 8
#define R16G16B16A16_FLOAT 10
#define R16G16B16A16_UNORM 11
#define R16G16B16A16_UINT 12
#define R16G16B16A16_SNORM 13
#define R16G16B16A16_SINT 14
#define R32G32_FLOAT 16
#define R32G32_UINT 17
#define R32G32_SINT 18
#define R10G10B10A2_UNORM 24
#define R10G10B10A2_UINT 25
#define R8G8B8A8_UNORM 28
#define R8G8B8A8_UNORM_SRGB 29
#define R8G8B8A8_UINT 30
#define R8G8B8A8_SNORM 31
#define R8G8B8A8_SINT 32
#define R16G16_FLOAT 34
#define R16G16_UNORM 35
#define R16G16_UINT 36
#define R16G16_SNORM 37
#define R16G16_SINT 38
#define R32_FLOAT 41
#define R32_UINT 42
#define R32_SINT 43
#define R8G8_UNORM 49
#define R8G8_UINT 50
#define R8G8_SNORM 51
#define R8G8_SINT 52
#define R16_FLOAT 54
#define R16_UNORM 55
#define R16_UINT 57
#define R16_SNORM 58
#define R16_SINT 59
#define R8_UNORM 61
#define R8_UINT 62
#define R8_SNORM 63
#define R8_SINT 64
#define B8G8R8A8_UNORM 87
#define B8G8R8A8_UNORM_SRGB 91

// =========================================================================
//  Core object structures
// =========================================================================

struct vk_Device {
  PyObject_HEAD;
  VkPhysicalDevice physical_device;
  VkDevice device;
  VkQueue queue;
  uint32_t queue_family_index;
  VkCommandPool command_pool;
  VkCommandBuffer internal_cmd_buffer; // short synchronous operations
  VkPipelineCache pipeline_cache;      // shared by all pipelines
  std::mutex cmd_pool_mutex;

  VkPhysicalDeviceMemoryProperties mem_props;
  VkPhysicalDeviceFeatures features;
  VkPhysicalDeviceVulkan12Features features12;

  bool supports_bindless;
  bool supports_sparse;
  bool supports_timestamps;
  float timestamp_period;
  VkQueryPool timestamp_pool;
  uint32_t timestamp_count;

  // Staging buffer pool (mappable, coherent)
  struct {
    VkBuffer *buffers;
    VkDeviceMemory *memories;
    VkDeviceSize *sizes;
    int count;
    int next;
  } staging_pool;

  // Python-exposed properties
  char *name;
  uint64_t dedicated_video_memory;
  uint64_t dedicated_system_memory;
  uint64_t shared_system_memory;
  uint32_t vendor_id, device_id;
  bool is_hardware, is_discrete;
};

struct vk_Heap {
  PyObject_HEAD;
  vk_Device *py_device;
  VkDeviceMemory memory;
  uint64_t size;
  int heap_type; // 0=DEFAULT, 1=UPLOAD, 2=READBACK
};

struct vk_Resource {
  PyObject_HEAD;
  vk_Device *py_device;
  VkBuffer buffer;
  VkImage image;
  VkImageView image_view;
  VkBufferView buffer_view;
  VkDeviceMemory memory;
  vk_Heap *py_heap; // optional backing heap
  uint64_t heap_offset;
  uint64_t size;
  uint64_t row_pitch;
  uint32_t stride;
  VkExtent3D image_extent;
  VkFormat format;
  uint32_t slices;
  uint64_t heap_size;
  int heap_type;

  // Pre-filled descriptor info (used when binding)
  VkDescriptorBufferInfo descriptor_buffer_info;
  VkDescriptorImageInfo descriptor_image_info;

  // Sparse resource tiling
  uint32_t tiles_x, tiles_y, tiles_z;
  uint32_t tile_width, tile_height, tile_depth;
};

struct vk_Compute {
  PyObject_HEAD;
  vk_Device *py_device;
  VkPipeline pipeline;
  VkPipelineLayout pipeline_layout;
  VkDescriptorSetLayout descriptor_set_layout;
  VkDescriptorPool descriptor_pool;
  VkDescriptorSet descriptor_set;
  VkShaderModule shader_module;
  VkFence dispatch_fence;
  uint32_t push_constant_size;
  uint32_t bindless;

  // References to bound resources (lifetime management)
  PyObject *py_cbv_list;
  PyObject *py_srv_list;
  PyObject *py_uav_list;
  PyObject *py_samplers_list;
};

// Full definition in vk_swapchain.h
struct vk_Swapchain;

struct vk_Sampler {
  PyObject_HEAD;
  vk_Device *py_device;
  VkSampler sampler;
  VkDescriptorImageInfo descriptor_image_info;
};

// =========================================================================
//  Python type objects (declared here, defined in their respective modules)
// =========================================================================
extern PyTypeObject vk_Device_Type;
extern PyTypeObject vk_Heap_Type;
extern PyTypeObject vk_Resource_Type;
extern PyTypeObject vk_Compute_Type;
extern PyTypeObject vk_Swapchain_Type;
extern PyTypeObject vk_Sampler_Type;

// =========================================================================
//  Convenience macros
// =========================================================================

// Zero all bytes after the PyObject header (used in object constructors).
#define VK_CLEAR_OBJECT(obj)                                                   \
  memset(((char *)(obj)) + sizeof(PyObject), 0,                                \
         sizeof(*(obj)) - sizeof(PyObject))

// Align a value up to the next multiple.
#define VK_ALIGN_UP(x, alignment) (((x) + (alignment) - 1) & ~((alignment) - 1))

// =========================================================================
//  Template helper - validate and populate descriptor resource lists
// =========================================================================
template <typename ResT, typename SampT>
bool vk_check_descriptor_lists(PyTypeObject *res_type, PyObject *cbv_list,
                               std::vector<ResT *> &cbv, PyObject *srv_list,
                               std::vector<ResT *> &srv, PyObject *uav_list,
                               std::vector<ResT *> &uav,
                               PyTypeObject *sampler_type,
                               PyObject *sampler_list,
                               std::vector<SampT *> &samplers) {
  auto check_list = [&](PyObject *list, std::vector<ResT *> &vec,
                        const char *name) -> bool {
    if (!list || list == Py_None)
      return true;
    if (!PyList_Check(list)) {
      PyErr_Format(PyExc_TypeError, "%s must be a list", name);
      return false;
    }
    Py_ssize_t size = PyList_Size(list);
    for (Py_ssize_t i = 0; i < size; i++) {
      PyObject *item = PyList_GetItem(list, i);
      if (!PyObject_TypeCheck(item, res_type)) {
        PyErr_Format(PyExc_TypeError, "%s[%zd] is not a Resource", name, i);
        return false;
      }
      vec.push_back((ResT *)item);
    }
    return true;
  };

  auto check_samplers = [&](PyObject *list, std::vector<SampT *> &vec) -> bool {
    if (!list || list == Py_None)
      return true;
    if (!PyList_Check(list)) {
      PyErr_Format(PyExc_TypeError, "samplers must be a list");
      return false;
    }
    Py_ssize_t size = PyList_Size(list);
    for (Py_ssize_t i = 0; i < size; i++) {
      PyObject *item = PyList_GetItem(list, i);
      if (!PyObject_TypeCheck(item, sampler_type)) {
        PyErr_Format(PyExc_TypeError, "samplers[%zd] is not a Sampler", i);
        return false;
      }
      vec.push_back((SampT *)item);
    }
    return true;
  };

  return check_list(cbv_list, cbv, "cbv") && check_list(srv_list, srv, "srv") &&
         check_list(uav_list, uav, "uav") &&
         check_samplers(sampler_list, samplers);
}

#endif // VK_COMMON_H