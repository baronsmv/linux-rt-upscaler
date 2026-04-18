/**
 * @file vk_swapchain.cpp
 * @brief Vulkan swapchain implementation with triple buffering support.
 *
 * This file implements the vk.Swapchain Python type, which manages a Vulkan
 * swapchain for presenting rendered images to a window. It supports
 * configurable image counts (double/triple buffering) and various present modes.
 * Synchronisation is handled via semaphores and fences to ensure correct frame
 * pacing and avoid GPU stalls.
 */

#include "vk_swapchain.h"
#include "vk_device.h"
#include "vk_utils.h"
#include <cstring>
#include <algorithm>
#include <xcb/xcb.h>
#include <vulkan/vulkan_xcb.h>

extern PyObject *vk_SwapchainError;

/* ----------------------------------------------------------------------------
   Helper: Create a Vulkan surface from an X11 window handle
   ------------------------------------------------------------------------- */
static VkResult create_xcb_surface(VkInstance instance,
                                   void* display_ptr,
                                   void* window_ptr,
                                   VkSurfaceKHR* out_surface) {
    VkXcbSurfaceCreateInfoKHR surface_info = {
        VK_STRUCTURE_TYPE_XCB_SURFACE_CREATE_INFO_KHR
    };
    surface_info.connection = static_cast<xcb_connection_t*>(display_ptr);
    surface_info.window = static_cast<xcb_window_t>(reinterpret_cast<uintptr_t>(window_ptr));

    PFN_vkCreateXcbSurfaceKHR func = (PFN_vkCreateXcbSurfaceKHR)
        vkGetInstanceProcAddr(instance, "vkCreateXcbSurfaceKHR");
    if (!func) return VK_ERROR_EXTENSION_NOT_PRESENT;
    return func(instance, &surface_info, nullptr, out_surface);
}

/* ----------------------------------------------------------------------------
   Helper: Choose swapchain image count (clamped to surface capabilities)
   ------------------------------------------------------------------------- */
static uint32_t choose_image_count(const VkSurfaceCapabilitiesKHR& caps,
                                   uint32_t desired) {
    uint32_t count = desired;
    if (caps.maxImageCount > 0 && count > caps.maxImageCount)
        count = caps.maxImageCount;
    if (count < caps.minImageCount)
        count = caps.minImageCount;
    return count;
}

/* ----------------------------------------------------------------------------
   Helper: Choose present mode with robust fallback
   ------------------------------------------------------------------------- */
static VkPresentModeKHR choose_present_mode(const std::vector<VkPresentModeKHR>& modes,
                                            const char* mode_str, bool vsync) {
    auto has_mode = [&](VkPresentModeKHR mode) {
        for (auto m : modes) if (m == mode) return true;
        return false;
    };

    // Debug output to verify available modes
    fprintf(stderr, "[Vulkan] Available present modes:");
    for (auto m : modes) {
        const char* name = "?";
        if (m == VK_PRESENT_MODE_IMMEDIATE_KHR) name = "immediate";
        else if (m == VK_PRESENT_MODE_MAILBOX_KHR) name = "mailbox";
        else if (m == VK_PRESENT_MODE_FIFO_KHR) name = "fifo";
        else if (m == VK_PRESENT_MODE_FIFO_RELAXED_KHR) name = "fifo_relaxed";
        fprintf(stderr, " %s(%d)", name, m);
    }
    fprintf(stderr, "\n");

    if (mode_str) {
        if (strcmp(mode_str, "immediate") == 0 && has_mode(VK_PRESENT_MODE_IMMEDIATE_KHR))
            return VK_PRESENT_MODE_IMMEDIATE_KHR;
        if (strcmp(mode_str, "mailbox") == 0 && has_mode(VK_PRESENT_MODE_MAILBOX_KHR))
            return VK_PRESENT_MODE_MAILBOX_KHR;
        if (strcmp(mode_str, "fifo") == 0 && has_mode(VK_PRESENT_MODE_FIFO_KHR))
            return VK_PRESENT_MODE_FIFO_KHR;
    }

    if (!vsync && has_mode(VK_PRESENT_MODE_MAILBOX_KHR))
        return VK_PRESENT_MODE_MAILBOX_KHR;
    if (has_mode(VK_PRESENT_MODE_FIFO_KHR))
        return VK_PRESENT_MODE_FIFO_KHR;

    // Absolute fallback – first available mode
    fprintf(stderr, "[Vulkan] Using fallback present mode: %d\n", modes[0]);
    return modes[0];
}

