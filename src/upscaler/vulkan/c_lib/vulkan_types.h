/**
 * @file vulkan_types.h
 * @brief Core type definitions shared across Vulkan backend modules.
 */

#ifndef VULKAN_TYPES_H
#define VULKAN_TYPES_H

#include <Python.h>
#include <stdbool.h>
#include <stdint.h>
#include <vulkan/vulkan.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Global Vulkan instance (defined in vulkan_module.c)
   ------------------------------------------------------------------------- */
extern VkInstance g_vulkan_instance;

/* -------------------------------------------------------------------------
   Error objects (defined in vulkan_module.c)
   ------------------------------------------------------------------------- */
extern PyObject *VkComp_Texture2DError;
extern PyObject *VkComp_BufferError;
extern PyObject *VkComp_ComputeError;
extern PyObject *VkComp_SwapchainError;
extern PyObject *VkComp_HeapError;
extern PyObject *VkComp_SamplerError;
extern PyObject *VkComp_Texture1DError;
extern PyObject *VkComp_Texture3DError;

/* -------------------------------------------------------------------------
   Format table entry
   ------------------------------------------------------------------------- */
typedef struct VkComp_FormatInfo {
  VkFormat vk_format;
  uint32_t bytes_per_pixel;
} VkComp_FormatInfo;

extern VkComp_FormatInfo g_vulkan_format_table[256];

/* -------------------------------------------------------------------------
   Forward declarations of all Python types
   ------------------------------------------------------------------------- */
typedef struct VkComp_Device VkComp_Device;
typedef struct VkComp_Heap VkComp_Heap;
typedef struct VkComp_Resource VkComp_Resource;
typedef struct VkComp_Compute VkComp_Compute;
typedef struct VkComp_Swapchain VkComp_Swapchain;
typedef struct VkComp_Sampler VkComp_Sampler;

/* -------------------------------------------------------------------------
   Device structure (opaque to most modules; full definition in vulkan_device.h)
   ------------------------------------------------------------------------- */
struct VkComp_Device {
  PyObject_HEAD

      /* Vulkan handles */
      VkPhysicalDevice physical_device;
  VkDevice device;
  VkQueue queue;
  uint32_t queue_family_index;
  VkCommandPool command_pool;

  /* Properties */
  VkPhysicalDeviceMemoryProperties mem_props;
  VkPhysicalDeviceFeatures features;
  VkPhysicalDeviceVulkan13Features vulkan13_features;
  VkPhysicalDeviceProperties props;

  /* Python-visible attributes */
  PyObject *name;
  uint64_t dedicated_video_memory;
  uint64_t dedicated_system_memory;
  uint64_t shared_system_memory;
  uint32_t vendor_id;
  uint32_t device_id;
  int is_hardware;
  int is_discrete;

  /* Timestamp queries */
  VkQueryPool timestamp_pool;
  uint32_t timestamp_count;
  float timestamp_period;
  bool supports_timestamps;

  /* Timeline semaphore */
  VkSemaphore timeline_semaphore;
  uint64_t timeline_value;

  /* Staging buffer pool */
  struct {
    VkBuffer *buffers;
    VkDeviceMemory *memories;
    VkDeviceSize *sizes;
    uint32_t count;
    uint32_t next;
    VkDeviceSize fixed_size;
  } staging_pool;

  /* Feature flags */
  bool supports_bindless;
  bool supports_sparse;
  bool supports_swapchain;
};

/* -------------------------------------------------------------------------
   Heap structure (full definition)
   ------------------------------------------------------------------------- */
struct VkComp_Heap {
  PyObject_HEAD VkComp_Device *device;
  VkDeviceMemory memory;
  uint64_t size;
  int heap_type;
};

/* -------------------------------------------------------------------------
   Resource structure (full definition)
   ------------------------------------------------------------------------- */
struct VkComp_Resource {
  PyObject_HEAD

      VkComp_Device *device;
  VkBuffer buffer;
  VkImage image;
  VkImageView image_view;
  VkBufferView buffer_view;
  VkDeviceMemory memory;
  uint64_t size;
  uint32_t stride;
  VkExtent3D image_extent;
  VkDescriptorBufferInfo descriptor_buffer_info;
  VkDescriptorImageInfo descriptor_image_info;
  uint64_t row_pitch;
  VkFormat format;
  VkComp_Heap *heap;
  uint64_t heap_offset;
  uint32_t slices;
  uint64_t heap_size;
  int heap_type;

  /* Sparse tiling */
  uint32_t tiles_x, tiles_y, tiles_z;
  uint32_t tile_width, tile_height, tile_depth;
};

/* -------------------------------------------------------------------------
   Compute pipeline structure (full definition)
   ------------------------------------------------------------------------- */
struct VkComp_Compute {
  PyObject_HEAD VkComp_Device *device;
  VkDescriptorPool descriptor_pool;
  VkPipeline pipeline;
  VkDescriptorSetLayout descriptor_set_layout;
  VkPipelineLayout pipeline_layout;
  VkDescriptorSet descriptor_set;
  VkShaderModule shader_module;
  PyObject *cbv_list;
  PyObject *srv_list;
  PyObject *uav_list;
  PyObject *samplers_list;
  uint32_t push_constant_size;
  uint32_t bindless_max;
  VkFence dispatch_fence;
};

/* -------------------------------------------------------------------------
   Swapchain structure (full definition)
   ------------------------------------------------------------------------- */
struct VkComp_Swapchain {
  PyObject_HEAD VkComp_Device *device;
  VkSwapchainKHR swapchain;
  VkSemaphore copy_semaphore;
  VkSemaphore present_semaphore;
  VkSurfaceKHR surface;
  VkExtent2D image_extent;
  VkImage *images;
  uint32_t image_count;
  VkFormat format;
  bool suboptimal;
  bool out_of_date;
  VkFence *fences;
};

/* -------------------------------------------------------------------------
   Sampler structure (full definition)
   ------------------------------------------------------------------------- */
struct VkComp_Sampler {
  PyObject_HEAD VkComp_Device *device;
  VkSampler sampler;
  VkDescriptorImageInfo descriptor_image_info;
};

/* -------------------------------------------------------------------------
   Type objects (defined in respective modules)
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Device_Type;
extern PyTypeObject VkComp_Heap_Type;
extern PyTypeObject VkComp_Resource_Type;
extern PyTypeObject VkComp_Compute_Type;
extern PyTypeObject VkComp_Swapchain_Type;
extern PyTypeObject VkComp_Sampler_Type;

/* -------------------------------------------------------------------------
   Helper macro to clear object fields after PyObject_HEAD
   ------------------------------------------------------------------------- */
#define VKCOMP_CLEAR_OBJECT(obj)                                               \
  memset((char *)(obj) + sizeof(PyObject), 0, sizeof(*(obj)) - sizeof(PyObject))

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_TYPES_H */