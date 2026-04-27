/**
 * @file vk_swapchain.cpp
 * @brief Vulkan swapchain creation and presentation management.
 *
 * This module provides a Python-callable swapchain wrapper built on top of
 * Vulkan 1.2+ and the XCB window system integration. It manages:
 *   - Creation of a VkSurfaceKHR from an X11 window (XCB).
 *   - Swapchain image acquisition, copying a compute-generated texture to the
 *     swapchain, and presenting it to the display.
 *   - Per-image synchronisation fences and shared semaphores for queue
 * operations.
 *   - Robust recreation of the swapchain when the surface is out of date or
 * resized.
 *
 * Synchronisation design
 * ----------------------
 * The swapchain uses a **triple-buffered** (configurable) set of images,
 * each with its own fence and a dedicated command buffer. Two shared
 * semaphores
 * (`image_available`, `render_finished`) coordinate the queue submissions.
 *
 * The `present()` method is **non-blocking** by design: it submits the copy
 * command buffer to the graphics/compute queue and returns immediately.
 * Full-frame completion is signalled by a per-image fence that becomes
 * available **after** the presentation engine has finished reading the image.
 * This fence is exposed via `get_last_fence()` so the application can wait on
 * it **before** modifying any GPU resources (e.g., staging buffers or textures)
 * that are reused across frames. Waiting on this fence replaces the need for
 * a full `vkDeviceWaitIdle()` and provides precise per-frame synchronisation
 * without unnecessary stalls.
 *
 * Lifecycle
 * ---------
 *   1. `Device.create_swapchain()` creates the surface, selects formats
 *      and present mode, then calls `vk_Swapchain_recreate()` for the
 *      actual swapchain.
 *   2. `present()` is called once per frame. It acquires the next image,
 *      records a copy from a source texture into that swapchain image,
 *      submits the work, and presents.
 *   3. If the surface is out-of-date (`VK_ERROR_OUT_OF_DATE_KHR` or
 *      `VK_SUBOPTIMAL_KHR`), the `out_of_date` flag is set and `present()`
 *      returns `False`. The application then calls `recreate()` (after
 *      draining the queue) to obtain a new swapchain.
 *   4. `vk_Swapchain_dealloc` destroys all Vulkan objects when the Python
 *      object is garbage collected.
 */

// clang-format off
#include "vk_device.h"
#include "vk_instance.h"
#include "vk_swapchain.h"
#include "vk_utils.h"
#include <algorithm>
#include <cstring>
#include <xcb/xcb.h>              // Must come before vulkan_xcb.h
#include <vulkan/vulkan_xcb.h>
// clang-format on

extern PyObject *vk_SwapchainError;

// =============================================================================
// Static helper functions (file-local)
// =============================================================================

/**
 * Creates an XCB surface for a given instance, display and window.
 *
 * @param instance      Vulkan instance.
 * @param display_ptr   Pointer to an xcb_connection_t.
 * @param window_ptr    Pointer to an xcb_window_t (cast to void* for storage).
 * @param out_surface   On success, receives the created VkSurfaceKHR.
 * @return VK_SUCCESS on success, or a negative error code.
 */
static VkResult create_xcb_surface(VkInstance instance, void *display_ptr,
                                   void *window_ptr,
                                   VkSurfaceKHR *out_surface) {
  VkXcbSurfaceCreateInfoKHR surface_info = {
      VK_STRUCTURE_TYPE_XCB_SURFACE_CREATE_INFO_KHR};
  surface_info.connection = static_cast<xcb_connection_t *>(display_ptr);
  surface_info.window =
      static_cast<xcb_window_t>(reinterpret_cast<uintptr_t>(window_ptr));

  PFN_vkCreateXcbSurfaceKHR func =
      (PFN_vkCreateXcbSurfaceKHR)vkGetInstanceProcAddr(instance,
                                                       "vkCreateXcbSurfaceKHR");
  if (!func)
    return VK_ERROR_EXTENSION_NOT_PRESENT;
  return func(instance, &surface_info, nullptr, out_surface);
}

/**
 * Chooses a suitable number of swapchain images, respecting the surface's
 * supported minimum and maximum counts.
 *
 * @param caps    Surface capabilities.
 * @param desired Preferred image count (e.g., 3).
 * @return The clamped number of images to request.
 */