/* ----------------------------------------------------------------------------
   Helper: Choose surface format (prefer SRGB if available)
   ------------------------------------------------------------------------- */
static VkSurfaceFormatKHR choose_surface_format(
    const std::vector<VkSurfaceFormatKHR>& formats,
    int requested_format) {
    // If a specific format constant was provided, map to VkFormat
    if (requested_format > 0) {
        auto it = vk_format_map.find(requested_format);
        if (it != vk_format_map.end()) {
            VkFormat target = it->second.first;
            for (const auto& fmt : formats)
                if (fmt.format == target && fmt.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
                    return fmt;
        }
    }
    // Prefer SRGB
    for (const auto& fmt : formats)
        if (fmt.format == VK_FORMAT_B8G8R8A8_SRGB && fmt.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
            return fmt;
    // Fallback to first available
    return formats[0];
}

/* ----------------------------------------------------------------------------
   Helper: Create image views for swapchain images
   ------------------------------------------------------------------------- */
static bool create_image_views(VkDevice device, VkFormat format,
                               const std::vector<VkImage>& images,
                               std::vector<VkImageView>& out_views) {
    out_views.resize(images.size());
    VkImageViewCreateInfo view_info = { VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO };
    view_info.viewType = VK_IMAGE_VIEW_TYPE_2D;
    view_info.format = format;
    view_info.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    view_info.subresourceRange.levelCount = 1;
    view_info.subresourceRange.layerCount = 1;

    for (size_t i = 0; i < images.size(); ++i) {
        view_info.image = images[i];
        VkResult res = vkCreateImageView(device, &view_info, nullptr, &out_views[i]);
        if (res != VK_SUCCESS) {
            for (size_t j = 0; j < i; ++j)
                vkDestroyImageView(device, out_views[j], nullptr);
            return false;
        }
    }
    return true;
}

/* ----------------------------------------------------------------------------
   Helper: Create synchronisation objects and command buffers for each frame
   ------------------------------------------------------------------------- */
static bool create_frame_sync(vk_Device* dev, uint32_t count,
                              std::vector<FrameSync>& out_sync) {
    out_sync.resize(count);
    VkSemaphoreCreateInfo sem_info = { VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO };
    VkFenceCreateInfo fence_info = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    fence_info.flags = VK_FENCE_CREATE_SIGNALED_BIT; // First frame doesn't wait

    for (uint32_t i = 0; i < count; ++i) {
        FrameSync& sync = out_sync[i];
        if (vkCreateSemaphore(dev->device, &sem_info, nullptr, &sync.image_available_semaphore) != VK_SUCCESS ||
            vkCreateSemaphore(dev->device, &sem_info, nullptr, &sync.render_finished_semaphore) != VK_SUCCESS ||
            vkCreateFence(dev->device, &fence_info, nullptr, &sync.in_flight_fence) != VK_SUCCESS) {
            for (uint32_t j = 0; j < i; ++j) {
                vkDestroySemaphore(dev->device, out_sync[j].image_available_semaphore, nullptr);
                vkDestroySemaphore(dev->device, out_sync[j].render_finished_semaphore, nullptr);
                vkDestroyFence(dev->device, out_sync[j].in_flight_fence, nullptr);
                vkFreeCommandBuffers(dev->device, dev->command_pool, 1, &out_sync[j].command_buffer);
            }
            return false;
        }

        // Allocate a persistent command buffer for this frame
        VkCommandBufferAllocateInfo alloc_info = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO };
        alloc_info.commandPool = dev->command_pool;
        alloc_info.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        alloc_info.commandBufferCount = 1;
        if (vkAllocateCommandBuffers(dev->device, &alloc_info, &sync.command_buffer) != VK_SUCCESS) {
            vkDestroySemaphore(dev->device, sync.image_available_semaphore, nullptr);
            vkDestroySemaphore(dev->device, sync.render_finished_semaphore, nullptr);
            vkDestroyFence(dev->device, sync.in_flight_fence, nullptr);
            for (uint32_t j = 0; j < i; ++j) {
                vkDestroySemaphore(dev->device, out_sync[j].image_available_semaphore, nullptr);
                vkDestroySemaphore(dev->device, out_sync[j].render_finished_semaphore, nullptr);
                vkDestroyFence(dev->device, out_sync[j].in_flight_fence, nullptr);
                vkFreeCommandBuffers(dev->device, dev->command_pool, 1, &out_sync[j].command_buffer);
            }
            return false;
        }
    }
    return true;
}

/* ----------------------------------------------------------------------------
   vk_Swapchain_recreate - internal recreation logic
   ------------------------------------------------------------------------- */
bool vk_Swapchain_recreate(vk_Swapchain* self, uint32_t width, uint32_t height) {
    vk_Device* dev = self->py_device;
    VkPhysicalDevice phys = dev->physical_device;
    VkDevice device = dev->device;

    // Query current surface capabilities
    VkSurfaceCapabilitiesKHR caps;
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR(phys, self->surface, &caps);

    // Determine extent
    if (width == 0 || height == 0) {
        if (caps.currentExtent.width != UINT32_MAX) {
            self->image_extent = caps.currentExtent;
        } else {
            self->image_extent.width = std::clamp(width ? width : 800,
                                                  caps.minImageExtent.width,
                                                  caps.maxImageExtent.width);
            self->image_extent.height = std::clamp(height ? height : 600,
                                                   caps.minImageExtent.height,
                                                   caps.maxImageExtent.height);
        }
    } else {
        self->image_extent.width = width;
        self->image_extent.height = height;
    }

    // Wait for device idle before destroying old swapchain
    vkDeviceWaitIdle(device);

    // Destroy old synchronization objects and command buffers
    for (auto& sync : self->frame_sync) {
        vkDestroySemaphore(device, sync.image_available_semaphore, nullptr);
        vkDestroySemaphore(device, sync.render_finished_semaphore, nullptr);
        vkDestroyFence(device, sync.in_flight_fence, nullptr);
        vkFreeCommandBuffers(device, dev->command_pool, 1, &sync.command_buffer);
    }
    self->frame_sync.clear();

    for (auto view : self->image_views)
        vkDestroyImageView(device, view, nullptr);
    self->image_views.clear();

    // Create new swapchain
    VkSwapchainCreateInfoKHR swap_info = { VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR };
    swap_info.surface = self->surface;
    swap_info.minImageCount = choose_image_count(caps, self->desired_image_count);
    swap_info.imageFormat = self->format;
    swap_info.imageColorSpace = self->color_space;
    swap_info.imageExtent = self->image_extent;
    swap_info.imageArrayLayers = 1;
    swap_info.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT |
                       VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    swap_info.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
    swap_info.preTransform = caps.currentTransform;
    VkCompositeAlphaFlagBitsKHR compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
    if (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR) {
        compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
    } else if (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR) {
        compositeAlpha = VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR;
    } else if (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR) {
        compositeAlpha = VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR;
    }
    swap_info.compositeAlpha = compositeAlpha;
    swap_info.presentMode = self->present_mode;
    swap_info.clipped = VK_TRUE;
    swap_info.oldSwapchain = self->swapchain;

    VkResult res = vkCreateSwapchainKHR(device, &swap_info, nullptr, &self->swapchain);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Failed to create swapchain (error %d)", res);
        return false;
    }

    if (swap_info.oldSwapchain != VK_NULL_HANDLE)
        vkDestroySwapchainKHR(device, swap_info.oldSwapchain, nullptr);

    // Retrieve swapchain images
    uint32_t count;
    vkGetSwapchainImagesKHR(device, self->swapchain, &count, nullptr);
    self->images.resize(count);
    vkGetSwapchainImagesKHR(device, self->swapchain, &count, self->images.data());
    self->image_count = count;

    // Create image views
    if (!create_image_views(device, self->format, self->images, self->image_views)) {
        PyErr_SetString(vk_SwapchainError, "Failed to create swapchain image views");
        return false;
    }

    // Create synchronization objects and command buffers (one per image)
    if (!create_frame_sync(dev, count, self->frame_sync)) {
        PyErr_SetString(vk_SwapchainError, "Failed to create frame synchronization objects");
        return false;
    }

    self->current_frame = 0;
    self->suboptimal = false;
    self->out_of_date = false;
    self->framebuffer_resized = false;

    return true;
}

