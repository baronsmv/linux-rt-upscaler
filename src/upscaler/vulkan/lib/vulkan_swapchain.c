/**
 * @file vulkan_swapchain.c
 * @brief Vulkan swapchain implementation for presentation.
 *
 * This module provides the Swapchain Python type with methods to present
 * textures to a window surface, and query swapchain health.
 */

#include "vulkan_swapchain.h"
#include "vulkan_device.h"
#include "vulkan_resource.h"
#include "vulkan_utils.h"
#include <X11/Xlib.h>
#include <stdlib.h>
#include <string.h>
#include <vulkan/vulkan_xlib.h>

/* -------------------------------------------------------------------------
   External references
   ------------------------------------------------------------------------- */
extern VkInstance g_vulkan_instance; /* from vulkan_module.c */

/* -------------------------------------------------------------------------
   Forward declarations
   ------------------------------------------------------------------------- */
static VkResult create_surface(VkComp_Swapchain *sc, PyObject *window_handle);
static VkResult create_swapchain(VkComp_Swapchain *sc, uint32_t width,
                                 uint32_t height, VkFormat format,
                                 uint32_t num_buffers,
                                 VkPresentModeKHR present_mode);
static void destroy_swapchain(VkComp_Swapchain *sc);

/* -------------------------------------------------------------------------
   Python type definition
   ------------------------------------------------------------------------- */
static PyMemberDef VkComp_Swapchain_members[] = {
    {"width", T_UINT, offsetof(VkComp_Swapchain, image_extent.width), 0,
     "Swapchain width"},
    {"height", T_UINT, offsetof(VkComp_Swapchain, image_extent.height), 0,
     "Swapchain height"},
    {NULL}};

static PyMethodDef VkComp_Swapchain_methods[] = {
    {"present", (PyCFunction)VkComp_Swapchain_Present, METH_VARARGS,
     "Present a texture to the swapchain."},
    {"is_suboptimal", (PyCFunction)VkComp_Swapchain_IsSuboptimal, METH_NOARGS,
     "Return True if the swapchain is suboptimal."},
    {"is_out_of_date", (PyCFunction)VkComp_Swapchain_IsOutOfDate, METH_NOARGS,
     "Return True if the swapchain is out of date."},
    {"needs_recreation", (PyCFunction)VkComp_Swapchain_NeedsRecreation,
     METH_NOARGS, "Return True if the swapchain needs to be recreated."},
    {NULL, NULL, 0, NULL}};

PyTypeObject VkComp_Swapchain_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Swapchain",
    .tp_basicsize = sizeof(VkComp_Swapchain),
    .tp_dealloc = (destructor)VkComp_Swapchain_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = VkComp_Swapchain_methods,
    .tp_members = VkComp_Swapchain_members,
};

/* -------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
void VkComp_Swapchain_Dealloc(VkComp_Swapchain *self) {
  if (self->device && self->device->device) {
    VkDevice dev = self->device->device;
    if (self->copy_semaphore)
      vkDestroySemaphore(dev, self->copy_semaphore, NULL);
    if (self->present_semaphore)
      vkDestroySemaphore(dev, self->present_semaphore, NULL);
    if (self->swapchain)
      vkDestroySwapchainKHR(dev, self->swapchain, NULL);
    if (self->surface)
      vkDestroySurfaceKHR(g_vulkan_instance, self->surface, NULL);
    if (self->fences) {
      for (uint32_t i = 0; i < self->image_count; i++) {
        if (self->fences[i])
          vkDestroyFence(dev, self->fences[i], NULL);
      }
      PyMem_Free(self->fences);
    }
    PyMem_Free(self->images);
    Py_DECREF(self->device);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* -------------------------------------------------------------------------
   Internal constructor (called from Device.create_swapchain)
   ------------------------------------------------------------------------- */
