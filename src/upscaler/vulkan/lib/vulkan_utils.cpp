#include "vulkan_common.h"
#include <cmath>
#include <cstring>

/* ----------------------------------------------------------------------------
   Global state definitions (single instance across all files)
   ------------------------------------------------------------------------- */
VkInstance vulkan_instance = VK_NULL_HANDLE;
bool vulkan_supports_swapchain = false;
bool vulkan_supports_wayland = false;
bool vulkan_debug = false;
std::unordered_map<uint32_t, std::pair<VkFormat, uint32_t>> vulkan_formats;
std::vector<std::string> vulkan_debug_messages;

/* ----------------------------------------------------------------------------
   Debug callback
   ------------------------------------------------------------------------- */
static VkBool32
vulkan_debug_message_callback(VkDebugUtilsMessageSeverityFlagBitsEXT severity,
                              VkDebugUtilsMessageTypeFlagsEXT type,
                              const VkDebugUtilsMessengerCallbackDataEXT *data,
                              void *user_data) {
  vulkan_debug_messages.push_back(data->pMessage);
  return VK_FALSE;
}

/* ----------------------------------------------------------------------------
   vulkan_get_spirv_entry_point
   ------------------------------------------------------------------------- */
const char *vulkan_get_spirv_entry_point(const uint32_t *words, uint64_t len) {
  if (len < 20)
    return NULL;
  if (len % 4)
    return NULL;
  if (words[0] != 0x07230203)
    return NULL; // SPIR-V magic

  uint64_t offset = 5; // skip header (5 words = 20 bytes)
  uint64_t words_num = len / 4;

  while (offset < words_num) {
    uint32_t word = words[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t size = word >> 16;
    if (size == 0)
      return NULL;

    // OpEntryPoint (0x0F) + ExecutionModel GLCompute (5)
    if (opcode == 0x0F && (offset + size < words_num) &&
        words[offset + 1] == 5) {
      if (size > 3) {
        const char *name = (const char *)&words[offset + 3];
        uint64_t max_namelen = (size - 3) * 4;
        for (uint64_t i = 0; i < max_namelen; i++) {
          if (name[i] == 0)
            return name;
        }
      }
    }
    offset += size;
  }
  return NULL;
}

/* ----------------------------------------------------------------------------
   vulkan_patch_spirv_unknown_uav
   Patches SPIR-V to add NonReadable decoration for BGRA UAVs on Intel.
   ------------------------------------------------------------------------- */
uint32_t *vulkan_patch_spirv_unknown_uav(const uint32_t *words, uint64_t len,
                                         uint32_t binding) {
  if (len < 20)
    return NULL;
  if (len % 4)
    return NULL;
  if (words[0] != 0x07230203)
    return NULL;

  uint64_t offset = 5;
  uint64_t words_num = len / 4;
  bool found = false;
  uint32_t binding_id = 0;
  uint64_t injection_offset = 0;

  // Find OpDecorate Binding for the given binding number
  while (offset < words_num) {
    uint32_t word = words[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t size = word >> 16;
    if (size == 0)
      return NULL;

    if (opcode == 71 && (offset + size < words_num)) { // OpDecorate
      if (size > 3 && words[offset + 2] == 33 && words[offset + 3] == binding) {
        binding_id = words[offset + 1];
        found = true;
        injection_offset = offset + size;
        break;
      }
    }
    offset += size;
  }
  if (!found)
    return NULL;

  // Check if NonReadable is already present
  offset = 5;
  while (offset < words_num) {
    uint32_t word = words[offset];
    uint16_t opcode = word & 0xFFFF;
    uint16_t size = word >> 16;
    if (size == 0)
      return NULL;

    if (opcode == 71 && (offset + size < words_num)) {
      if (size > 2 && words[offset + 2] == 25) {
        return NULL; // already has NonReadable
      }
    }
    offset += size;
  }

  // Inject NonReadable decoration (3 words)
  uint32_t *patched = (uint32_t *)PyMem_Malloc(len + 12);
  if (!patched)
    return NULL;

  memcpy(patched, words, injection_offset * 4);
  patched[injection_offset++] = 3 << 16 | 71; // OpDecorate, 3 words
  patched[injection_offset++] = binding_id;
  patched[injection_offset++] = 25; // NonReadable
  memcpy(patched + injection_offset, words + (injection_offset - 3),
         len - ((injection_offset - 3) * 4));
  return patched;
}

/* ----------------------------------------------------------------------------
   vulkan_create_image
   ------------------------------------------------------------------------- */
VkImage vulkan_create_image(VkDevice device, VkImageType image_type,
                            VkFormat format, const uint32_t width,
                            const uint32_t height, const uint32_t depth,
                            const uint32_t slices, const bool sparse) {
  VkImageCreateInfo info = {VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
  info.imageType = image_type;
  info.format = format;
  info.extent = {width, height, depth};
  info.mipLevels = 1;
  info.arrayLayers = slices;
  info.samples = VK_SAMPLE_COUNT_1_BIT;
  info.tiling = VK_IMAGE_TILING_OPTIMAL;
  info.usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT |
               VK_IMAGE_USAGE_TRANSFER_DST_BIT | VK_IMAGE_USAGE_SAMPLED_BIT |
               VK_IMAGE_USAGE_STORAGE_BIT;
  info.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
  if (sparse) {
    info.flags = VK_IMAGE_CREATE_SPARSE_BINDING_BIT |
                 VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT |
                 VK_IMAGE_CREATE_SPARSE_ALIASED_BIT;
  }

  VkImage image;
  VkResult res = vkCreateImage(device, &info, NULL, &image);
  if (res != VK_SUCCESS)
    return VK_NULL_HANDLE;
  return image;
}

/* ----------------------------------------------------------------------------
   vulkan_texture_set_layout
   ------------------------------------------------------------------------- */
bool vulkan_texture_set_layout(vulkan_Device *py_device, VkImage image,
                               VkImageLayout old_layout,
                               VkImageLayout new_layout,
                               const uint32_t slices) {
  VkCommandBuffer cmd = py_device->command_buffer;
  VkCommandBufferBeginInfo begin = {
      VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
  vkBeginCommandBuffer(cmd, &begin);

  VkImageMemoryBarrier barrier = {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
  barrier.image = image;
  barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
  barrier.subresourceRange.levelCount = 1;
  barrier.subresourceRange.layerCount = slices;
  barrier.oldLayout = old_layout;
  barrier.newLayout = new_layout;
  barrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
  barrier.dstAccessMask =
      VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT;

  vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                       VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 0, NULL, 0,
                       NULL, 1, &barrier);
  vkEndCommandBuffer(cmd);

  VkSubmitInfo submit = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
  submit.commandBufferCount = 1;
  submit.pCommandBuffers = &cmd;

  VkResult res = vkQueueSubmit(py_device->queue, 1, &submit, VK_NULL_HANDLE);
  if (res != VK_SUCCESS)
    return false;

  Py_BEGIN_ALLOW_THREADS;
  vkQueueWaitIdle(py_device->queue);
  Py_END_ALLOW_THREADS;
  return true;
}

/* ----------------------------------------------------------------------------
   vulkan_get_memory_type_index_by_flag
   ------------------------------------------------------------------------- */
uint32_t vulkan_get_memory_type_index_by_flag(
    VkPhysicalDeviceMemoryProperties *mem_props, VkMemoryPropertyFlags flags) {
  for (uint32_t i = 0; i < mem_props->memoryTypeCount; i++) {
    if ((mem_props->memoryTypes[i].propertyFlags & flags) == flags)
      return i;
  }
  return 0;
}

/* ----------------------------------------------------------------------------
   vulkan_instance_check
   Creates Vulkan instance if not already created.
   ------------------------------------------------------------------------- */
PyObject *vulkan_instance_check(void) {
  if (vulkan_instance != VK_NULL_HANDLE)
    Py_RETURN_NONE;

  // Enumerate instance extensions
  uint32_t ext_count;
  vkEnumerateInstanceExtensionProperties(NULL, &ext_count, NULL);
  std::vector<VkExtensionProperties> exts(ext_count);
  vkEnumerateInstanceExtensionProperties(NULL, &ext_count, exts.data());

  std::vector<const char *> enabled_exts;
  bool has_surface = false, has_xlib_surface = false;

  for (auto &e : exts) {
    if (!strcmp(e.extensionName, VK_KHR_SURFACE_EXTENSION_NAME)) {
      enabled_exts.push_back(VK_KHR_SURFACE_EXTENSION_NAME);
      has_surface = true;
    }
    if (!strcmp(e.extensionName, VK_KHR_XLIB_SURFACE_EXTENSION_NAME)) {
      enabled_exts.push_back(VK_KHR_XLIB_SURFACE_EXTENSION_NAME);
      has_xlib_surface = true;
    }
    if (vulkan_debug &&
        !strcmp(e.extensionName, VK_EXT_DEBUG_UTILS_EXTENSION_NAME)) {
      enabled_exts.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
    }
  }

  vulkan_supports_swapchain = has_surface && has_xlib_surface;

  VkApplicationInfo app = {VK_STRUCTURE_TYPE_APPLICATION_INFO};
  app.pApplicationName = "compushady";
  app.apiVersion = VK_API_VERSION_1_1;

  VkInstanceCreateInfo inst = {VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
  inst.pApplicationInfo = &app;
  inst.enabledExtensionCount = (uint32_t)enabled_exts.size();
  inst.ppEnabledExtensionNames = enabled_exts.data();

  VkResult res = vkCreateInstance(&inst, NULL, &vulkan_instance);
  if (res != VK_SUCCESS) {
    PyErr_Format(PyExc_RuntimeError, "Failed to create Vulkan instance: %d",
                 res);
    return NULL;
  }

  // Set up debug messenger if requested
  if (vulkan_debug) {
    PFN_vkCreateDebugUtilsMessengerEXT func =
        (PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(
            vulkan_instance, "vkCreateDebugUtilsMessengerEXT");
    if (func) {
      VkDebugUtilsMessengerCreateInfoEXT dbg = {
          VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};
      dbg.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                            VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
      dbg.messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                        VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                        VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
      dbg.pfnUserCallback = vulkan_debug_message_callback;
      VkDebugUtilsMessengerEXT messenger;
      func(vulkan_instance, &dbg, NULL, &messenger);
    }
  }

  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_enable_debug
   ------------------------------------------------------------------------- */
PyObject *vulkan_enable_debug(PyObject *self, PyObject *args) {
  vulkan_debug = true;
  Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vulkan_get_shader_binary_type
   ------------------------------------------------------------------------- */
PyObject *vulkan_get_shader_binary_type(PyObject *self) {
  // COMPUSHADY_SHADER_BINARY_TYPE_SPIRV = 1
  return PyLong_FromLong(1);
}

/* ----------------------------------------------------------------------------
   compushady_check_descriptors
   ------------------------------------------------------------------------- */
bool compushady_check_descriptors(
    PyTypeObject *res_type, PyObject *py_cbv,
    std::vector<vulkan_Resource *> &cbv, PyObject *py_srv,
    std::vector<vulkan_Resource *> &srv, PyObject *py_uav,
    std::vector<vulkan_Resource *> &uav, PyTypeObject *sampler_type,
    PyObject *py_samplers, std::vector<vulkan_Sampler *> &samplers) {
  auto check_list = [&](PyObject *list, std::vector<vulkan_Resource *> &vec,
                        const char *name) -> bool {
    if (!list || list == Py_None)
      return true;
    if (!PyList_Check(list)) {
      PyErr_Format(PyExc_TypeError, "%s must be a list", name);
      return false;
    }
    Py_ssize_t size = PyList_Size(list);
    for (Py_ssize_t i = 0; i < size; i++) {
      PyObject *item = PyList_GetItem(list, i);
      if (!PyObject_TypeCheck(item, res_type)) {
        PyErr_Format(PyExc_TypeError, "%s[%zd] is not a Resource", name, i);
        return false;
      }
      vec.push_back((vulkan_Resource *)item);
    }
    return true;
  };

  auto check_samplers = [&](PyObject *list,
                            std::vector<vulkan_Sampler *> &vec) -> bool {
    if (!list || list == Py_None)
      return true;
    if (!PyList_Check(list)) {
      PyErr_Format(PyExc_TypeError, "samplers must be a list");
      return false;
    }
    Py_ssize_t size = PyList_Size(list);
    for (Py_ssize_t i = 0; i < size; i++) {
      PyObject *item = PyList_GetItem(list, i);
      if (!PyObject_TypeCheck(item, sampler_type)) {
        PyErr_Format(PyExc_TypeError, "samplers[%zd] is not a Sampler", i);
        return false;
      }
      vec.push_back((vulkan_Sampler *)item);
    }
    return true;
  };

  if (!check_list(py_cbv, cbv, "cbv"))
    return false;
  if (!check_list(py_srv, srv, "srv"))
    return false;
  if (!check_list(py_uav, uav, "uav"))
    return false;
  if (!check_samplers(py_samplers, samplers))
    return false;
  return true;
}