/* ----------------------------------------------------------------------------
   vk_Device_create_swapchain_impl
   ------------------------------------------------------------------------- */
PyObject* vk_Device_create_swapchain_impl(vk_Device* self, PyObject* args) {
    PyObject* window_tuple;
    int format;
    int num_buffers = 3;
    int width = 0, height = 0;
    const char* present_mode_str = nullptr;

    if (!PyArg_ParseTuple(args, "O!i|iIIs", &PyTuple_Type, &window_tuple,
                          &format, &num_buffers, &width, &height, &present_mode_str))
        return nullptr;

    if (!vk_instance_ensure()) return nullptr;
    vk_Device* dev = vk_Device_get_initialized(self);
    if (!dev) return nullptr;

    // Extract window handle from tuple
    if (PyTuple_Size(window_tuple) != 2) {
        PyErr_SetString(PyExc_ValueError,
                        "window_handle must be a tuple (display_ptr, window_ptr)");
        return nullptr;
    }
    void* display_ptr = PyLong_AsVoidPtr(PyTuple_GetItem(window_tuple, 0));
    void* window_ptr = PyLong_AsVoidPtr(PyTuple_GetItem(window_tuple, 1));
    if (PyErr_Occurred()) return nullptr;

    // Create surface
    VkSurfaceKHR surface;
    VkResult res = create_xcb_surface(vk_instance, display_ptr, window_ptr, &surface);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Failed to create XCB surface (error %d)", res);
        return nullptr;
    }

    // Verify queue family supports presentation
    VkBool32 supports_present;
    vkGetPhysicalDeviceSurfaceSupportKHR(dev->physical_device,
                                         dev->queue_family_index,
                                         surface, &supports_present);
    if (!supports_present) {
        vkDestroySurfaceKHR(vk_instance, surface, nullptr);
        PyErr_SetString(vk_SwapchainError,
                        "Queue family does not support presentation");
        return nullptr;
    }

    // Query surface formats and choose
    uint32_t fmt_count;
    vkGetPhysicalDeviceSurfaceFormatsKHR(dev->physical_device, surface,
                                         &fmt_count, nullptr);
    std::vector<VkSurfaceFormatKHR> formats(fmt_count);
    vkGetPhysicalDeviceSurfaceFormatsKHR(dev->physical_device, surface,
                                         &fmt_count, formats.data());
    VkSurfaceFormatKHR chosen_fmt = choose_surface_format(formats, format);

    // Query present modes and choose
    uint32_t mode_count;
    vkGetPhysicalDeviceSurfacePresentModesKHR(dev->physical_device, surface,
                                              &mode_count, nullptr);
    std::vector<VkPresentModeKHR> modes(mode_count);
    vkGetPhysicalDeviceSurfacePresentModesKHR(dev->physical_device, surface,
                                              &mode_count, modes.data());
    bool vsync = (present_mode_str == nullptr || strcmp(present_mode_str, "fifo") == 0);
    VkPresentModeKHR present_mode = choose_present_mode(modes, present_mode_str, vsync);

    // Allocate Python object
    vk_Swapchain* sw = PyObject_New(vk_Swapchain, &vk_Swapchain_Type);
    if (!sw) {
        vkDestroySurfaceKHR(vk_instance, surface, nullptr);
        return PyErr_NoMemory();
    }
    VK_CLEAR_OBJECT(sw);
    sw->py_device = dev;
    Py_INCREF(dev);
    sw->surface = surface;
    sw->format = chosen_fmt.format;
    sw->color_space = chosen_fmt.colorSpace;
    sw->desired_image_count = num_buffers;
    sw->present_mode = present_mode;
    sw->vsync = vsync;
    sw->swapchain = VK_NULL_HANDLE;

    if (!vk_Swapchain_recreate(sw, width, height)) {
        vkDestroySurfaceKHR(vk_instance, surface, nullptr);
        Py_DECREF(sw);
        return nullptr;
    }

    return reinterpret_cast<PyObject*>(sw);
}

