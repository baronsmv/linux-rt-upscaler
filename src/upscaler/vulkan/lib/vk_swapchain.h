#ifndef VK_SWAPCHAIN_H
#define VK_SWAPCHAIN_H

#include "vk_common.h"
#include <vector>

/**
 * Synchronisation and command resources for a single frame in flight.
 * Each frame has its own set to allow overlapping CPU/GPU work.
 */
struct FrameSync {
    VkSemaphore image_available_semaphore;  // Signaled when swapchain image is ready
    VkSemaphore render_finished_semaphore;  // Signaled when rendering/copy finishes
    VkFence in_flight_fence;                // Signaled when frame resources can be reused
    VkCommandBuffer command_buffer;         // Command buffer used for this frame's copy
};

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
    std::vector<FrameSync> frame_sync;

    uint32_t current_frame;      // Index of the frame we will use next
    uint32_t image_index;        // Index of the acquired swapchain image

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

PyObject *vk_Swapchain_acquire_next_image(vk_Swapchain *self, PyObject *args);
PyObject *vk_Swapchain_present(vk_Swapchain *self, PyObject *args);
PyObject *vk_Swapchain_get_current_image(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_get_image_view(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_is_suboptimal(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_is_out_of_date(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_needs_recreation(vk_Swapchain *self, PyObject *ignored);
PyObject *vk_Swapchain_recreate_method(vk_Swapchain *self, PyObject *args);

#endif /* VK_SWAPCHAIN_H */