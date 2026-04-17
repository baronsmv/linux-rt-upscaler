#include "vk_device.h"
#include "vk_swapchain.h"
#include "vk_utils.h"
#include <X11/Xlib.h>
#include <vulkan/vulkan_xlib.h>

void vk_Swapchain_dealloc(vk_Swapchain *self) {
    if (self->py_device) {
        VkDevice dev = self->py_device->device;
        if (self->copy_semaphore) vkDestroySemaphore(dev, self->copy_semaphore, nullptr);
        if (self->present_semaphore) vkDestroySemaphore(dev, self->present_semaphore, nullptr);
        if (self->swapchain) vkDestroySwapchainKHR(dev, self->swapchain, nullptr);
        if (self->surface) vkDestroySurfaceKHR(vk_instance, self->surface, nullptr);
        if (self->fences) {
            for (uint32_t i = 0; i < self->image_count; ++i) {
                if (self->fences[i]) vkDestroyFence(dev, self->fences[i], nullptr);
            }
            PyMem_Free(self->fences);
        }
        Py_DECREF(self->py_device);
    }
    self->images.~vector<VkImage>();
    Py_TYPE(self)->tp_free(reinterpret_cast<PyObject *>(self));
}

static VkPresentModeKHR choose_present_mode(VkPhysicalDevice phys, VkSurfaceKHR surface, const char *mode_str) {
    uint32_t count;
    vkGetPhysicalDeviceSurfacePresentModesKHR(phys, surface, &count, nullptr);
    std::vector<VkPresentModeKHR> modes(count);
    vkGetPhysicalDeviceSurfacePresentModesKHR(phys, surface, &count, modes.data());

    VkPresentModeKHR desired;
    if (strcmp(mode_str, "immediate") == 0) desired = VK_PRESENT_MODE_IMMEDIATE_KHR;
    else if (strcmp(mode_str, "mailbox") == 0) desired = VK_PRESENT_MODE_MAILBOX_KHR;
    else desired = VK_PRESENT_MODE_FIFO_KHR; // default "fifo"

    for (auto m : modes) if (m == desired) return desired;
    return VK_PRESENT_MODE_FIFO_KHR; // fallback
}

