#include "vk_swapchain.h"
#include "vk_device.h"
#include "vk_utils.h"
#include <cstring>
#include <algorithm>
#include <xcb/xcb.h>
#include <vulkan/vulkan_xcb.h>

extern PyObject *vk_SwapchainError;

// -----------------------------------------------------------------------------
// XCB Surface Creation
// -----------------------------------------------------------------------------
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

// -----------------------------------------------------------------------------
// Image Count Selection
// -----------------------------------------------------------------------------
static uint32_t choose_image_count(const VkSurfaceCapabilitiesKHR& caps,
                                   uint32_t desired) {
    uint32_t count = desired;
    if (caps.maxImageCount > 0 && count > caps.maxImageCount)
        count = caps.maxImageCount;
    if (count < caps.minImageCount)
        count = caps.minImageCount;
    return count;
}

// -----------------------------------------------------------------------------
// Present Mode Selection (FIFO default)
// -----------------------------------------------------------------------------
static VkPresentModeKHR choose_present_mode(VkPhysicalDevice phys,
                                            VkSurfaceKHR surface,
                                            const char* mode_str) {
    uint32_t count;
    vkGetPhysicalDeviceSurfacePresentModesKHR(phys, surface, &count, nullptr);
    std::vector<VkPresentModeKHR> modes(count);
    vkGetPhysicalDeviceSurfacePresentModesKHR(phys, surface, &count, modes.data());

    VkPresentModeKHR desired;
    if (mode_str && strcmp(mode_str, "immediate") == 0)
        desired = VK_PRESENT_MODE_IMMEDIATE_KHR;
    else if (mode_str && strcmp(mode_str, "mailbox") == 0)
        desired = VK_PRESENT_MODE_MAILBOX_KHR;
    else
        desired = VK_PRESENT_MODE_FIFO_KHR;

    for (auto m : modes)
        if (m == desired) return desired;
    return VK_PRESENT_MODE_FIFO_KHR; // mandatory fallback
}

// -----------------------------------------------------------------------------
// Surface Format Selection (prefer SRGB)
// -----------------------------------------------------------------------------
static VkSurfaceFormatKHR choose_surface_format(
    const std::vector<VkSurfaceFormatKHR>& formats,
    int requested_format) {
    if (requested_format > 0) {
        auto it = vk_format_map.find(requested_format);
        if (it != vk_format_map.end()) {
            VkFormat target = it->second.first;
            for (const auto& fmt : formats)
                if (fmt.format == target && fmt.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
                    return fmt;
        }
    }
    for (const auto& fmt : formats)
        if (fmt.format == VK_FORMAT_B8G8R8A8_SRGB && fmt.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
            return fmt;
    return formats[0];
}

// -----------------------------------------------------------------------------
// Image View Creation
// -----------------------------------------------------------------------------
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
        if (vkCreateImageView(device, &view_info, nullptr, &out_views[i]) != VK_SUCCESS) {
            for (size_t j = 0; j < i; ++j)
                vkDestroyImageView(device, out_views[j], nullptr);
            return false;
        }
    }
    return true;
}

