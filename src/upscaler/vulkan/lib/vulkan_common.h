#ifndef VULKAN_COMMON_H
#define VULKAN_COMMON_H

#include "structmember.h"
#include <Python.h>
#include <X11/Xlib.h>
#include <string>
#include <unordered_map>
#include <vector>
#include <vulkan/vulkan.h>
#include <vulkan/vulkan_xlib.h>

/* ----------------------------------------------------------------------------
   Error objects (defined in vulkan_module.c)
   ------------------------------------------------------------------------- */
extern PyObject *Compushady_Texture2DError;
extern PyObject *Compushady_BufferError;
extern PyObject *Compushady_ComputeError;
extern PyObject *Compushady_SwapchainError;
extern PyObject *Compushady_HeapError;
extern PyObject *Compushady_SamplerError;
extern PyObject *Compushady_Texture1DError;
extern PyObject *Compushady_Texture3DError;

/* ----------------------------------------------------------------------------
   Global state
   ------------------------------------------------------------------------- */
extern VkInstance vulkan_instance;
extern bool vulkan_supports_swapchain;
extern bool vulkan_supports_wayland;
extern bool vulkan_debug;
extern std::unordered_map<uint32_t, std::pair<VkFormat, uint32_t>>
    vulkan_formats;
extern std::vector<std::string> vulkan_debug_messages;

/* ----------------------------------------------------------------------------
   Core object types
   ------------------------------------------------------------------------- */
typedef struct vulkan_Device {
  PyObject_HEAD;
  VkPhysicalDevice physical_device;
  VkDevice device;
  VkQueue queue;
  PyObject *name;
  uint64_t dedicated_video_memory;
  uint64_t dedicated_system_memory;
  uint64_t shared_system_memory;
  VkPhysicalDeviceMemoryProperties mem_props;
  VkCommandPool command_pool;
  VkCommandBuffer command_buffer;
  uint32_t device_id;
  uint32_t vendor_id;
  uint32_t queue_family_index;
  char is_hardware;
  char is_discrete;
  VkPhysicalDeviceFeatures features;
  bool supports_bindless;
  bool supports_sparse;
  int buffer_pool_size;
  struct {
    VkBuffer *buffers;
    VkDeviceMemory *memories;
    VkDeviceSize *sizes;
    int count;
    int next;
  } staging_pool;
  // Timestamp support
  VkQueryPool timestamp_pool;
  uint32_t timestamp_count;
  float timestamp_period;
  bool supports_timestamps;
} vulkan_Device;

typedef struct vulkan_Heap {
  PyObject_HEAD;
  vulkan_Device *py_device;
  VkDeviceMemory memory;
  uint64_t size;
  int heap_type;
} vulkan_Heap;

typedef struct vulkan_Resource {
  PyObject_HEAD;
  vulkan_Device *py_device;
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
  vulkan_Heap *py_heap;
  uint64_t heap_offset;
  uint32_t slices;
  uint64_t heap_size;
  int heap_type;
  uint32_t tiles_x, tiles_y, tiles_z;
  uint32_t tile_width, tile_height, tile_depth;
} vulkan_Resource;

typedef struct vulkan_Compute {
  PyObject_HEAD;
  vulkan_Device *py_device;
  VkDescriptorPool descriptor_pool;
  VkPipeline pipeline;
  VkDescriptorSetLayout descriptor_set_layout;
  VkPipelineLayout pipeline_layout;
  VkDescriptorSet descriptor_set;
  VkShaderModule shader_module;
  PyObject *py_cbv_list;
  PyObject *py_srv_list;
  PyObject *py_uav_list;
  PyObject *py_samplers_list;
  uint32_t push_constant_size;
  uint32_t bindless;
  VkFence dispatch_fence;
} vulkan_Compute;

typedef struct vulkan_Swapchain {
  PyObject_HEAD;
  vulkan_Device *py_device;
  VkSwapchainKHR swapchain;
  VkSemaphore copy_semaphore;
  VkSemaphore present_semaphore;
  VkSurfaceKHR surface;
  VkExtent2D image_extent;
  std::vector<VkImage> images;
  uint32_t image_count;
  VkFormat format;
  bool suboptimal;
  bool out_of_date;
  VkFence *fences;
} vulkan_Swapchain;

typedef struct vulkan_Sampler {
  PyObject_HEAD;
  vulkan_Device *py_device;
  VkSampler sampler;
  VkDescriptorImageInfo descriptor_image_info;
} vulkan_Sampler;

/* ----------------------------------------------------------------------------
   Type objects (defined in their respective .c files)
   ------------------------------------------------------------------------- */
extern PyTypeObject vulkan_Device_Type;
extern PyTypeObject vulkan_Heap_Type;
extern PyTypeObject vulkan_Resource_Type;
extern PyTypeObject vulkan_Compute_Type;
extern PyTypeObject vulkan_Swapchain_Type;
extern PyTypeObject vulkan_Sampler_Type;