static uint32_t choose_image_count(const VkSurfaceCapabilitiesKHR &caps,
                                   uint32_t desired) {
  uint32_t count = desired;
  if (caps.maxImageCount > 0 && count > caps.maxImageCount)
    count = caps.maxImageCount;
  if (count < caps.minImageCount)
    count = caps.minImageCount;
  return count;
}

/**
 * Selects the VkPresentModeKHR matching a human-readable string.
 * Falls back to VK_PRESENT_MODE_FIFO_KHR if the desired mode is unavailable.
 *
 * @param phys      Physical device handle.
 * @param surface   Surface to query.
 * @param mode_str  "fifo", "mailbox", "immediate", or nullptr (fifo assumed).
 * @return The selected present mode.
 */
static VkPresentModeKHR choose_present_mode(VkPhysicalDevice phys,
                                            VkSurfaceKHR surface,
                                            const char *mode_str) {
  uint32_t count;
  vkGetPhysicalDeviceSurfacePresentModesKHR(phys, surface, &count, nullptr);
  std::vector<VkPresentModeKHR> modes(count);
  vkGetPhysicalDeviceSurfacePresentModesKHR(phys, surface, &count,
                                            modes.data());

  VkPresentModeKHR desired = VK_PRESENT_MODE_FIFO_KHR; // default
  if (mode_str) {
    if (strcmp(mode_str, "immediate") == 0)
      desired = VK_PRESENT_MODE_IMMEDIATE_KHR;
    else if (strcmp(mode_str, "mailbox") == 0)
      desired = VK_PRESENT_MODE_MAILBOX_KHR;
  }

  for (auto m : modes)
    if (m == desired)
      return desired;
  return VK_PRESENT_MODE_FIFO_KHR; // mandatory fallback
}

/**
 * Selects a VkSurfaceFormatKHR. Prefers sRGB if available, or a format
 * explicitly requested by the `requested_format` numeric constant (see
 * `vk_format_map`).
 *
 * @param formats           List of supported surface formats.
 * @param requested_format  A pixel format constant (e.g., B8G8R8A8_UNORM).
 * @return The selected format.
 */