VkComp_Swapchain *VkComp_Swapchain_Create(VkComp_Device *device,
                                          PyObject *window_handle, int format,
                                          uint32_t num_buffers, uint32_t width,
                                          uint32_t height,
                                          const char *present_mode_str) {
  VkComp_Swapchain *sc = PyObject_New(VkComp_Swapchain, &VkComp_Swapchain_Type);
  if (!sc)
    return NULL;
  VKCOMP_CLEAR_OBJECT(sc);
  sc->device = device;
  Py_INCREF(device);

  /* Validate format */
  VkFormat vk_format = g_vulkan_format_table[format].vk_format;
  if (vk_format == VK_FORMAT_UNDEFINED) {
    PyErr_Format(VkComp_SwapchainError, "Invalid pixel format: %d", format);
    Py_DECREF(sc);
    return NULL;
  }
  sc->format = vk_format;

  /* Create surface from window handle (X11) */
  if (create_surface(sc, window_handle) != VK_SUCCESS) {
    Py_DECREF(sc);
    return NULL;
  }

  /* Select present mode */
  VkPresentModeKHR desired_mode;
  if (strcmp(present_mode_str, "immediate") == 0) {
    desired_mode = VK_PRESENT_MODE_IMMEDIATE_KHR;
  } else if (strcmp(present_mode_str, "mailbox") == 0) {
    desired_mode = VK_PRESENT_MODE_MAILBOX_KHR;
  } else if (strcmp(present_mode_str, "fifo") == 0) {
    desired_mode = VK_PRESENT_MODE_FIFO_KHR;
  } else {
    PyErr_Format(
        VkComp_SwapchainError,
        "Invalid present_mode: '%s'. Use 'fifo', 'mailbox', or 'immediate'.",
        present_mode_str);
    Py_DECREF(sc);
    return NULL;
  }

  /* Query supported present modes and fallback if needed */
  uint32_t mode_count = 0;
  vkGetPhysicalDeviceSurfacePresentModesKHR(device->physical_device,
                                            sc->surface, &mode_count, NULL);
  VkPresentModeKHR *modes = PyMem_Malloc(mode_count * sizeof(VkPresentModeKHR));
  if (!modes) {
    Py_DECREF(sc);
    return PyErr_NoMemory();
  }
  vkGetPhysicalDeviceSurfacePresentModesKHR(device->physical_device,
                                            sc->surface, &mode_count, modes);
  bool supported = false;
  for (uint32_t i = 0; i < mode_count; i++) {
    if (modes[i] == desired_mode) {
      supported = true;
      break;
    }
  }
  VkPresentModeKHR selected_mode =
      supported ? desired_mode : VK_PRESENT_MODE_FIFO_KHR;
  PyMem_Free(modes);

  /* Create swapchain */
  if (create_swapchain(sc, width, height, vk_format, num_buffers,
                       selected_mode) != VK_SUCCESS) {
    Py_DECREF(sc);
    return NULL;
  }

  /* Create semaphores */
  VkSemaphoreCreateInfo sem_info = {VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO};
  if (vkCreateSemaphore(device->device, &sem_info, NULL, &sc->copy_semaphore) !=
          VK_SUCCESS ||
      vkCreateSemaphore(device->device, &sem_info, NULL,
                        &sc->present_semaphore) != VK_SUCCESS) {
    Py_DECREF(sc);
    PyErr_SetString(VkComp_SwapchainError, "Failed to create semaphores");
    return NULL;
  }

  /* Transition swapchain images to present layout */
  VkCommandBuffer cmd;
  if (VkComp_Device_AllocateCmd(device, &cmd) == VK_SUCCESS) {
    VkCommandBufferBeginInfo begin_info = {
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
        .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
    };
    vkBeginCommandBuffer(cmd, &begin_info);

    for (uint32_t i = 0; i < sc->image_count; i++) {
      VkImageMemoryBarrier barrier = {
          .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
          .srcAccessMask = 0,
          .dstAccessMask = VK_ACCESS_MEMORY_READ_BIT,
          .oldLayout = VK_IMAGE_LAYOUT_UNDEFINED,
          .newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
          .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .image = sc->images[i],
          .subresourceRange =
              {
                  .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                  .baseMipLevel = 0,
                  .levelCount = 1,
                  .baseArrayLayer = 0,
                  .layerCount = 1,
              },
      };
      vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                           VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0, 0, NULL, 0,
                           NULL, 1, &barrier);
    }
    vkEndCommandBuffer(cmd);
    vkcomp_submit_and_wait(device, cmd, VK_NULL_HANDLE);
    VkComp_Device_FreeCmd(device, cmd);
  }

  return sc;
}