// -----------------------------------------------------------------------------
// Recreate Swapchain (allocates per-image fences, shared semaphores)
// -----------------------------------------------------------------------------
bool vk_Swapchain_recreate(vk_Swapchain* self, uint32_t width, uint32_t height) {
    vk_Device* dev = self->py_device;
    VkDevice device = dev->device;
    VkPhysicalDevice phys = dev->physical_device;

    // Query surface capabilities
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

    vkDeviceWaitIdle(device);

    // Destroy old per-image resources
    if (self->fences) {
        for (uint32_t i = 0; i < self->image_count; ++i)
            vkDestroyFence(device, self->fences[i], nullptr);
        PyMem_Free(self->fences);
        self->fences = nullptr;
    }
    if (self->image_available_semaphore) {
        vkDestroySemaphore(device, self->image_available_semaphore, nullptr);
        self->image_available_semaphore = VK_NULL_HANDLE;
    }
    if (self->render_finished_semaphore) {
        vkDestroySemaphore(device, self->render_finished_semaphore, nullptr);
        self->render_finished_semaphore = VK_NULL_HANDLE;
    }
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
    swap_info.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
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

    // Retrieve images
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

    // Create shared semaphores
    VkSemaphoreCreateInfo sem_info = { VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO };
    if (vkCreateSemaphore(device, &sem_info, nullptr, &self->image_available_semaphore) != VK_SUCCESS ||
        vkCreateSemaphore(device, &sem_info, nullptr, &self->render_finished_semaphore) != VK_SUCCESS) {
        PyErr_SetString(vk_SwapchainError, "Failed to create semaphores");
        return false;
    }

    // Create per-image fences (signaled initially)
    self->fences = (VkFence*)PyMem_Malloc(sizeof(VkFence) * self->image_count);
    VkFenceCreateInfo fence_info = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    fence_info.flags = VK_FENCE_CREATE_SIGNALED_BIT;
    for (uint32_t i = 0; i < self->image_count; ++i) {
        if (vkCreateFence(device, &fence_info, nullptr, &self->fences[i]) != VK_SUCCESS) {
            for (uint32_t j = 0; j < i; ++j)
                vkDestroyFence(device, self->fences[j], nullptr);
            PyMem_Free(self->fences);
            self->fences = nullptr;
            PyErr_SetString(vk_SwapchainError, "Failed to create fences");
            return false;
        }
    }

    // Allocate per-image command buffers (persistent, avoids per-frame allocation jitter)
    self->command_buffers = (VkCommandBuffer*)PyMem_Malloc(sizeof(VkCommandBuffer) * self->image_count);
    VkCommandBufferAllocateInfo alloc_info = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO };
    alloc_info.commandPool = dev->command_pool;
    alloc_info.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    alloc_info.commandBufferCount = self->image_count;
    if (vkAllocateCommandBuffers(device, &alloc_info, self->command_buffers) != VK_SUCCESS) {
        for (uint32_t j = 0; j < self->image_count; ++j)
            vkDestroyFence(device, self->fences[j], nullptr);
        PyMem_Free(self->fences);
        PyMem_Free(self->command_buffers);
        self->fences = nullptr;
        self->command_buffers = nullptr;
        PyErr_SetString(vk_SwapchainError, "Failed to allocate command buffers");
        return false;
    }

    self->suboptimal = false;
    self->out_of_date = false;
    self->framebuffer_resized = false;
    return true;
}

// -----------------------------------------------------------------------------
// Device::create_swapchain Implementation
// -----------------------------------------------------------------------------
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

    if (PyTuple_Size(window_tuple) != 2) {
        PyErr_SetString(PyExc_ValueError, "window_handle must be (display_ptr, window_ptr)");
        return nullptr;
    }
    void* display_ptr = PyLong_AsVoidPtr(PyTuple_GetItem(window_tuple, 0));
    void* window_ptr = PyLong_AsVoidPtr(PyTuple_GetItem(window_tuple, 1));
    if (PyErr_Occurred()) return nullptr;

    VkSurfaceKHR surface;
    VkResult res = create_xcb_surface(vk_instance, display_ptr, window_ptr, &surface);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Failed to create XCB surface (error %d)", res);
        return nullptr;
    }

    VkBool32 supports_present;
    vkGetPhysicalDeviceSurfaceSupportKHR(dev->physical_device, dev->queue_family_index,
                                         surface, &supports_present);
    if (!supports_present) {
        vkDestroySurfaceKHR(vk_instance, surface, nullptr);
        PyErr_SetString(vk_SwapchainError, "Queue family does not support presentation");
        return nullptr;
    }

    uint32_t fmt_count;
    vkGetPhysicalDeviceSurfaceFormatsKHR(dev->physical_device, surface, &fmt_count, nullptr);
    std::vector<VkSurfaceFormatKHR> formats(fmt_count);
    vkGetPhysicalDeviceSurfaceFormatsKHR(dev->physical_device, surface, &fmt_count, formats.data());
    VkSurfaceFormatKHR chosen_fmt = choose_surface_format(formats, format);

    VkPresentModeKHR present_mode = choose_present_mode(dev->physical_device, surface, present_mode_str);

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
    sw->vsync = (present_mode == VK_PRESENT_MODE_FIFO_KHR);
    sw->swapchain = VK_NULL_HANDLE;
    sw->fences = nullptr;
    sw->image_available_semaphore = VK_NULL_HANDLE;
    sw->render_finished_semaphore = VK_NULL_HANDLE;

    if (!vk_Swapchain_recreate(sw, width, height)) {
        vkDestroySurfaceKHR(vk_instance, surface, nullptr);
        Py_DECREF(sw);
        return nullptr;
    }

    return reinterpret_cast<PyObject*>(sw);
}

