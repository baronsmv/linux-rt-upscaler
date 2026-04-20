#ifndef VK_SWAPCHAIN_H
#define VK_SWAPCHAIN_H

#include "vk_common.h"
#include <vector>

struct vk_Swapchain {
    PyObject_HEAD;
    vk_Device* py_device;
    VkSwapchainKHR swapchain;
    VkSurfaceKHR surface;
    VkExtent2D image_extent;
    VkFormat format;
    VkColorSpaceKHR color_space;

    uint32_t image_count;
    std::vector<VkImage> images;
    std::vector<VkImageView> image_views;

    // Synchronisation: per-image fences, shared semaphores
    VkFence* fences;                         // One fence per swapchain image
    VkSemaphore image_available_semaphore;   // Shared
    VkSemaphore render_finished_semaphore;   // Shared
    VkCommandBuffer* command_buffers;        // One command buffer per image

    bool suboptimal;
    bool out_of_date;
    bool framebuffer_resized;

    uint32_t desired_image_count;
    VkPresentModeKHR present_mode;
    bool vsync;
};

extern PyTypeObject vk_Swapchain_Type;

void vk_Swapchain_dealloc(vk_Swapchain *self);
bool vk_Swapchain_recreate(vk_Swapchain *self, uint32_t width = 0, uint32_t height = 0);

PyObject *vk_Device_create_swapchain_impl(vk_Device *self, PyObject *args);
PyObject *vk_Swapchain_present(vk_Swapchain *self, PyObject *args);

// Status queries
PyObject *vk_Swapchain_is_suboptimal(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_is_out_of_date(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_needs_recreation(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_recreate_method(vk_Swapchain *self, PyObject *args);

#endif