/* ----------------------------------------------------------------------------
   Utility functions
   ------------------------------------------------------------------------- */
vulkan_Device *vulkan_Device_get_device(vulkan_Device *self);
uint32_t
vulkan_get_memory_type_index_by_flag(VkPhysicalDeviceMemoryProperties *props,
                                     VkMemoryPropertyFlags flags);
bool vulkan_texture_set_layout(vulkan_Device *py_device, VkImage image,
                               VkImageLayout old_layout,
                               VkImageLayout new_layout, const uint32_t slices);
VkImage vulkan_create_image(VkDevice device, VkImageType image_type,
                            VkFormat format, const uint32_t width,
                            const uint32_t height, const uint32_t depth,
                            const uint32_t slices, const bool sparse);
const char *vulkan_get_spirv_entry_point(const uint32_t *words, uint64_t len);
uint32_t *vulkan_patch_spirv_unknown_uav(const uint32_t *words, uint64_t len,
                                         uint32_t binding);
PyObject *vulkan_instance_check(void);
bool compushady_check_descriptors(
    PyTypeObject *res_type, PyObject *py_cbv,
    std::vector<vulkan_Resource *> &cbv, PyObject *py_srv,
    std::vector<vulkan_Resource *> &srv, PyObject *py_uav,
    std::vector<vulkan_Resource *> &uav, PyTypeObject *sampler_type,
    PyObject *py_samplers, std::vector<vulkan_Sampler *> &samplers);

/* ----------------------------------------------------------------------------
   Timestamp query helpers
   ------------------------------------------------------------------------- */
bool vulkan_device_init_timestamps(vulkan_Device *dev, uint32_t max_queries);
PyObject *vulkan_device_get_timestamps(vulkan_Device *dev, uint32_t count);

/* ----------------------------------------------------------------------------
   Device methods
   ------------------------------------------------------------------------- */
PyObject *vulkan_Device_create_texture2d(vulkan_Device *self, PyObject *args);
PyObject *vulkan_Device_create_buffer(vulkan_Device *self, PyObject *args);
PyObject *vulkan_Device_create_sampler(vulkan_Device *self, PyObject *args);
PyObject *vulkan_Device_create_compute(vulkan_Device *self, PyObject *args,
                                       PyObject *kwds);
PyObject *vulkan_Device_create_swapchain(vulkan_Device *self, PyObject *args);
PyObject *vulkan_Device_create_heap(vulkan_Device *self, PyObject *args);
PyObject *vulkan_Device_get_debug_messages(vulkan_Device *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Resource methods
   ------------------------------------------------------------------------- */
PyObject *vulkan_Resource_upload_subresource(vulkan_Resource *self,
                                             PyObject *args);
PyObject *vulkan_Resource_download_texture(vulkan_Resource *self,
                                           PyObject *args);
PyObject *vulkan_Resource_upload(vulkan_Resource *self, PyObject *args);
PyObject *vulkan_Resource_upload2d(vulkan_Resource *self, PyObject *args);
PyObject *vulkan_Resource_copy_to(vulkan_Resource *self, PyObject *args);
PyObject *vulkan_Resource_readback(vulkan_Resource *self, PyObject *args);
PyObject *vulkan_Resource_upload_subresources(vulkan_Resource *self,
                                              PyObject *args);

/* ----------------------------------------------------------------------------
   Compute methods
   ------------------------------------------------------------------------- */
PyObject *vulkan_Compute_dispatch(vulkan_Compute *self, PyObject *args);
PyObject *vulkan_Compute_dispatch_sequence(vulkan_Compute *self, PyObject *args,
                                           PyObject *kwds);

/* ----------------------------------------------------------------------------
   Swapchain methods
   ------------------------------------------------------------------------- */
PyObject *vulkan_Swapchain_present(vulkan_Swapchain *self, PyObject *args);
PyObject *vulkan_Swapchain_is_suboptimal(vulkan_Swapchain *self,
                                         PyObject *ignored);
PyObject *vulkan_Swapchain_is_out_of_date(vulkan_Swapchain *self,
                                          PyObject *ignored);
PyObject *vulkan_Swapchain_needs_recreation(vulkan_Swapchain *self,
                                            PyObject *ignored);
PyObject *vulkan_Swapchain_present_texture(vulkan_Swapchain *self,
                                           PyObject *args);

/* ----------------------------------------------------------------------------
   Module initialization
   ------------------------------------------------------------------------- */
PyObject *vulkan_get_discovered_devices(PyObject *self, PyObject *args);
PyObject *vulkan_enable_debug(PyObject *self, PyObject *args);
PyObject *vulkan_get_shader_binary_type(PyObject *self);

#endif /* VULKAN_COMMON_H */