static VkSurfaceFormatKHR
choose_surface_format(const std::vector<VkSurfaceFormatKHR> &formats,
                      int requested_format) {
  // If the caller asked for a specific format, try to find it.
  if (requested_format > 0) {
    auto it = vk_format_map.find(requested_format);
    if (it != vk_format_map.end()) {
      VkFormat target = it->second.first;
      for (const auto &fmt : formats)
        if (fmt.format == target &&
            fmt.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
          return fmt;
    }
  }
  // Prefer BGRA sRGB.
  for (const auto &fmt : formats)
    if (fmt.format == VK_FORMAT_B8G8R8A8_SRGB &&
        fmt.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR)
      return fmt;
  // Fall back to the first available format.
  return formats[0];
}

/**
 * Creates an array of VkImageViews, one for each swapchain image.
 *
 * @param device     Logical device.
 * @param format     Image format.
 * @param images     Vector of swapchain images.
 * @param out_views  Output vector to receive the views.
 * @return true on success, false with Python exception set.
 */
static bool create_image_views(VkDevice device, VkFormat format,
                               const std::vector<VkImage> &images,
                               std::vector<VkImageView> &out_views) {
  out_views.resize(images.size());
  VkImageViewCreateInfo view_info = {VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
  view_info.viewType = VK_IMAGE_VIEW_TYPE_2D;
  view_info.format = format;
  view_info.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  view_info.subresourceRange.levelCount = 1;
  view_info.subresourceRange.layerCount = 1;

  for (size_t i = 0; i < images.size(); ++i) {
    view_info.image = images[i];
    if (vkCreateImageView(device, &view_info, nullptr, &out_views[i]) !=
        VK_SUCCESS) {
      // Clean up already created views.
      for (size_t j = 0; j < i; ++j)
        vkDestroyImageView(device, out_views[j], nullptr);
      return false;
    }
  }
  return true;
}

// =============================================================================
// Internal lifecycle management
// =============================================================================

/**
 * (Re)allocates all per-image resources (fences, command buffers) and the
 * swapchain itself. The caller **must** ensure that the device queue is idle
 * (vkDeviceWaitIdle) before calling this function if the swapchain is being
 * recreated - otherwise in-flight submissions may touch destroyed objects.
 *
 * Resets the `last_present_fence` to VK_NULL_HANDLE, because after recreation
 * any previously stored fence becomes invalid.
 *
 * @param self   Swapchain wrapper object.
 * @param width  Desired width (0 = use surface capabilities).
 * @param height Desired height (0 = use surface capabilities).
 * @return true on success, false with Python exception set.
 */
bool vk_Swapchain_recreate(vk_Swapchain *self, uint32_t width,
                           uint32_t height) {
  vk_Device *dev = self->py_device;
  VkDevice device = dev->device;
  VkPhysicalDevice phys = dev->physical_device;

  // ---------------------------------------------------------------
  // 1. Query surface capabilities and determine image extent
  // ---------------------------------------------------------------
  VkSurfaceCapabilitiesKHR caps;
  vkGetPhysicalDeviceSurfaceCapabilitiesKHR(phys, self->surface, &caps);

  if (width == 0 || height == 0) {
    if (caps.currentExtent.width != UINT32_MAX) {
      self->image_extent = caps.currentExtent;
    } else {
      self->image_extent.width =
          std::clamp(width ? width : 800, caps.minImageExtent.width,
                     caps.maxImageExtent.width);
      self->image_extent.height =
          std::clamp(height ? height : 600, caps.minImageExtent.height,
                     caps.maxImageExtent.height);
    }
  } else {
    self->image_extent.width = width;
    self->image_extent.height = height;
  }

  // ---------------------------------------------------------------
  // 2. Wait for device idle, then tear down old resources
  // ---------------------------------------------------------------
  vkDeviceWaitIdle(device);

  // Per-image fences
  if (self->fences) {
    for (uint32_t i = 0; i < self->image_count; ++i)
      vkDestroyFence(device, self->fences[i], nullptr);
    PyMem_Free(self->fences);
    self->fences = nullptr;
  }
  // Persistent command buffers
  if (self->command_buffers) {
    vkFreeCommandBuffers(device, self->py_device->command_pool,
                         self->image_count, self->command_buffers);
    PyMem_Free(self->command_buffers);
    self->command_buffers = nullptr;
  }
  // Semaphores
  if (self->image_available_semaphore) {
    vkDestroySemaphore(device, self->image_available_semaphore, nullptr);
    self->image_available_semaphore = VK_NULL_HANDLE;
  }
  if (self->render_finished_semaphore) {
    vkDestroySemaphore(device, self->render_finished_semaphore, nullptr);
    self->render_finished_semaphore = VK_NULL_HANDLE;
  }
  // Image views
  for (auto view : self->image_views)
    vkDestroyImageView(device, view, nullptr);
  self->image_views.clear();

  // ---------------------------------------------------------------
  // 3. Create new swapchain
  // ---------------------------------------------------------------
  VkCompositeAlphaFlagBitsKHR compositeAlpha =
      VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
  if (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR)
    compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
  else if (caps.supportedCompositeAlpha &
           VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR)
    compositeAlpha = VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR;
  else if (caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR)
    compositeAlpha = VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR;

  VkSwapchainCreateInfoKHR swap_info = {
      VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR};
  swap_info.surface = self->surface;
  swap_info.minImageCount = choose_image_count(caps, self->desired_image_count);
  swap_info.imageFormat = self->format;
  swap_info.imageColorSpace = self->color_space;
  swap_info.imageExtent = self->image_extent;
  swap_info.imageArrayLayers = 1;
  swap_info.imageUsage =
      VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
  swap_info.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
  swap_info.preTransform = caps.currentTransform;
  swap_info.compositeAlpha = compositeAlpha;
  swap_info.presentMode = self->present_mode;
  swap_info.clipped = VK_TRUE;
  swap_info.oldSwapchain = self->swapchain; // facilitates reuse of old images

  VkResult res =
      vkCreateSwapchainKHR(device, &swap_info, nullptr, &self->swapchain);
  if (res != VK_SUCCESS) {
    PyErr_Format(vk_SwapchainError, "Failed to create swapchain (error %d)",
                 res);
    return false;
  }
  // Destroy the old swapchain now that the new one is alive.
  if (swap_info.oldSwapchain != VK_NULL_HANDLE)
    vkDestroySwapchainKHR(device, swap_info.oldSwapchain, nullptr);

  // ---------------------------------------------------------------
  // 4. Retrieve the new images and create views
  // ---------------------------------------------------------------
  uint32_t count;
  vkGetSwapchainImagesKHR(device, self->swapchain, &count, nullptr);
  self->images.resize(count);
  vkGetSwapchainImagesKHR(device, self->swapchain, &count, self->images.data());
  self->image_count = count;

  if (!create_image_views(device, self->format, self->images,
                          self->image_views)) {
    PyErr_SetString(vk_SwapchainError,
                    "Failed to create swapchain image views");
    return false;
  }

  // ---------------------------------------------------------------
  // 5. Create synchronisation primitives
  // ---------------------------------------------------------------
  VkSemaphoreCreateInfo sem_info = {VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO};
  if (vkCreateSemaphore(device, &sem_info, nullptr,
                        &self->image_available_semaphore) != VK_SUCCESS ||
      vkCreateSemaphore(device, &sem_info, nullptr,
                        &self->render_finished_semaphore) != VK_SUCCESS) {
    PyErr_SetString(vk_SwapchainError, "Failed to create semaphores");
    return false;
  }

  // Per-image fences, initially signalled so the first acquire does not wait.
  self->fences = (VkFence *)PyMem_Malloc(sizeof(VkFence) * self->image_count);
  if (!self->fences) {
    PyErr_NoMemory();
    return false;
  }
  VkFenceCreateInfo fence_info = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
  fence_info.flags = VK_FENCE_CREATE_SIGNALED_BIT;
  for (uint32_t i = 0; i < self->image_count; ++i) {
    if (vkCreateFence(device, &fence_info, nullptr, &self->fences[i]) !=
        VK_SUCCESS) {
      for (uint32_t j = 0; j < i; ++j)
        vkDestroyFence(device, self->fences[j], nullptr);
      PyMem_Free(self->fences);
      self->fences = nullptr;
      PyErr_SetString(vk_SwapchainError, "Failed to create fences");
      return false;
    }
  }

  // Per-image command buffers (persistent, avoids per-frame allocation jitter).
  self->command_buffers = (VkCommandBuffer *)PyMem_Malloc(
      sizeof(VkCommandBuffer) * self->image_count);
  if (!self->command_buffers) {
    PyErr_NoMemory();
    return false;
  }
  VkCommandBufferAllocateInfo alloc_info = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
  alloc_info.commandPool = dev->command_pool;
  alloc_info.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
  alloc_info.commandBufferCount = self->image_count;
  if (vkAllocateCommandBuffers(device, &alloc_info, self->command_buffers) !=
      VK_SUCCESS) {
    for (uint32_t j = 0; j < self->image_count; ++j)
      vkDestroyFence(device, self->fences[j], nullptr);
    PyMem_Free(self->fences);
    PyMem_Free(self->command_buffers);
    self->fences = nullptr;
    self->command_buffers = nullptr;
    PyErr_SetString(vk_SwapchainError, "Failed to allocate command buffers");
    return false;
  }

  // Clear stale state flags; the new swapchain is pristine.
  self->suboptimal = false;
  self->out_of_date = false;
  self->framebuffer_resized = false;

  // Any previously held fence handle is now invalid.
  self->last_present_fence = VK_NULL_HANDLE;

  return true;
}

// =============================================================================
// Python-facing method implementations
// =============================================================================

/**
 * Creates a swapchain from a Python tuple representing the native window
 * handle. This is the workhorse called by `Device.create_swapchain`.
 *
 * Args (Python):
 *   window_tuple: (display_ptr: int, window_ptr: int) for XCB.
 *   format:       pixel format constant (e.g., B8G8R8A8_UNORM).
 *   num_buffers:  desired number of swapchain images (default 3).
 *   width:        desired width (0 = derive from surface).
 *   height:       desired height (0 = derive from surface).
 *   present_mode: "fifo" (default), "mailbox", or "immediate".
 *
 * Returns:
 *   A new `vk.Swapchain` object, or NULL with a Python exception.
 */
PyObject *vk_Device_create_swapchain_impl(vk_Device *self, PyObject *args) {
  PyObject *window_tuple;
  int format;
  int num_buffers = 3;
  int width = 0, height = 0;
  const char *present_mode_str = nullptr;

  if (!PyArg_ParseTuple(args, "O!i|iIIs", &PyTuple_Type, &window_tuple, &format,
                        &num_buffers, &width, &height, &present_mode_str))
    return nullptr;

  if (!vk_instance_ensure())
    return nullptr;
  vk_Device *dev = vk_Device_get_initialized(self);
  if (!dev)
    return nullptr;

  // Validate the window tuple: must contain exactly two integer-like objects.
  if (PyTuple_Size(window_tuple) != 2) {
    PyErr_SetString(PyExc_ValueError,
                    "window_handle must be (display_ptr, window_ptr)");
    return nullptr;
  }
  void *display_ptr = PyLong_AsVoidPtr(PyTuple_GetItem(window_tuple, 0));
  void *window_ptr = PyLong_AsVoidPtr(PyTuple_GetItem(window_tuple, 1));
  if (PyErr_Occurred())
    return nullptr;

  // Create the XCB surface.
  VkSurfaceKHR surface;
  VkResult res =
      create_xcb_surface(vk_instance, display_ptr, window_ptr, &surface);
  if (res != VK_SUCCESS) {
    PyErr_Format(vk_SwapchainError, "Failed to create XCB surface (error %d)",
                 res);
    return nullptr;
  }

  // Verify that the queue family supports presentation.
  VkBool32 supports_present;
  vkGetPhysicalDeviceSurfaceSupportKHR(dev->physical_device,
                                       dev->queue_family_index, surface,
                                       &supports_present);
  if (!supports_present) {
    vkDestroySurfaceKHR(vk_instance, surface, nullptr);
    PyErr_SetString(vk_SwapchainError,
                    "Queue family does not support presentation");
    return nullptr;
  }

  // Select surface format and present mode.
  uint32_t fmt_count;
  vkGetPhysicalDeviceSurfaceFormatsKHR(dev->physical_device, surface,
                                       &fmt_count, nullptr);
  std::vector<VkSurfaceFormatKHR> formats(fmt_count);
  vkGetPhysicalDeviceSurfaceFormatsKHR(dev->physical_device, surface,
                                       &fmt_count, formats.data());
  VkSurfaceFormatKHR chosen_fmt = choose_surface_format(formats, format);

  VkPresentModeKHR present_mode =
      choose_present_mode(dev->physical_device, surface, present_mode_str);

  // Allocate the Python wrapper object.
  vk_Swapchain *sw = PyObject_New(vk_Swapchain, &vk_Swapchain_Type);
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
  // The following are set by vk_Swapchain_recreate.
  sw->swapchain = VK_NULL_HANDLE;
  sw->fences = nullptr;
  sw->command_buffers = nullptr;
  sw->image_available_semaphore = VK_NULL_HANDLE;
  sw->render_finished_semaphore = VK_NULL_HANDLE;
  sw->last_present_fence = VK_NULL_HANDLE;

  if (!vk_Swapchain_recreate(sw, width, height)) {
    vkDestroySurfaceKHR(vk_instance, surface, nullptr);
    Py_DECREF(sw);
    return nullptr;
  }

  return reinterpret_cast<PyObject *>(sw);
}

/**
 * Destroys all Vulkan resources held by a swapchain object.
 * The queue is first idled to guarantee that no submissions are in flight.
 */
void vk_Swapchain_dealloc(vk_Swapchain *self) {
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
  Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

/**
 * Presents a texture to the window.
 *
 *  1. Acquires the next available swapchain image (blocking indefinitely if
 *     necessary).
 *  2. Waits on the per-image fence (from the previous use of that image) and
 *     resets it for the new submission.
 *  3. Records a command buffer that:
 *       - Transitions the swapchain image to TRANSFER_DST_OPTIMAL.
 *       - Inserts a memory barrier for compute writes -> transfer reads.
 *       - Transitions the source texture to TRANSFER_SRC_OPTIMAL.
 *       - Copies the source texture into the swapchain image.
 *       - Transitions the source texture back to GENERAL and the swapchain
 *         image to PRESENT_SRC_KHR.
 *  4. Submits the command buffer to the queue, signalling the per-image fence
 *     and the `render_finished` semaphore.
 *  5. Presents the image.
 *
 * The `wait_for_fence` parameter (from the Python caller) is ignored; the
 * caller is expected to use `get_last_fence()` for frame-level synchronisation.
 *
 * @param self        Swapchain object.
 * @param args        Python arguments: (texture, x, y, wait_for_fence)
 * @return Py_True if the image was successfully presented,
 *         Py_False if the swapchain is out of date,
 *         NULL on error (with exception set).
 */
PyObject *vk_Swapchain_present(vk_Swapchain *self, PyObject *args) {
  PyObject *texture_obj;
  int x = 0, y = 0;
  int wait_for_fence = 1; // ignored - see comment above
  if (!PyArg_ParseTuple(args, "O|iip", &texture_obj, &x, &y, &wait_for_fence))
    return nullptr;

  // Type checks
  if (!PyObject_TypeCheck(texture_obj, &vk_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "texture must be a Resource");
    return nullptr;
  }
  vk_Resource *texture = reinterpret_cast<vk_Resource *>(texture_obj);
  if (!texture->image) {
    PyErr_SetString(PyExc_TypeError, "texture must be an image");
    return nullptr;
  }

/**
 * ______________________________________________________________________________
 *
 *  WHY WE DO NOT ENFORCE EQUAL TEXTURE-SWAPCHAIN DIMENSIONS
 *
 *  On XWayland the compositor may create the Vulkan surface at a physical size
 *  that is larger than the logical window size. For example, a 3840x2160
 *  overlay on a 200% HiDPI display results in a 7680x4320 swapchain.
 *
 *  Our rendering pipeline works at the logical resolution:
 *
 *     - The Lanczos shader writes into a screen texture of 3840x2160 pixels.
 *     - The swapchain is 7680x4320 pixels but we present only the logical
 *       region (the top-left 3840x2160) by copying a smaller texture.
 *
 *  After presentation the compositor down-samples the entire swapchain buffer
 *  back onto the logical overlay window. This gives us:
 *
 *     - Correct on-screen position - the overlay stays at (0,0) at logical
 *       size rather than expanding to the full physical surface.
 *     - Performance - Lanczos runs at 4K instead of 8K.
 *     - Robustness - the compositor handles any scale factor automatically.
 *
 *  The old behaviour (before this check was introduced) already worked this
 *  way and is well-tested.
 *
 *  If we kept the equal-size check we would be forced to render the
 *  screen texture at the physical swapchain resolution (e.g. 7680x4320),
 *  which would both waste GPU resources and cause the overlay to cover
 *  more area than intended (displacing it).
 *
 *  Therefore the check is intentionally removed.
 * ______________________________________________________________________________
 *
 *  Removed check:
 *
 * if (texture->image_extent.width != self->image_extent.width ||
 *     texture->image_extent.height != self->image_extent.height) {
 *   PyErr_Format(PyExc_ValueError,
 *                "Texture dimensions (%ux%u) must match swapchain (%ux%u)",
 *                texture->image_extent.width, texture->image_extent.height,
 *                self->image_extent.width, self->image_extent.height);
 *   return nullptr;
 * }
 * ______________________________________________________________________________
 */

  vk_Device *dev = self->py_device;
  VkResult res;

  // --- Acquire next image index ---
  uint32_t image_index;
  res = vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                              self->image_available_semaphore, VK_NULL_HANDLE,
                              &image_index);
  if (res == VK_ERROR_OUT_OF_DATE_KHR) {
    self->out_of_date = true;
    Py_RETURN_FALSE;
  } else if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
    PyErr_Format(vk_SwapchainError, "Failed to acquire next image (error %d)",
                 res);
    return nullptr;
  }

  // --- Wait for and reset the per-image fence ---
  vkWaitForFences(dev->device, 1, &self->fences[image_index], VK_TRUE,
                  UINT64_MAX);
  vkResetFences(dev->device, 1, &self->fences[image_index]);

  // --- Record the command buffer ---
  VkCommandBuffer cmd = self->command_buffers[image_index];
  vkResetCommandBuffer(cmd, 0);

  VkCommandBufferBeginInfo begin_info = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  begin_info.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
  vkBeginCommandBuffer(cmd, &begin_info);

  // Barrier 1: swapchain image undefined -> TRANSFER_DST_OPTIMAL
  VkImageMemoryBarrier dst_barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  dst_barrier.srcAccessMask = 0;
  dst_barrier.dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  dst_barrier.oldLayout = VK_IMAGE_LAYOUT_UNDEFINED;
  dst_barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  dst_barrier.image = self->images[image_index];
  dst_barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  dst_barrier.subresourceRange.levelCount = 1;
  dst_barrier.subresourceRange.layerCount = 1;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, nullptr, 0,
                       nullptr, 1, &dst_barrier);

  // Memory barrier: ensure compute writes are visible to the transfer.
  VkMemoryBarrier mem_barrier = {VK_STRUCTURE_TYPE_MEMORY_BARRIER};
  mem_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  mem_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 1, &mem_barrier, 0,
                       nullptr, 0, nullptr);

  // Barrier 2: source texture GENERAL -> TRANSFER_SRC_OPTIMAL
  VkImageMemoryBarrier src_barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  src_barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  src_barrier.dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  src_barrier.oldLayout = VK_IMAGE_LAYOUT_GENERAL;
  src_barrier.newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  src_barrier.image = texture->image;
  src_barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  src_barrier.subresourceRange.levelCount = 1;
  src_barrier.subresourceRange.layerCount = 1;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, nullptr, 0,
                       nullptr, 1, &src_barrier);

  // Copy the entire texture into the swapchain image.
  VkImageCopy copy_region = {};
  copy_region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  copy_region.srcSubresource.layerCount = 1;
  copy_region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  copy_region.dstSubresource.layerCount = 1;
  copy_region.srcOffset = {0, 0, 0};
  copy_region.dstOffset = {x, y, 0};
  copy_region.extent = {texture->image_extent.width,
                        texture->image_extent.height, 1};
  vkCmdCopyImage(cmd, texture->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                 self->images[image_index],
                 VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &copy_region);

  // Barrier 3: source texture back to GENERAL.
  src_barrier.srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  src_barrier.dstAccessMask = 0; // layout transition only
  src_barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  src_barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, nullptr, 0,
                       nullptr, 1, &src_barrier);

  // Barrier 4: swapchain image TRANSFER_DST_OPTIMAL -> PRESENT_SRC_KHR
  dst_barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  dst_barrier.dstAccessMask = 0;
  dst_barrier.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  dst_barrier.newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0, 0, nullptr, 0,
                       nullptr, 1, &dst_barrier);

  if (vkEndCommandBuffer(cmd) != VK_SUCCESS) {
    PyErr_SetString(vk_SwapchainError, "Failed to end command buffer");
    return nullptr;
  }

  // --- Submit to queue ---
  VkPipelineStageFlags wait_stage = VK_PIPELINE_STAGE_TRANSFER_BIT;
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
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

  // The fence will signal when the presentation engine has finished reading
  // the image. The application may wait on this fence to know when all
  // frame-related GPU work is complete.
  self->last_present_fence = self->fences[image_index];

  // --- Present ---
  VkPresentInfoKHR present_info = {VK_STRUCTURE_TYPE_PRESENT_INFO_KHR};
  present_info.waitSemaphoreCount = 1;
  present_info.pWaitSemaphores = &self->render_finished_semaphore;
  present_info.swapchainCount = 1;
  present_info.pSwapchains = &self->swapchain;
  present_info.pImageIndices = &image_index;

  res = vkQueuePresentKHR(dev->queue, &present_info);
  if (res == VK_ERROR_OUT_OF_DATE_KHR || res == VK_SUBOPTIMAL_KHR ||
      self->framebuffer_resized) {
    self->out_of_date = true;
    Py_RETURN_FALSE;
  } else if (res != VK_SUCCESS) {
    PyErr_Format(vk_SwapchainError, "Present failed (error %d)", res);
    return nullptr;
  }

  Py_RETURN_TRUE;
}