/* -------------------------------------------------------------------------
   Create X11 surface
   ------------------------------------------------------------------------- */
static VkResult create_surface(VkComp_Swapchain *sc, PyObject *window_handle) {
  if (!PyTuple_Check(window_handle) || PyTuple_Size(window_handle) != 2) {
    PyErr_SetString(VkComp_SwapchainError,
                    "Window handle must be a tuple (display_ptr, window_ptr)");
    return VK_ERROR_INITIALIZATION_FAILED;
  }

  unsigned long long display_ptr, window_ptr;
  if (!PyArg_ParseTuple(window_handle, "KK", &display_ptr, &window_ptr)) {
    return VK_ERROR_INITIALIZATION_FAILED;
  }

  VkXlibSurfaceCreateInfoKHR surf_info = {
      .sType = VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR,
      .dpy = (Display *)display_ptr,
      .window = (Window)window_ptr,
  };
  return vkCreateXlibSurfaceKHR(g_vulkan_instance, &surf_info, NULL,
                                &sc->surface);
}

/* -------------------------------------------------------------------------
   Create swapchain
   ------------------------------------------------------------------------- */
static VkResult create_swapchain(VkComp_Swapchain *sc, uint32_t width,
                                 uint32_t height, VkFormat format,
                                 uint32_t num_buffers,
                                 VkPresentModeKHR present_mode) {
  VkPhysicalDevice phys = sc->device->physical_device;
  VkDevice dev = sc->device->device;
  uint32_t qf_index = sc->device->queue_family_index;

  /* Check surface support */
  VkBool32 supported;
  vkGetPhysicalDeviceSurfaceSupportKHR(phys, qf_index, sc->surface, &supported);
  if (!supported) {
    PyErr_SetString(VkComp_SwapchainError, "Surface not supported by device");
    return VK_ERROR_INITIALIZATION_FAILED;
  }

  /* Get surface capabilities */
  VkSurfaceCapabilitiesKHR caps;
  vkGetPhysicalDeviceSurfaceCapabilitiesKHR(phys, sc->surface, &caps);

  VkExtent2D extent = caps.currentExtent;
  if (extent.width == UINT32_MAX) {
    /* Surface size is determined by the swapchain; use provided dimensions */
    extent.width = width ? width : 800;
    extent.height = height ? height : 600;
    extent.width = Py_MIN(Py_MAX(extent.width, caps.minImageExtent.width),
                          caps.maxImageExtent.width);
    extent.height = Py_MIN(Py_MAX(extent.height, caps.minImageExtent.height),
                           caps.maxImageExtent.height);
  }
  sc->image_extent = extent;

  num_buffers = Py_MAX(num_buffers, caps.minImageCount);
  if (caps.maxImageCount > 0)
    num_buffers = Py_MIN(num_buffers, caps.maxImageCount);

  VkCompositeAlphaFlagBitsKHR composite_alpha =
      VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
  if (!(caps.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR)) {
    VkCompositeAlphaFlagBitsKHR bits[] = {
        VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
        VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR,
        VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR,
        VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR};
    for (int i = 0; i < 4; i++) {
      if (caps.supportedCompositeAlpha & bits[i]) {
        composite_alpha = bits[i];
        break;
      }
    }
  }

  VkSwapchainCreateInfoKHR create_info = {
      .sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
      .surface = sc->surface,
      .minImageCount = num_buffers,
      .imageFormat = format,
      .imageColorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR,
      .imageExtent = extent,
      .imageArrayLayers = 1,
      .imageUsage = VK_IMAGE_USAGE_TRANSFER_DST_BIT,
      .imageSharingMode = VK_SHARING_MODE_EXCLUSIVE,
      .preTransform = caps.currentTransform,
      .compositeAlpha = composite_alpha,
      .presentMode = present_mode,
      .clipped = VK_TRUE,
  };

  VkResult res = vkCreateSwapchainKHR(dev, &create_info, NULL, &sc->swapchain);
  if (res != VK_SUCCESS)
    return res;

  vkGetSwapchainImagesKHR(dev, sc->swapchain, &sc->image_count, NULL);
  sc->images = PyMem_Malloc(sc->image_count * sizeof(VkImage));
  if (!sc->images)
    return VK_ERROR_OUT_OF_HOST_MEMORY;
  vkGetSwapchainImagesKHR(dev, sc->swapchain, &sc->image_count, sc->images);

  /* Create per‑image fences */
  sc->fences = PyMem_Malloc(sc->image_count * sizeof(VkFence));
  if (!sc->fences)
    return VK_ERROR_OUT_OF_HOST_MEMORY;
  VkFenceCreateInfo fence_info = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
  for (uint32_t i = 0; i < sc->image_count; i++) {
    vkCreateFence(dev, &fence_info, NULL, &sc->fences[i]);
  }

  sc->suboptimal = false;
  sc->out_of_date = false;
  return VK_SUCCESS;
}