PyObject *vk_Device_create_swapchain_impl(vk_Device *self, PyObject *args) {
    PyObject *py_window_handle;
    int format;
    uint32_t num_buffers;
    uint32_t width = 0, height = 0;
    const char *present_mode_str = "fifo";

    if (!PyArg_ParseTuple(args, "OiI|IIs", &py_window_handle, &format, &num_buffers,
                          &width, &height, &present_mode_str))
        return nullptr;

    if (!vk_supports_swapchain) {
        PyErr_SetString(vk_SwapchainError, "Swapchain not supported");
        return nullptr;
    }
    if (vk_format_map.find(format) == vk_format_map.end()) {
        PyErr_Format(PyExc_ValueError, "Invalid pixel format %d", format);
        return nullptr;
    }

    vk_Device *dev = vk_Device_get_initialized(self);
    if (!dev) return nullptr;

    // Parse window handle (X11 only for simplicity)
    if (!PyTuple_Check(py_window_handle) || PyTuple_Size(py_window_handle) != 2) {
        PyErr_SetString(PyExc_ValueError, "window_handle must be (display_ptr, window_ptr)");
        return nullptr;
    }
    unsigned long display_ptr, window_ptr;
    if (!PyArg_ParseTuple(py_window_handle, "KK", &display_ptr, &window_ptr))
        return nullptr;

    vk_Swapchain *sc = PyObject_New(vk_Swapchain, &vk_Swapchain_Type);
    if (!sc) return PyErr_NoMemory();
    VK_CLEAR_OBJECT(sc);
    new (&sc->images) std::vector<VkImage>();
    sc->py_device = dev;
    Py_INCREF(dev);
    sc->suboptimal = sc->out_of_date = false;

    // Create Xlib surface
    VkXlibSurfaceCreateInfoKHR surf_info = { VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR };
    surf_info.dpy = (Display *)display_ptr;
    surf_info.window = (Window)window_ptr;
    if (vkCreateXlibSurfaceKHR(vk_instance, &surf_info, nullptr, &sc->surface) != VK_SUCCESS) {
        Py_DECREF(sc);
        PyErr_SetString(vk_SwapchainError, "Failed to create Xlib surface");
        return nullptr;
    }

    // Check surface support
    VkBool32 supported;
    vkGetPhysicalDeviceSurfaceSupportKHR(dev->physical_device, dev->queue_family_index,
                                         sc->surface, &supported);
    if (!supported) {
        Py_DECREF(sc);
        PyErr_SetString(vk_SwapchainError, "Surface not supported by device");
        return nullptr;
    }

    VkSurfaceCapabilitiesKHR caps;
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR(dev->physical_device, sc->surface, &caps);
    VkExtent2D extent = caps.currentExtent;
    if (width) extent.width = width;
    if (height) extent.height = height;
    // Clamp to surface limits
    extent.width = std::max(caps.minImageExtent.width, std::min(extent.width, caps.maxImageExtent.width));
    extent.height = std::max(caps.minImageExtent.height, std::min(extent.height, caps.maxImageExtent.height));
    sc->image_extent = extent;

    VkPresentModeKHR present_mode = choose_present_mode(dev->physical_device, sc->surface, present_mode_str);

    VkSwapchainCreateInfoKHR swap_info = { VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR };
    swap_info.surface = sc->surface;
    swap_info.minImageCount = std::max(num_buffers, caps.minImageCount);
    swap_info.imageFormat = vk_format_map[format].first;
    swap_info.imageColorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR;
    swap_info.imageExtent = extent;
    swap_info.imageArrayLayers = 1;
    swap_info.imageUsage = VK_IMAGE_USAGE_TRANSFER_DST_BIT;
    swap_info.preTransform = caps.currentTransform;
    swap_info.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
    swap_info.presentMode = present_mode;
    swap_info.clipped = VK_TRUE;

    if (vkCreateSwapchainKHR(dev->device, &swap_info, nullptr, &sc->swapchain) != VK_SUCCESS) {
        Py_DECREF(sc);
        PyErr_SetString(vk_SwapchainError, "Failed to create swapchain");
        return nullptr;
    }

    uint32_t img_count;
    vkGetSwapchainImagesKHR(dev->device, sc->swapchain, &img_count, nullptr);
    sc->images.resize(img_count);
    vkGetSwapchainImagesKHR(dev->device, sc->swapchain, &img_count, sc->images.data());
    sc->image_count = img_count;

    // Create per-image fences and semaphores
    sc->fences = (VkFence *)PyMem_Malloc(sizeof(VkFence) * img_count);
    VkFenceCreateInfo finfo = { VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    for (uint32_t i = 0; i < img_count; ++i) {
        vkCreateFence(dev->device, &finfo, nullptr, &sc->fences[i]);
    }

    VkSemaphoreCreateInfo sem_info = { VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO };
    vkCreateSemaphore(dev->device, &sem_info, nullptr, &sc->copy_semaphore);
    vkCreateSemaphore(dev->device, &sem_info, nullptr, &sc->present_semaphore);

    return reinterpret_cast<PyObject *>(sc);
}

PyObject *vk_Swapchain_present(vk_Swapchain *self, PyObject *args) {
    PyObject *tex_obj;
    uint32_t x = 0, y = 0;
    int wait_for_fence = 1;
    if (!PyArg_ParseTuple(args, "O|IIp", &tex_obj, &x, &y, &wait_for_fence))
        return nullptr;

    if (!PyObject_TypeCheck(tex_obj, &vk_Resource_Type)) {
        PyErr_SetString(PyExc_TypeError, "Expected a Texture resource");
        return nullptr;
    }
    vk_Resource *tex = reinterpret_cast<vk_Resource *>(tex_obj);
    if (!tex->image) {
        PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
        return nullptr;
    }

    vk_Device *dev = self->py_device;

    uint32_t image_index;
    VkResult res = vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                                         self->copy_semaphore, VK_NULL_HANDLE, &image_index);
    if (res == VK_ERROR_OUT_OF_DATE_KHR) {
        self->out_of_date = true;
        Py_RETURN_NONE;
    }
    if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
        PyErr_Format(PyExc_RuntimeError, "Failed to acquire swapchain image (error %d)", res);
        return nullptr;
    }
    self->suboptimal = (res == VK_SUBOPTIMAL_KHR);
    self->out_of_date = false;

    VkCommandBuffer cmd = vk_allocate_temp_cmd(dev);
    if (!cmd) {
        PyErr_SetString(vk_ComputeError, "Failed to allocate command buffer");
        return nullptr;
    }

    VkCommandBufferBeginInfo begin = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO };
    vkBeginCommandBuffer(cmd, &begin);

    // Transition swapchain image to TRANSFER_DST_OPTIMAL
    vk_image_barrier(cmd, self->images[image_index],
                     VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                     VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT,
                     0, VK_ACCESS_TRANSFER_WRITE_BIT,
                     0, 1, 0, 1);

    // Transition source texture to TRANSFER_SRC_OPTIMAL
    vk_image_barrier(cmd, tex->image,
                     VK_IMAGE_LAYOUT_GENERAL, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                     VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT,
                     VK_ACCESS_SHADER_WRITE_BIT, VK_ACCESS_TRANSFER_READ_BIT,
                     0, 1, 0, 1);

    // Blit (copy) region
    VkImageCopy region = {};
    region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.srcSubresource.layerCount = 1;
    region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    region.dstSubresource.layerCount = 1;
    region.extent.width = std::min(tex->image_extent.width, self->image_extent.width - x);
    region.extent.height = std::min(tex->image_extent.height, self->image_extent.height - y);
    region.extent.depth = 1;
    region.dstOffset = { (int32_t)x, (int32_t)y, 0 };

    vkCmdCopyImage(cmd, tex->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   self->images[image_index], VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
                   1, &region);

    // Transition swapchain image to PRESENT_SRC_KHR
    vk_image_barrier(cmd, self->images[image_index],
                     VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_PRESENT_SRC_KHR,
                     VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
                     VK_ACCESS_TRANSFER_WRITE_BIT, 0,
                     0, 1, 0, 1);

    // Transition source texture back to GENERAL
    vk_image_barrier(cmd, tex->image,
                     VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_IMAGE_LAYOUT_GENERAL,
                     VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                     VK_ACCESS_TRANSFER_READ_BIT, VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT,
                     0, 1, 0, 1);

    vkEndCommandBuffer(cmd);

    VkPipelineStageFlags wait_stage = VK_PIPELINE_STAGE_TRANSFER_BIT;
    VkSubmitInfo submit = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
    submit.waitSemaphoreCount = 1;
    submit.pWaitSemaphores = &self->copy_semaphore;
    submit.pWaitDstStageMask = &wait_stage;
    submit.commandBufferCount = 1;
    submit.pCommandBuffers = &cmd;
    submit.signalSemaphoreCount = 1;
    submit.pSignalSemaphores = &self->present_semaphore;

    VkFence fence = self->fences[image_index];
    vkResetFences(dev->device, 1, &fence);
    res = vkQueueSubmit(dev->queue, 1, &submit, fence);
    if (res != VK_SUCCESS) {
        vk_free_temp_cmd(dev, cmd);
        PyErr_Format(PyExc_RuntimeError, "Queue submit failed (error %d)", res);
        return nullptr;
    }

    VkPresentInfoKHR present = { VK_STRUCTURE_TYPE_PRESENT_INFO_KHR };
    present.waitSemaphoreCount = 1;
    present.pWaitSemaphores = &self->present_semaphore;
    present.swapchainCount = 1;
    present.pSwapchains = &self->swapchain;
    present.pImageIndices = &image_index;

    res = vkQueuePresentKHR(dev->queue, &present);
    if (res == VK_ERROR_OUT_OF_DATE_KHR || res == VK_SUBOPTIMAL_KHR) {
        self->out_of_date = (res == VK_ERROR_OUT_OF_DATE_KHR);
        self->suboptimal = (res == VK_SUBOPTIMAL_KHR);
    } else if (res != VK_SUCCESS) {
        vk_free_temp_cmd(dev, cmd);
        PyErr_Format(PyExc_RuntimeError, "Present failed (error %d)", res);
        return nullptr;
    }

    if (wait_for_fence) {
        vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
    }

    vk_free_temp_cmd(dev, cmd);
    Py_RETURN_NONE;
}