/* ----------------------------------------------------------------------------
   vk_Swapchain_dealloc
   ------------------------------------------------------------------------- */
void vk_Swapchain_dealloc(vk_Swapchain* self) {
    if (self->py_device) {
        VkDevice device = self->py_device->device;
        vkDeviceWaitIdle(device);

        for (auto& sync : self->frame_sync) {
            vkDestroySemaphore(device, sync.image_available_semaphore, nullptr);
            vkDestroySemaphore(device, sync.render_finished_semaphore, nullptr);
            vkDestroyFence(device, sync.in_flight_fence, nullptr);
            vkFreeCommandBuffers(device, self->py_device->command_pool, 1, &sync.command_buffer);
        }
        for (auto view : self->image_views)
            vkDestroyImageView(device, view, nullptr);
        if (self->swapchain)
            vkDestroySwapchainKHR(device, self->swapchain, nullptr);
        if (self->surface)
            vkDestroySurfaceKHR(vk_instance, self->surface, nullptr);
        Py_DECREF(self->py_device);
    }
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject*>(self));
}

/* ----------------------------------------------------------------------------
   vk_Swapchain_acquire_next_image
   ------------------------------------------------------------------------- */
PyObject* vk_Swapchain_acquire_next_image(vk_Swapchain* self, PyObject* args) {
    vk_Device* dev = self->py_device;
    FrameSync& sync = self->frame_sync[self->current_frame];

    // Wait for the fence to ensure frame resources are free
    vkWaitForFences(dev->device, 1, &sync.in_flight_fence, VK_TRUE, UINT64_MAX);
    vkResetFences(dev->device, 1, &sync.in_flight_fence);

    uint32_t image_index;
    VkResult res = vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                                         sync.image_available_semaphore,
                                         VK_NULL_HANDLE, &image_index);
    if (res == VK_ERROR_OUT_OF_DATE_KHR) {
        self->out_of_date = true;
        return PyLong_FromLong(-1);
    } else if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
        PyErr_Format(vk_SwapchainError, "Failed to acquire next image (error %d)", res);
        return nullptr;
    }

    self->image_index = image_index;
    if (res == VK_SUBOPTIMAL_KHR)
        self->suboptimal = true;

    return PyLong_FromUnsignedLong(image_index);
}