// -----------------------------------------------------------------------------
// Deallocation
// -----------------------------------------------------------------------------
void vk_Swapchain_dealloc(vk_Swapchain* self) {
    if (self->py_device) {
        VkDevice device = self->py_device->device;
        vkDeviceWaitIdle(device);

        if (self->fences) {
            for (uint32_t i = 0; i < self->image_count; ++i)
                vkDestroyFence(device, self->fences[i], nullptr);
            PyMem_Free(self->fences);
        }
        if (self->command_buffers) {
            vkFreeCommandBuffers(device, self->py_device->command_pool,
                                 self->image_count, self->command_buffers);
            PyMem_Free(self->command_buffers);
        }
        if (self->image_available_semaphore)
            vkDestroySemaphore(device, self->image_available_semaphore, nullptr);
        if (self->render_finished_semaphore)
            vkDestroySemaphore(device, self->render_finished_semaphore, nullptr);

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

// -----------------------------------------------------------------------------
// Present (per-image fences + temporary command buffers)
// -----------------------------------------------------------------------------
PyObject* vk_Swapchain_present(vk_Swapchain* self, PyObject* args) {
    PyObject* texture_obj;
    int x = 0, y = 0;
    int wait_for_fence = 1;
    if (!PyArg_ParseTuple(args, "O|iip", &texture_obj, &x, &y, &wait_for_fence))
        return nullptr;

    if (!PyObject_TypeCheck(texture_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "texture must be a Resource");
        return nullptr;
    }
    vk_Resource* texture = reinterpret_cast<vk_Resource*>(texture_obj);
    if (!texture->image) {
        PyErr_SetString(PyExc_TypeError, "texture must be an image");
        return nullptr;
    }

    if (texture->image_extent.width != self->image_extent.width ||
        texture->image_extent.height != self->image_extent.height) {
        PyErr_Format(PyExc_ValueError,
            "Texture dimensions (%ux%u) must match swapchain (%ux%u)",
            texture->image_extent.width, texture->image_extent.height,
            self->image_extent.width, self->image_extent.height);
        return nullptr;
    }

    vk_Device* dev = self->py_device;
    VkResult res;

    // Acquire next image
    uint32_t image_index;
    res = vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                                self->image_available_semaphore, VK_NULL_HANDLE,
                                &image_index);
    if (res == VK_ERROR_OUT_OF_DATE_KHR) {
        self->out_of_date = true;
        Py_RETURN_FALSE;
    } else if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
        PyErr_Format(vk_SwapchainError, "Failed to acquire next image (error %d)", res);
        return nullptr;
    }

    // Wait for the fence associated with THIS image
    vkWaitForFences(dev->device, 1, &self->fences[image_index], VK_TRUE, UINT64_MAX);
    vkResetFences(dev->device, 1, &self->fences[image_index]);

    // Use persistent command buffer for this image
    VkCommandBuffer cmd = self->command_buffers[image_index];
    vkResetCommandBuffer(cmd, 0);   // Reset before recording

    VkCommandBufferBeginInfo begin_info = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    begin_info.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(cmd, &begin_info);

    // Barrier 1: swapchain image -> TRANSFER_DST_OPTIMAL
    VkImageMemoryBarrier barrier = { VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER };
    barrier.srcAccessMask = 0;
    barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.oldLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.image = self->images[image_index];
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.levelCount = 1;
    barrier.subresourceRange.layerCount = 1;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                         0, nullptr, 0, nullptr, 1, &barrier);

    // Memory barrier: compute writes -> transfer reads
    VkMemoryBarrier mem_barrier = { VK_STRUCTURE_TYPE_MEMORY_BARRIER };
    mem_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    mem_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                         1, &mem_barrier, 0, nullptr, 0, nullptr);

    // Barrier 2: source texture -> TRANSFER_SRC_OPTIMAL
    VkImageMemoryBarrier src_barrier = { VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER };
    src_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    src_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    src_barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
    src_barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    src_barrier.image = texture->image;
    src_barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    src_barrier.subresourceRange.levelCount = 1;
    src_barrier.subresourceRange.layerCount = 1;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                         0, nullptr, 0, nullptr, 1, &src_barrier);

    // Copy
    VkImageCopy copy_region = {};
    copy_region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    copy_region.srcSubresource.layerCount = 1;
    copy_region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    copy_region.dstSubresource.layerCount = 1;
    copy_region.srcOffset = {0, 0, 0};
    copy_region.dstOffset = {x, y, 0};
    copy_region.extent = {texture->image_extent.width, texture->image_extent.height, 1};
    vkCmdCopyImage(cmd,
                   texture->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   self->images[image_index], VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   1, &copy_region);

    // Barrier 3: source texture back -> GENERAL
    src_barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
    src_barrier.dstAccessMask = 0;  // No need for explicit access; layout change only
    src_barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    src_barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
    vkCmdPipelineBarrier(cmd,
                         VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         0, 0, nullptr, 0, nullptr, 1, &src_barrier);

    // Barrier 4: swapchain image -> PRESENT_SRC_KHR
    barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
    barrier.dstAccessMask = 0;
    barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
    barrier.newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                         VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0,
                         0, nullptr, 0, nullptr, 1, &barrier);

    vkEndCommandBuffer(cmd);

    // Submit
    VkPipelineStageFlags wait_stage = VK_PIPELINE_STAGE_TRANSFER_BIT;
    VkSubmitInfo submit = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
    submit.waitSemaphoreCount = 1;
    submit.pWaitSemaphores = &self->image_available_semaphore;
    submit.pWaitDstStageMask = &wait_stage;
    submit.commandBufferCount = 1;
    submit.pCommandBuffers = &cmd;
    submit.signalSemaphoreCount = 1;
    submit.pSignalSemaphores = &self->render_finished_semaphore;

    res = vkQueueSubmit(dev->queue, 1, &submit, self->fences[image_index]);
    if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Queue submit failed (error %d)", res);
        return nullptr;
    }

    // Present
    VkPresentInfoKHR present_info = { VK_STRUCTURE_TYPE_PRESENT_INFO_KHR };
    present_info.waitSemaphoreCount = 1;
    present_info.pWaitSemaphores = &self->render_finished_semaphore;
    present_info.swapchainCount = 1;
    present_info.pSwapchains = &self->swapchain;
    present_info.pImageIndices = &image_index;

    res = vkQueuePresentKHR(dev->queue, &present_info);

    if (res == VK_ERROR_OUT_OF_DATE_KHR || res == VK_SUBOPTIMAL_KHR || self->framebuffer_resized) {
        self->out_of_date = true;
        Py_RETURN_FALSE;
    } else if (res != VK_SUCCESS) {
        PyErr_Format(vk_SwapchainError, "Present failed (error %d)", res);
        return nullptr;
    }

    Py_RETURN_TRUE;
}

