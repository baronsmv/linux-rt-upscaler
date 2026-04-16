#include "vulkan_common.h"

/* ----------------------------------------------------------------------------
   Forward declaration
   ------------------------------------------------------------------------- */
static void vulkan_Swapchain_dealloc(vulkan_Swapchain *self);

/* ----------------------------------------------------------------------------
   Swapchain Type
   ------------------------------------------------------------------------- */
static PyMemberDef vulkan_Swapchain_members[] = {
    {"width", T_UINT,
     offsetof(vulkan_Swapchain, image_extent) + offsetof(VkExtent2D, width), 0,
     "swapchain width"},
    {"height", T_UINT,
     offsetof(vulkan_Swapchain, image_extent) + offsetof(VkExtent2D, height), 0,
     "swapchain height"},
    {NULL}};

PyTypeObject vulkan_Swapchain_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "vulkan.Swapchain",
    .tp_basicsize = sizeof(vulkan_Swapchain),
    .tp_dealloc = (destructor)vulkan_Swapchain_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = vulkan_Swapchain_members,
};

/* ----------------------------------------------------------------------------
   Deallocator
   ------------------------------------------------------------------------- */
static void vulkan_Swapchain_dealloc(vulkan_Swapchain *self) {
  if (self->py_device) {
    VkDevice dev = self->py_device->device;
    if (self->copy_semaphore)
      vkDestroySemaphore(dev, self->copy_semaphore, NULL);
    if (self->present_semaphore)
      vkDestroySemaphore(dev, self->present_semaphore, NULL);
    if (self->swapchain)
      vkDestroySwapchainKHR(dev, self->swapchain, NULL);
    if (self->surface)
      vkDestroySurfaceKHR(vulkan_instance, self->surface, NULL);
    if (self->fences) {
      for (uint32_t i = 0; i < self->image_count; i++) {
        if (self->fences[i])
          vkDestroyFence(dev, self->fences[i], NULL);
      }
      PyMem_Free(self->fences);
    }
    Py_DECREF(self->py_device);
  }
  self->images.~vector<VkImage>();
  Py_TYPE(self)->tp_free((PyObject *)self);
}

/* ----------------------------------------------------------------------------
   vulkan_Swapchain_present
   ------------------------------------------------------------------------- */
