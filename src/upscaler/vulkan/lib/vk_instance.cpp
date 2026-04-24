/**
 * @file vk_instance.cpp
 * @brief Global Vulkan instance, debug messenger, and device enumeration.
 *
 * This module manages the singleton `VkInstance` (Vulkan 1.2), global state
 * such as debug settings and the format map, and provides the functions to
 * enumerate physical devices and enable validation layers.
 *
 * Global state:
 *   - `vk_instance`          - the shared VkInstance (created on first use).
 *   - `vk_supports_swapchain`- whether surface + (XCB or Wayland) extensions
 *                              are available.
 *   - `vk_debug_enabled`     - flag controlling validation layer loading.
 *   - `vk_format_map`        - maps Python pixel-format constants to
 *                              (VkFormat, bytes-per-pixel).
 *   - `vk_debug_messages`    - collected debug callbacks, returned by
 *                              `Device.get_debug_messages()`.
 *
 * Thread-safety:
 *   - The debug callback is **intended for single-threaded use**. If the
 *     application becomes multi-threaded, access to `vk_debug_messages` must
 *     be protected by a mutex.
 *   - All other global variables are initialised once, before any device
 *     creation, and never modified afterwards (read-only from the Python
 *     side).
 *
 * The XCB surface extension is included here because the instance must
 * advertise it; the actual surface creation happens in `vk_swapchain.cpp`.
 */

// clang-format off
#include "vk_instance.h"
#include "vk_utils.h"
#include <cstring>
#include <vector>
#include <xcb/xcb.h>              // Must come before vulkan_xcb.h
#include <vulkan/vulkan_xcb.h>
#include <vulkan/vulkan_wayland.h>
// clang-format on

// =============================================================================
//  Global state
// =============================================================================

VkInstance vk_instance = VK_NULL_HANDLE;
bool vk_supports_swapchain = false;
bool vk_debug_enabled = false;
std::unordered_map<uint32_t, std::pair<VkFormat, uint32_t>> vk_format_map;
std::vector<std::string> vk_debug_messages;

// =============================================================================
//  Debug callback (VK_EXT_debug_utils)
// =============================================================================

/**
 * Vulkan debug callback - stores all messages for later retrieval.
 *
 * @param severity  message severity flags (warning, error, info, verbose).
 * @param type      message type (general, validation, performance).
 * @param data      callback data including the message string.
 * @param user_data user-provided pointer (unused).
 * @return VK_FALSE (the application should not abort).
 *
 * Note: This function is called from arbitrary threads by the Vulkan loader.
 * In a single-threaded application this is safe; if the architecture changes,
 * a mutex is required around `vk_debug_messages`.
 */
static VKAPI_ATTR VkBool32 VKAPI_CALL vk_debug_callback(
    VkDebugUtilsMessageSeverityFlagBitsEXT /*severity*/,
    VkDebugUtilsMessageTypeFlagsEXT /*type*/,
    const VkDebugUtilsMessengerCallbackDataEXT *data, void * /*user_data*/) {
  vk_debug_messages.push_back(data->pMessage);
  return VK_FALSE;
}

// =============================================================================
//  Instance creation (singleton)
// =============================================================================

/**
 * Create the global VkInstance (Vulkan 1.2) if it does not already exist.
 * Loads required extensions (surface, XCB/Wayland, debug if enabled) and
 * optionally enables validation layers.
 *
 * The instance is never destroyed - it lives for the lifetime of the process.
 *
 * @return true on success, false with a Python exception set.
 */