// -----------------------------------------------------------------------------
// Frame-level synchronisation helper
// -----------------------------------------------------------------------------

/**
 * Returns the native VkFence handle of the fence that was signalled by the
 * most recent `present()` call. This fence can be waited on to ensure that
 * **all** GPU work for the corresponding frame has completed, including the
 * presentation engine's read of the swapchain image.
 *
 * The returned handle is an integer (the raw pointer) and may be passed to
 * `Device.wait_for_fences()`. On the first frame (or immediately after
 * recreation), `None` is returned because no present has yet occurred.
 *
 * @return A Python int (fence handle) or None.
 */
PyObject *vk_Swapchain_get_last_fence(vk_Swapchain *self, PyObject *ignored) {
  if (self->last_present_fence == VK_NULL_HANDLE) {
    Py_RETURN_NONE;
  }
  return PyLong_FromVoidPtr((void *)self->last_present_fence);
}

// -----------------------------------------------------------------------------
// Status query methods
// -----------------------------------------------------------------------------

PyObject *vk_Swapchain_is_suboptimal(vk_Swapchain *self, PyObject *ignored) {
  return PyBool_FromLong(self->suboptimal);
}

PyObject *vk_Swapchain_is_out_of_date(vk_Swapchain *self, PyObject *ignored) {
  return PyBool_FromLong(self->out_of_date);
}