/* ----------------------------------------------------------------------------
   vk_Swapchain_present (robust, asynchronous, with per-frame command buffers)
   ------------------------------------------------------------------------- */
PyObject* vk_Swapchain_present(vk_Swapchain* self, PyObject* args) {
    PyObject* texture_obj;
    int x = 0, y = 0;
    int wait_for_fence = 1;
    if (!PyArg_ParseTuple(args, "O|iip", &texture_obj, &x, &y, &wait_for_fence))
        return nullptr;

    // Validate texture
    if (!PyObject_TypeCheck(texture_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "texture must be a Resource");
        return nullptr;
    }
    vk_Resource* texture = reinterpret_cast<vk_Resource*>(texture_obj);
    if (!texture->image) {
        PyErr_SetString(PyExc_TypeError, "texture must be an image");
        return nullptr;
    }

    // Ensure texture dimensions match swapchain
    if (texture->image_extent.width != self->image_extent.width ||
        texture->image_extent.height != self->image_extent.height) {
        PyErr_Format(PyExc_ValueError,
            "Texture dimensions (%ux%u) must match swapchain (%ux%u)",
            texture->image_extent.width, texture->image_extent.height,
            self->image_extent.width, self->image_extent.height);
        return nullptr;
    }

    vk_Device* dev = self->py_device;
    FrameSync& sync = self->frame_sync[self->current_frame];

    // ALWAYS wait for the fence – ensures the previous frame's GPU work is done.
    vkWaitForFences(dev->device, 1, &sync.in_flight_fence, VK_TRUE, UINT64_MAX);
    vkResetFences(dev->device, 1, &sync.in_flight_fence);

    // Acquire next swapchain image
    uint32_t image_index;
    VkResult res = vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                                         sync.image_available_semaphore,
                                         VK_NULL_HANDLE, &image_index);
    if (res == VK_ERROR_OUT_OF_DATE_KHR) {
        self->out_of_date = true;
        Py_RETURN_FALSE;
    } else if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
        PyErr_Format(vk_SwapchainError, "Failed to acquire next image (error %d)", res);
        return nullptr;
    }
    self->image_index = image_index;
    if (res == VK_SUBOPTIMAL_KHR)
        self->suboptimal = true;

    // Record commands into the per‑frame command buffer
    VkCommandBuffer cmd = sync.command_buffer;
    VkCommandBufferBeginInfo begin_info = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    begin_info.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &begin_info);

    // Transition swapchain image to transfer destination
    VkImageMemoryBarrier barrier = { VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER };
    barrier.srcAccessMask = 0;
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.oldLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.image = self->images[image_index];
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.layerCount = 1;
    vkCmdPipelineBarrier(cmd,
                         VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT,
                         0, 0, nullptr, 0, nullptr, 1, &barrier);

    // Ensure all compute writes to the texture are visible to the copy operation
    VkMemoryBarrier mem_barrier = { VK_STRUCTURE_TYPE_MEMORY_BARRIER };
    mem_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    mem_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    vkCmdPipelineBarrier(cmd,
        VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,  // src stage
        VK_PIPELINE_STAGE_TRANSFER_BIT,        // dst stage
        0,
        1, &mem_barrier,
        0, nullptr,
        0, nullptr);

    // Transition source texture to TRANSFER_SRC_OPTIMAL
    VkImageMemoryBarrier src_barrier = { VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER };
    src_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    src_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    src_barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