PyObject *vk_Swapchain_is_suboptimal(vk_Swapchain *self, PyObject *ignored) {
    return PyBool_FromLong(self->suboptimal);
}
PyObject *vk_Swapchain_is_out_of_date(vk_Swapchain *self, PyObject *ignored) {
    return PyBool_FromLong(self->out_of_date);
}
PyObject *vk_Swapchain_needs_recreation(vk_Swapchain *self, PyObject *ignored) {
    return PyBool_FromLong(self->suboptimal || self->out_of_date);
}

static PyMemberDef vk_Swapchain_members[] = {
    {"width", T_UINT, offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, width), 0, "Swapchain width"},
    {"height", T_UINT, offsetof(vk_Swapchain, image_extent) + offsetof(VkExtent2D, height), 0, "Swapchain height"},
    {nullptr}
};

static PyMethodDef vk_Swapchain_methods[] = {
    {"present", (PyCFunction)vk_Swapchain_present, METH_VARARGS, "Present a texture to the swapchain."},
    {"is_suboptimal", (PyCFunction)vk_Swapchain_is_suboptimal, METH_NOARGS, "Return True if swapchain is suboptimal."},
    {"is_out_of_date", (PyCFunction)vk_Swapchain_is_out_of_date, METH_NOARGS, "Return True if swapchain is out of date."},
    {"needs_recreation", (PyCFunction)vk_Swapchain_needs_recreation, METH_NOARGS, "Return True if swapchain needs recreation."},
    {nullptr, nullptr, 0, nullptr}
};

