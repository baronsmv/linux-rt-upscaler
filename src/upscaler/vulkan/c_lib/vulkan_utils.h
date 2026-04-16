/**
 * @file vulkan_utils.h
 * @brief Utility functions for the Vulkan backend: copy validation, pitch
 * calculation, memory type selection, SPIR‑V helpers, and descriptor checking.
 */

#ifndef VULKAN_UTILS_H
#define VULKAN_UTILS_H

#include <Python.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <vulkan/vulkan.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Forward declarations (to avoid circular includes)
   ------------------------------------------------------------------------- */
typedef struct VkComp_Device VkComp_Device;
typedef struct VkComp_Resource VkComp_Resource;
typedef struct VkComp_Sampler VkComp_Sampler;

/* -------------------------------------------------------------------------
   Size and pitch calculations
   ------------------------------------------------------------------------- */

/**
 * @brief Calculate the total size of a 2D/3D resource given its row pitch.
 * @param pitch Row pitch in bytes.
 * @param width Width in pixels.
 * @param height Height in pixels.
 * @param depth Depth in pixels.
 * @param bytes_per_pixel Bytes per pixel.
 * @return Total size in bytes.
 */
size_t vkcomp_get_size_by_pitch(size_t pitch, size_t width, size_t height,
                                size_t depth, size_t bytes_per_pixel);

/* -------------------------------------------------------------------------
   Copy validation
   ------------------------------------------------------------------------- */

/**
 * @brief Validate the parameters for a resource copy operation and fill
 *        default values for width/height/depth if zero.
 *
 * @param src_is_buffer True if source is a buffer.
 * @param dst_is_buffer True if destination is a buffer.
 * @param size Requested size (buffer copies).
 * @param src_offset Source offset.
 * @param dst_offset Destination offset.
 * @param src_size Total source size.
 * @param dst_size Total destination size.
 * @param src_x, src_y, src_z Source start coordinates.
 * @param src_slice Source array slice.
 * @param src_slices Total source array slices.
 * @param dst_slice Destination array slice.
 * @param dst_slices Total destination array slices.
 * @param src_width, src_height, src_depth Source dimensions.
 * @param dst_width, dst_height, dst_depth Destination dimensions.
 * @param[in,out] dst_x, dst_y, dst_z Destination start coordinates (set to 0
 * for buffer<->texture).
 * @param[in,out] width, height, depth Copy dimensions (filled with source
 * dimensions if 0).
 * @return true if valid, false with Python exception set.
 */
bool vkcomp_check_copy_to(
    bool src_is_buffer, bool dst_is_buffer, uint64_t size, uint64_t src_offset,
    uint64_t dst_offset, uint64_t src_size, uint64_t dst_size, uint32_t src_x,
    uint32_t src_y, uint32_t src_z, uint32_t src_slice, uint32_t src_slices,
    uint32_t dst_slice, uint32_t dst_slices, uint32_t src_width,
    uint32_t src_height, uint32_t src_depth, uint32_t dst_width,
    uint32_t dst_height, uint32_t dst_depth, uint32_t *dst_x, uint32_t *dst_y,
    uint32_t *dst_z, uint32_t *width, uint32_t *height, uint32_t *depth);

/* -------------------------------------------------------------------------
   Descriptor validation (replaces C++ template version)
   ------------------------------------------------------------------------- */

/**
 * @brief Validate and collect resource lists for compute pipeline creation.
 *
 * @param py_resource_type Python type object for Resource.
 * @param py_cbv Python iterable of CBV resources (may be NULL).
 * @param cbv_out Output array of resource pointers (caller must free with
 * PyMem_Free).
 * @param cbv_count Output count.
 * @param py_srv Python iterable of SRV resources (may be NULL).
 * @param srv_out Output array.
 * @param srv_count Output count.
 * @param py_uav Python iterable of UAV resources (may be NULL).
 * @param uav_out Output array.
 * @param uav_count Output count.
 * @param py_sampler_type Python type object for Sampler.
 * @param py_samplers Python iterable of Sampler objects (may be NULL).
 * @param samplers_out Output array.
 * @param samplers_count Output count.
 * @return true on success, false on error (Python exception set).
 */
bool vkcomp_check_descriptors(PyTypeObject *py_resource_type, PyObject *py_cbv,
                              VkComp_Resource ***cbv_out, size_t *cbv_count,
                              PyObject *py_srv, VkComp_Resource ***srv_out,
                              size_t *srv_count, PyObject *py_uav,
                              VkComp_Resource ***uav_out, size_t *uav_count,
                              PyTypeObject *py_sampler_type,
                              PyObject *py_samplers,
                              VkComp_Sampler ***samplers_out,
                              size_t *samplers_count);

/* -------------------------------------------------------------------------
   Vulkan helpers
   ------------------------------------------------------------------------- */

/**
 * @brief Find a memory type index matching the given requirements.
 */
uint32_t vkcomp_find_memory_type(const VkPhysicalDeviceMemoryProperties *props,
                                 uint32_t type_filter,
                                 VkMemoryPropertyFlags properties);

/**
 * @brief Transition an image to a new layout using a temporary command buffer.
 */
bool vkcomp_texture_set_layout(VkComp_Device *device, VkImage image,
                               VkImageLayout old_layout,
                               VkImageLayout new_layout, uint32_t slices);

/**
 * @brief Create a Vulkan image with standard usage flags for compute.
 */
VkImage vkcomp_create_image(VkDevice device, VkImageType image_type,
                            VkFormat format, uint32_t width, uint32_t height,
                            uint32_t depth, uint32_t slices, bool sparse);

/**
 * @brief Extract the entry point name from SPIR‑V (simplified: returns "main").
 */
const char *vkcomp_get_spirv_entry_point(const uint32_t *words, size_t len);

/**
 * @brief Patch SPIR‑V to replace Unknown format with a concrete one for BGRA
 * UAVs. Returns a newly allocated buffer (caller must PyMem_Free) or NULL if
 * not needed.
 */
uint32_t *vkcomp_patch_spirv_unknown_uav(const uint32_t *words, size_t len,
                                         uint32_t binding);

/**
 * @brief Submit a command buffer and wait for completion using a timeline
 * semaphore.
 */
VkResult vkcomp_submit_and_wait(VkComp_Device *device, VkCommandBuffer cmd,
                                VkFence fence);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_UTILS_H */