// -----------------------------------------------------------------------------
// Status Queries
// -----------------------------------------------------------------------------
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
PyObject* vk_Swapchain_recreate_method(vk_Swapchain* self, PyObject* args) {
    int width = 0, height = 0;
    if (!PyArg_ParseTuple(args, "|ii", &width, &height)) return nullptr;
    if (!vk_Swapchain_recreate(self, width, height)) return nullptr;
    Py_RETURN_NONE;
}

// -----------------------------------------------------------------------------
// Type Definition
// -----------------------------------------------------------------------------
static PyMethodDef vk_Swapchain_methods[] = {
    {"present", (PyCFunction)vk_Swapchain_present, METH_VARARGS, "Copy texture and present."},
    {"is_suboptimal", (PyCFunction)vk_Swapchain_is_suboptimal, METH_NOARGS, ""},
    {"is_out_of_date", (PyCFunction)vk_Swapchain_is_out_of_date, METH_NOARGS, ""},
    {"needs_recreation", (PyCFunction)vk_Swapchain_needs_recreation, METH_NOARGS, ""},
    {"recreate", (PyCFunction)vk_Swapchain_recreate_method, METH_VARARGS, ""},
    {nullptr, nullptr, 0, nullptr}
};

static PyMemberDef vk_Swapchain_members[] = {
    {"width", T_UINT, offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, width), 0, ""},
    {"height", T_UINT, offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, height), 0, ""},
    {"image_count", T_UINT, offsetof(vk_Swapchain, image_count), 0, ""},
    {"vsync", T_BOOL, offsetof(vk_Swapchain, vsync), 0, ""},
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