bool vk_instance_ensure(void) {
  if (vk_instance != VK_NULL_HANDLE)
    return true;

  // ---- Enumerate available instance extensions ----
  uint32_t ext_count;
  vkEnumerateInstanceExtensionProperties(nullptr, &ext_count, nullptr);
  std::vector<VkExtensionProperties> exts(ext_count);
  vkEnumerateInstanceExtensionProperties(nullptr, &ext_count, exts.data());

  std::vector<const char *> enabled_exts;
  bool has_surface = false, has_xcb_surface = false,
       has_wayland_surface = false;

  for (const auto &e : exts) {
    if (strcmp(e.extensionName, VK_KHR_SURFACE_EXTENSION_NAME) == 0) {
      enabled_exts.push_back(VK_KHR_SURFACE_EXTENSION_NAME);
      has_surface = true;
    }
    if (strcmp(e.extensionName, VK_KHR_XCB_SURFACE_EXTENSION_NAME) == 0) {
      enabled_exts.push_back(VK_KHR_XCB_SURFACE_EXTENSION_NAME);
      has_xcb_surface = true;
    }
    if (strcmp(e.extensionName, VK_KHR_WAYLAND_SURFACE_EXTENSION_NAME) == 0) {
      enabled_exts.push_back(VK_KHR_WAYLAND_SURFACE_EXTENSION_NAME);
      has_wayland_surface = true;
    }
    if (vk_debug_enabled &&
        strcmp(e.extensionName, VK_EXT_DEBUG_UTILS_EXTENSION_NAME) == 0) {
      enabled_exts.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
    }
  }

  vk_supports_swapchain =
      has_surface && (has_xcb_surface || has_wayland_surface);

  // ---- Application info ----
  VkApplicationInfo app_info = {VK_STRUCTURE_TYPE_APPLICATION_INFO};
  app_info.pApplicationName = "Vulkan Python Backend";
  app_info.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
  app_info.pEngineName = "vk_backend";
  app_info.engineVersion = VK_MAKE_VERSION(1, 0, 0);
  app_info.apiVersion = VK_API_VERSION_1_2;

  // ---- Instance create info ----
  VkInstanceCreateInfo inst_info = {VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
  inst_info.pApplicationInfo = &app_info;
  inst_info.enabledExtensionCount = static_cast<uint32_t>(enabled_exts.size());
  inst_info.ppEnabledExtensionNames = enabled_exts.data();

  // Validation layers (only if debug is enabled)
  const char *validation_layers[] = {"VK_LAYER_KHRONOS_validation"};
  if (vk_debug_enabled) {
    inst_info.enabledLayerCount = 1;
    inst_info.ppEnabledLayerNames = validation_layers;
  }

  VkResult res = vkCreateInstance(&inst_info, nullptr, &vk_instance);
  VK_CHECK_OR_RETURN_FALSE(res, PyExc_RuntimeError,
                           "Failed to create Vulkan instance");

  // ---- Debug messenger (attach after instance creation) ----
  if (vk_debug_enabled) {
    PFN_vkCreateDebugUtilsMessengerEXT func =
        (PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(
            vk_instance, "vkCreateDebugUtilsMessengerEXT");
    if (func) {
      VkDebugUtilsMessengerCreateInfoEXT dbg = {
          VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};
      dbg.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                            VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
      dbg.messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                        VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                        VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
      dbg.pfnUserCallback = vk_debug_callback;
      VkDebugUtilsMessengerEXT messenger;
      func(vk_instance, &dbg, nullptr, &messenger);
      // The messenger is intentionally not stored; it will be destroyed
      // when the instance is destroyed (which never happens in this
      // application). If clean-up becomes necessary, the handle should
      // be saved and destroyed before the instance.
    }
  }

  return true;
}

// =============================================================================
//  Python-facing module functions
// =============================================================================

/**
 * Enable Vulkan validation layers and debug callbacks.
 * Must be called before any device is created.
 */
PyObject *vk_enable_debug_mode(PyObject * /*self*/, PyObject * /*args*/) {
  vk_debug_enabled = true;
  Py_RETURN_NONE;
}

/**
 * Return the shader binary type supported by this wrapper.
 * Always returns 1 (corresponding to `SHADER_BINARY_TYPE_SPIRV`).
 */
PyObject *vk_get_shader_binary_type(PyObject * /*self*/) {
  return PyLong_FromLong(1); // SHADER_BINARY_TYPE_SPIRV
}

/**
 * Enumerate all Vulkan physical devices in the system.
 *
 * Each device is returned as a `vk.Device` object with its name, memory
 * sizes, and capability flags pre-populated. The device list is cached
 * by the Python `VulkanContext` and will not change after the first call.
 *
 * @return A Python list of `vk.Device` objects, or NULL on error.
 */
PyObject *vk_get_discovered_devices(PyObject * /*self*/, PyObject * /*args*/) {
  if (!vk_instance_ensure())
    return nullptr;

  uint32_t count = 0;
  vkEnumeratePhysicalDevices(vk_instance, &count, nullptr);
  if (count == 0)
    return PyList_New(0); // empty list

  std::vector<VkPhysicalDevice> devices(count);
  vkEnumeratePhysicalDevices(vk_instance, &count, devices.data());

  PyObject *list = PyList_New(count);
  if (!list)
    return PyErr_NoMemory();

  for (uint32_t i = 0; i < count; i++) {
    vk_Device *dev = PyObject_New(vk_Device, &vk_Device_Type);
    if (!dev) {
      Py_DECREF(list);
      return PyErr_NoMemory();
    }
    VK_CLEAR_OBJECT(dev);
    dev->physical_device = devices[i];

    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(devices[i], &props);
    dev->name = strdup(props.deviceName);
    if (!dev->name) {
      Py_DECREF(dev);
      Py_DECREF(list);
      return PyErr_NoMemory();
    }
    dev->vendor_id = props.vendorID;
    dev->device_id = props.deviceID;
    dev->is_discrete =
        (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU);
    dev->is_hardware = (props.deviceType != VK_PHYSICAL_DEVICE_TYPE_CPU &&
                        props.deviceType != VK_PHYSICAL_DEVICE_TYPE_OTHER);

    // Calculate memory totals from heap information
    vkGetPhysicalDeviceMemoryProperties(devices[i], &dev->mem_props);
    for (uint32_t j = 0; j < dev->mem_props.memoryHeapCount; j++) {
      if (dev->mem_props.memoryHeaps[j].flags & VK_MEMORY_HEAP_DEVICE_LOCAL_BIT)
        dev->dedicated_video_memory += dev->mem_props.memoryHeaps[j].size;
      else
        dev->shared_system_memory += dev->mem_props.memoryHeaps[j].size;
    }

    PyList_SetItem(list, i, reinterpret_cast<PyObject *>(dev));
  }

  return list;
}