src_barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    src_barrier.image = texture->image;
    src_barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    src_barrier.subresourceRange.levelCount = 1;
    src_barrier.subresourceRange.layerCount = 1;
    vkCmdPipelineBarrier(cmd,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT,
                         0, 0, nullptr, 0, nullptr, 1, &src_barrier);

    // Copy from texture to swapchain image at (x, y)
    VkImageCopy copy_region = {};
    copy_region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    copy_region.srcSubresource.layerCount = 1;
    copy_region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    copy_region.dstSubresource.layerCount = 1;
    copy_region.srcOffset = {0, 0, 0};
    copy_region.dstOffset = {x, y, 0};
    // Copy entire texture (dimensions already validated)
    copy_region.extent = {
        texture->image_extent.width,
        texture->image_extent.height,
        1
    };

    // Clear the entire swapchain image to black to avoid stale content
    VkClearColorValue clear_color = {{0.0f, 0.0f, 0.0f, 1.0f}};
    VkImageSubresourceRange clear_range = {
        VK_IMAGE_ASPECT_COLOR_BIT,  // aspectMask
        0,                          // baseMipLevel
        1,                          // levelCount
        0,                          // baseArrayLayer
        1                           // layerCount
    };
    vkCmdClearColorImage(cmd,
        self->images[image_index],
        VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
        &clear_color,
        1,
        &clear_range);

    vkCmdCopyImage(cmd,
                   texture->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   self->images[image_index], VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   1, &copy_region);

    // Transition source texture back to GENERAL (for next frame's compute)
    src_barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    src_barrier.dstAccessMask = 0;
    src_barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    src_barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    vkCmdPipelineBarrier(cmd,
                         VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                         0, 0, nullptr, 0, nullptr, 1, &src_barrier);

    // Transition to present layout
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.dstAccessMask = 0;
    barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
    vkCmdPipelineBarrier(cmd,
                         VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                         0, 0, nullptr, 0, nullptr, 1, &barrier);

    vkEndCommandBuffer(cmd);

    // Submit: wait for image_available, signal render_finished, and signal fence
    VkPipelineStageFlags wait_stage = VK_PIPELINE_STAGE_TRANSFER_BIT;
    VkSubmitInfo submit = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
    submit.waitSemaphoreCount = 1;
    submit.pWaitSemaphores = &sync.image_available_semaphore;
    submit.pWaitDstStageMask = &wait_stage;
    submit.commandBufferCount = 1;
    submit.pCommandBuffers = &cmd;
    submit.signalSemaphoreCount = 1;
    submit.pSignalSemaphores = &sync.render_finished_semaphore;

    res = vkQueueSubmit(dev->queue, 1, &submit, sync.in_flight_fence);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Failed to submit copy command (error %d)", res);
        return nullptr;
    }

    // Present
    VkPresentInfoKHR present_info = { VK_STRUCTURE_TYPE_PRESENT_INFO_KHR };
    present_info.waitSemaphoreCount = 1;
    present_info.pWaitSemaphores = &sync.render_finished_semaphore;
    present_info.swapchainCount = 1;
    present_info.pSwapchains = &self->swapchain;
    present_info.pImageIndices = &image_index;

    res = vkQueuePresentKHR(dev->queue, &present_info);

    if (res == VK_ERROR_OUT_OF_DATE_KHR || res == VK_SUBOPTIMAL_KHR || self->framebuffer_resized) {
        self->out_of_date = true;
        Py_RETURN_FALSE;
    } else if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Failed to present image (error %d)", res);
        return nullptr;
    }

    // Advance to next frame
    self->current_frame = (self->current_frame + 1) % self->image_count;

    Py_RETURN_TRUE;
}