/* -------------------------------------------------------------------------
   present(texture, x=0, y=0, wait_for_fence=True)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Swapchain_Present(VkComp_Swapchain *self, PyObject *args) {
  PyObject *tex_obj;
  unsigned int x = 0, y = 0;
  int wait_for_fence = 1;
  if (!PyArg_ParseTuple(args, "O|IIp", &tex_obj, &x, &y, &wait_for_fence))
    return NULL;

  if (!PyObject_TypeCheck(tex_obj, &VkComp_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Texture object");
    return NULL;
  }
  VkComp_Resource *tex = (VkComp_Resource *)tex_obj;
  if (!VkComp_Resource_IsTexture(tex)) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
    return NULL;
  }

  VkComp_Device *dev = VkComp_Device_GetActive(self->device);
  if (!dev)
    return NULL;

  /* Acquire next image */
  uint32_t image_index;
  VkResult res =
      vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                            self->copy_semaphore, VK_NULL_HANDLE, &image_index);
  if (res == VK_ERROR_OUT_OF_DATE_KHR) {
    self->out_of_date = true;
    Py_RETURN_NONE;
  }
  if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
    PyErr_Format(VkComp_SwapchainError, "Failed to acquire swapchain image: %d",
                 res);
    return NULL;
  }
  self->suboptimal = (res == VK_SUBOPTIMAL_KHR);
  self->out_of_date = false;

  /* Clamp coordinates */
  x = Py_MIN(x, self->image_extent.width - 1);
  y = Py_MIN(y, self->image_extent.height - 1);

  VkCommandBuffer cmd;
  res = VkComp_Device_AllocateCmd(dev, &cmd);
  if (res != VK_SUCCESS) {
    PyErr_Format(VkComp_SwapchainError, "Failed to allocate command buffer: %d",
                 res);
    return NULL;
  }

  VkCommandBufferBeginInfo begin_info = {
      .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
      .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
  };
  vkBeginCommandBuffer(cmd, &begin_info);

  /* Transition both images */
  VkImageMemoryBarrier barriers[2] = {
      {
          .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
          .srcAccessMask = VK_ACCESS_MEMORY_READ_BIT,
          .dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT,
          .oldLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
          .newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
          .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .image = self->images[image_index],
          .subresourceRange =
              {
                  .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                  .baseMipLevel = 0,
                  .levelCount = 1,
                  .baseArrayLayer = 0,
                  .layerCount = 1,
              },
      },
      {
          .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
          .srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT,
          .dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT,
          .oldLayout = VK_IMAGE_LAYOUT_GENERAL,
          .newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
          .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
          .image = tex->image,
          .subresourceRange =
              {
                  .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                  .baseMipLevel = 0,
                  .levelCount = 1,
                  .baseArrayLayer = 0,
                  .layerCount = 1,
              },
      }};
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 2,
                       barriers);

  /* Copy region */
  VkImageCopy region = {
      .srcSubresource = {.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                         .layerCount = 1},
      .dstSubresource = {.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                         .layerCount = 1},
      .dstOffset = {(int32_t)x, (int32_t)y, 0},
      .extent = {Py_MIN(tex->image_extent.width, self->image_extent.width - x),
                 Py_MIN(tex->image_extent.height,
                        self->image_extent.height - y),
                 1},
  };
  vkCmdCopyImage(cmd, tex->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                 self->images[image_index],
                 VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

  /* Transition back */
  barriers[0].srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barriers[0].dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;
  barriers[0].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barriers[0].newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
  barriers[1].srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barriers[1].dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;
  barriers[1].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barriers[1].newLayout = VK_IMAGE_LAYOUT_GENERAL;
  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0, 0, NULL, 0,
                       NULL, 2, barriers);

  vkEndCommandBuffer(cmd);

  /* Submit */
  VkPipelineStageFlags wait_stage = VK_PIPELINE_STAGE_TRANSFER_BIT;
  VkSubmitInfo submit_info = {
      .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
      .waitSemaphoreCount = 1,
      .pWaitSemaphores = &self->copy_semaphore,
      .pWaitDstStageMask = &wait_stage,
      .commandBufferCount = 1,
      .pCommandBuffers = &cmd,
      .signalSemaphoreCount = 1,
      .pSignalSemaphores = &self->present_semaphore,
  };

  VkFence fence = self->fences[image_index];
  vkResetFences(dev->device, 1, &fence);
  res = vkQueueSubmit(dev->queue, 1, &submit_info, fence);
  if (res != VK_SUCCESS) {
    VkComp_Device_FreeCmd(dev, cmd);
    PyErr_Format(VkComp_SwapchainError, "Queue submit failed: %d", res);
    return NULL;
  }

  /* Present */
  VkPresentInfoKHR present_info = {
      .sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
      .waitSemaphoreCount = 1,
      .pWaitSemaphores = &self->present_semaphore,
      .swapchainCount = 1,
      .pSwapchains = &self->swapchain,
      .pImageIndices = &image_index,
  };
  res = vkQueuePresentKHR(dev->queue, &present_info);
  if (res == VK_ERROR_OUT_OF_DATE_KHR || res == VK_SUBOPTIMAL_KHR) {
    self->out_of_date = (res == VK_ERROR_OUT_OF_DATE_KHR);
    self->suboptimal = (res == VK_SUBOPTIMAL_KHR);
  } else if (res != VK_SUCCESS) {
    VkComp_Device_FreeCmd(dev, cmd);
    PyErr_Format(VkComp_SwapchainError, "Present failed: %d", res);
    return NULL;
  }

  VkComp_Device_FreeCmd(dev, cmd);

  if (wait_for_fence) {
    vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
  }

  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   Status query methods
   ------------------------------------------------------------------------- */
PyObject *VkComp_Swapchain_IsSuboptimal(VkComp_Swapchain *self,
                                        PyObject *ignored) {
  return PyBool_FromLong(self->suboptimal);
}

PyObject *VkComp_Swapchain_IsOutOfDate(VkComp_Swapchain *self,
                                       PyObject *ignored) {
  return PyBool_FromLong(self->out_of_date);
}

PyObject *VkComp_Swapchain_NeedsRecreation(VkComp_Swapchain *self,
                                           PyObject *ignored) {
  return PyBool_FromLong(self->suboptimal || self->out_of_date);
}