PyTypeObject vk_Swapchain_Type = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "vulkan.Swapchain",               /* tp_name */
    sizeof(vk_Swapchain),             /* tp_basicsize */
    0,                                /* tp_itemsize */
    (destructor)vk_Swapchain_dealloc, /* tp_dealloc */
    0,                                /* tp_vectorcall_offset */
    0,                                /* tp_getattr */
    0,                                /* tp_setattr */
    0,                                /* tp_as_async */
    0,                                /* tp_repr */
    0,                                /* tp_as_number */
    0,                                /* tp_as_sequence */
    0,                                /* tp_as_mapping */
    0,                                /* tp_hash */
    0,                                /* tp_call */
    0,                                /* tp_str */
    0,                                /* tp_getattro */
    0,                                /* tp_setattro */
    0,                                /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,               /* tp_flags */
    0,                                /* tp_doc */
    0,                                /* tp_traverse */
    0,                                /* tp_clear */
    0,                                /* tp_richcompare */
    0,                                /* tp_weaklistoffset */
    0,                                /* tp_iter */
    0,                                /* tp_iternext */
    vk_Swapchain_methods,             /* tp_methods */
    vk_Swapchain_members,             /* tp_members */
    0,                                /* tp_getset */
    0,                                /* tp_base */
    0,                                /* tp_dict */
    0,                                /* tp_descr_get */
    0,                                /* tp_descr_set */
    0,                                /* tp_dictoffset */
    0,                                /* tp_init */
    0,                                /* tp_alloc */
    0,                                /* tp_new */
};