/* ----------------------------------------------------------------------------
   Status queries
   ------------------------------------------------------------------------- */
PyObject* vk_Swapchain_is_suboptimal(vk_Swapchain* self, PyObject* ignored) {
    if (self->suboptimal) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}
PyObject* vk_Swapchain_is_out_of_date(vk_Swapchain* self, PyObject* ignored) {
    if (self->out_of_date) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}
PyObject* vk_Swapchain_needs_recreation(vk_Swapchain* self, PyObject* ignored) {
    if (self->out_of_date || self->suboptimal) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

PyObject* vk_Swapchain_get_current_image(vk_Swapchain* self, PyObject* ignored) {
    return PyLong_FromUnsignedLong(self->image_index);
}
PyObject* vk_Swapchain_get_image_view(vk_Swapchain* self, PyObject* ignored) {
    Py_RETURN_NONE;
}
PyObject* vk_Swapchain_recreate_method(vk_Swapchain* self, PyObject* args) {
    int width = 0, height = 0;
    if (!PyArg_ParseTuple(args, "|ii", &width, &height)) return nullptr;
    if (!vk_Swapchain_recreate(self, width, height)) return nullptr;
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   Type definition
   ------------------------------------------------------------------------- */
static PyMethodDef vk_Swapchain_methods[] = {
    {"acquire_next_image", (PyCFunction)vk_Swapchain_acquire_next_image, METH_NOARGS,
     "Acquire the next swapchain image."},
    {"present", (PyCFunction)vk_Swapchain_present, METH_VARARGS,
     "Copy a texture to the swapchain and present."},
    {"is_suboptimal", (PyCFunction)vk_Swapchain_is_suboptimal, METH_NOARGS,
     "Return True if swapchain is suboptimal."},
    {"is_out_of_date", (PyCFunction)vk_Swapchain_is_out_of_date, METH_NOARGS,
     "Return True if swapchain is out of date."},
    {"needs_recreation", (PyCFunction)vk_Swapchain_needs_recreation, METH_NOARGS,
     "Return True if swapchain needs recreation."},
    {"recreate", (PyCFunction)vk_Swapchain_recreate_method, METH_VARARGS,
     "Recreate the swapchain."},
    {"get_current_image", (PyCFunction)vk_Swapchain_get_current_image, METH_NOARGS, nullptr},
    {"get_image_view", (PyCFunction)vk_Swapchain_get_image_view, METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyMemberDef vk_Swapchain_members[] = {
    {"width", T_UINT, offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, width), 0,
     "Current swapchain width."},
    {"height", T_UINT, offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, height), 0,
     "Current swapchain height."},
    {"image_count", T_UINT, offsetof(vk_Swapchain, image_count), 0,
     "Number of images in the swapchain."},
    {"vsync", T_BOOL, offsetof(vk_Swapchain, vsync), 0,
     "Whether vertical sync is enabled."},
    {nullptr}
};

PyTypeObject vk_Swapchain_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name = "vulkan.Swapchain",
    .tp_basicsize = sizeof(vk_Swapchain),
    .tp_dealloc = (destructor)vk_Swapchain_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Swapchain_methods,
    .tp_members = vk_Swapchain_members,
};