PyObject *vk_Swapchain_needs_recreation(vk_Swapchain *self, PyObject *ignored) {
  return PyBool_FromLong(self->out_of_date || self->suboptimal);
}

/**
 * Public recreation entry point, callable from Python.
 * Passes width/height (0 = keep current) to vk_Swapchain_recreate().
 */
PyObject *vk_Swapchain_recreate_method(vk_Swapchain *self, PyObject *args) {
  int width = 0, height = 0;
  if (!PyArg_ParseTuple(args, "|ii", &width, &height))
    return nullptr;
  if (!vk_Swapchain_recreate(self, width, height))
    return nullptr;
  Py_RETURN_NONE;
}

// -----------------------------------------------------------------------------
// Python type definition
// -----------------------------------------------------------------------------

static PyMethodDef vk_Swapchain_methods[] = {
    {"present", (PyCFunction)vk_Swapchain_present, METH_VARARGS,
     "Copy a texture to the swapchain and present it to the screen.\n\n"
     "Args:\n"
     "  texture (vk.Resource): The image to display.\n"
     "  x (int, optional): Destination x offset.\n"
     "  y (int, optional): Destination y offset.\n"
     "  wait_for_fence (bool, optional): ignored (sync via get_last_fence).\n"
     "Returns True on success, False if the swapchain is out of date,\n"
     "or raises an exception on error."},

    {"get_last_fence", (PyCFunction)vk_Swapchain_get_last_fence, METH_NOARGS,
     "Return the native handle of the fence from the last present(), or "
     "None.\n\n"
     "This fence can be waited on to know when the frame's GPU work is "
     "complete."},

    {"is_suboptimal", (PyCFunction)vk_Swapchain_is_suboptimal, METH_NOARGS,
     "Return True if the present was suboptimal."},

    {"is_out_of_date", (PyCFunction)vk_Swapchain_is_out_of_date, METH_NOARGS,
     "Return True if the swapchain is out of date and needs recreation."},

    {"needs_recreation", (PyCFunction)vk_Swapchain_needs_recreation,
     METH_NOARGS, "True if out_of_date or suboptimal."},

    {"recreate", (PyCFunction)vk_Swapchain_recreate_method, METH_VARARGS,
     "Recreate the swapchain (must be called after an out-of-date event).\n"
     "Args: (width=0, height=0). 0 = keep current extent."},

    {nullptr, nullptr, 0, nullptr}};

static PyMemberDef vk_Swapchain_members[] = {
    {"width", T_UINT,
     offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, width), 0,
     "Swapchain image width in pixels."},
    {"height", T_UINT,
     offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, height), 0,
     "Swapchain image height in pixels."},
    {"image_count", T_UINT, offsetof(vk_Swapchain, image_count), 0,
     "Number of swapchain images."},
    {"vsync", T_BOOL, offsetof(vk_Swapchain, vsync), 0,
     "True if presenting with VSync (fifo mode)."},
    {nullptr}};

PyTypeObject vk_Swapchain_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0).tp_name = "vulkan.Swapchain",
    .tp_basicsize = sizeof(vk_Swapchain),
    .tp_dealloc = (destructor)vk_Swapchain_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = vk_Swapchain_methods,
    .tp_members = vk_Swapchain_members,
};