PyObject *vulkan_Swapchain_present(vulkan_Swapchain *self, PyObject *args) {
  PyObject *tex_obj;
  uint32_t x = 0, y = 0;
  int wait_for_fence = 1; // default true for safety

  if (!PyArg_ParseTuple(args, "O|IIp", &tex_obj, &x, &y, &wait_for_fence))
    return NULL;

  if (!PyObject_TypeCheck(tex_obj, &vulkan_Resource_Type)) {
    PyErr_SetString(PyExc_TypeError, "Expected a Texture2D object");
    return NULL;
  }

  vulkan_Resource *tex = (vulkan_Resource *)tex_obj;
  if (!tex->image) {
    PyErr_SetString(PyExc_TypeError, "Resource is not a texture");
    return NULL;
  }

  vulkan_Device *dev = self->py_device;
  vkQueueWaitIdle(dev->queue);

  uint32_t image_index;
  VkResult res =
      vkAcquireNextImageKHR(dev->device, self->swapchain, UINT64_MAX,
                            self->copy_semaphore, VK_NULL_HANDLE, &image_index);
  if (res == VK_ERROR_OUT_OF_DATE_KHR) {
    self->out_of_date = true;
    Py_RETURN_NONE;
  }
  if (res != VK_SUCCESS && res != VK_SUBOPTIMAL_KHR) {
    return PyErr_Format(PyExc_RuntimeError,
                        "Failed to acquire swapchain image: %d", res);
  }
  self->suboptimal = (res == VK_SUBOPTIMAL_KHR);
  self->out_of_date = false;

  x = Py_MIN(x, self->image_extent.width - 1);
  y = Py_MIN(y, self->image_extent.height - 1);

  VkCommandBuffer cmd = dev->command_buffer;
  res = vkResetCommandBuffer(cmd, 0);
  if (res != VK_SUCCESS) {
    return PyErr_Format(Compushady_ComputeError,
                        "Failed to reset command buffer");
  }

  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  VkImageMemoryBarrier barriers[2] = {};
  barriers[0].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
  barriers[1].sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;

  // Transition swapchain image to TRANSFER_DST_OPTIMAL
  barriers[0].image = self->images[image_index];
  barriers[0].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barriers[0].subresourceRange.layerCount = 1;
  barriers[0].oldLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
  barriers[0].newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barriers[0].srcAccessMask = VK_ACCESS_MEMORY_READ_BIT;
  barriers[0].dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;

  // Transition source texture to TRANSFER_SRC_OPTIMAL
  barriers[1].image = tex->image;
  barriers[1].subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barriers[1].subresourceRange.layerCount = 1;
  barriers[1].oldLayout = VK_IMAGE_LAYOUT_GENERAL;
  barriers[1].newLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barriers[1].srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  barriers[1].dstAccessMask = VK_ACCESS_TRANSFER_READ_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
                       VK_PIPELINE_STAGE_TRANSFER_BIT, 0, 0, NULL, 0, NULL, 2,
                       barriers);

  VkImageCopy region = {0};
  region.srcSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  region.srcSubresource.layerCount = 1;
  region.dstSubresource.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  region.dstSubresource.layerCount = 1;
  region.extent.width =
      Py_MIN(tex->image_extent.width, self->image_extent.width - x);
  region.extent.height =
      Py_MIN(tex->image_extent.height, self->image_extent.height - y);
  region.extent.depth = 1;
  region.dstOffset.x = x;
  region.dstOffset.y = y;

  vkCmdCopyImage(cmd, tex->image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                 self->images[image_index],
                 VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &region);

  barriers[0].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
  barriers[0].newLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
  barriers[0].srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
  barriers[0].dstAccessMask = VK_ACCESS_MEMORY_READ_BIT;

  barriers[1].oldLayout = VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
  barriers[1].newLayout = VK_IMAGE_LAYOUT_GENERAL;
  barriers[1].srcAccessMask = VK_ACCESS_TRANSFER_READ_BIT;
  barriers[1].dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_TRANSFER_BIT,
                       VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, 0, 0, NULL, 0,
                       NULL, 2, barriers);

  vkEndCommandBuffer(cmd);

  VkPipelineStageFlags wait_stage = VK_PIPELINE_STAGE_TRANSFER_BIT;
  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
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
  if (res != VK_SUCCESS)
    return PyErr_Format(PyExc_RuntimeError, "Queue submit failed: %d", res);

  VkPresentInfoKHR present = {VK_STRUCTURE_TYPE_PRESENT_INFO_KHR};
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
    return PyErr_Format(PyExc_RuntimeError, "Present failed: %d", res);
  }

  if (wait_for_fence) {
    vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
  }

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_Swapchain_is_suboptimal
   ------------------------------------------------------------------------- */
PyObject *vulkan_Swapchain_is_suboptimal(vulkan_Swapchain *self,
                                         PyObject *ignored) {
  if (self->suboptimal)
    Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

/* ----------------------------------------------------------------------------
   vulkan_Swapchain_is_out_of_date
   ------------------------------------------------------------------------- */
PyObject *vulkan_Swapchain_is_out_of_date(vulkan_Swapchain *self,
                                          PyObject *ignored) {
  if (self->out_of_date)
    Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

/* ----------------------------------------------------------------------------
   vulkan_Swapchain_needs_recreation
   ------------------------------------------------------------------------- */
PyObject *vulkan_Swapchain_needs_recreation(vulkan_Swapchain *self,
                                            PyObject *ignored) {
  if (self->suboptimal || self->out_of_date)
    Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

/* ----------------------------------------------------------------------------
   Method table
   ------------------------------------------------------------------------- */
PyMethodDef vulkan_Swapchain_methods[] = {
    {"present", (PyCFunction)vulkan_Swapchain_present, METH_VARARGS,
     "Blit a texture resource to the Swapchain and present it"},
    {"is_suboptimal", (PyCFunction)vulkan_Swapchain_is_suboptimal, METH_NOARGS,
     "Return True if the swapchain is suboptimal."},
    {"is_out_of_date", (PyCFunction)vulkan_Swapchain_is_out_of_date,
     METH_NOARGS, "Return True if the swapchain is out of date."},
    {"needs_recreation", (PyCFunction)vulkan_Swapchain_needs_recreation,
     METH_NOARGS, "Return True if the swapchain needs to be recreated."},
    {NULL, NULL, 0, NULL}};