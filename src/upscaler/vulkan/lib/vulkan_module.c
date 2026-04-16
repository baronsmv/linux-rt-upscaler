/**
 * @file vulkan_module.c
 * @brief Vulkan backend module initialization for Python.
 *
 * This module exposes the Vulkan backend with functions:
 *   - get_discovered_devices()
 *   - enable_debug()
 *   - get_shader_binary_type()
 * and registers all Vulkan object types.
 */

#include "vulkan_module.h"
#include "vulkan_compute.h"
#include "vulkan_device.h"
#include "vulkan_heap.h"
#include "vulkan_resource.h"
#include "vulkan_sampler.h"
#include "vulkan_swapchain.h"
#include "vulkan_types.h"
#include "vulkan_utils.h"
#include <X11/Xlib.h>
#include <stdlib.h>
#include <string.h>
#include <vulkan/vulkan_xlib.h>

/* -------------------------------------------------------------------------
   Global Vulkan instance
   ------------------------------------------------------------------------- */
VkInstance g_vulkan_instance = VK_NULL_HANDLE;
static VkDebugUtilsMessengerEXT g_debug_messenger = VK_NULL_HANDLE;
static bool g_debug_enabled = false;

/* -------------------------------------------------------------------------
   Error objects
   ------------------------------------------------------------------------- */
PyObject *VkComp_Texture2DError = NULL;
PyObject *VkComp_BufferError = NULL;
PyObject *VkComp_ComputeError = NULL;
PyObject *VkComp_SwapchainError = NULL;
PyObject *VkComp_HeapError = NULL;
PyObject *VkComp_SamplerError = NULL;
PyObject *VkComp_Texture1DError = NULL;
PyObject *VkComp_Texture3DError = NULL;

/* -------------------------------------------------------------------------
   Format table
   ------------------------------------------------------------------------- */
VkComp_FormatInfo g_vulkan_format_table[256] = {{VK_FORMAT_UNDEFINED, 0}};

/* -------------------------------------------------------------------------
   Debug message storage
   ------------------------------------------------------------------------- */
static PyObject *g_debug_message_list = NULL;

/* -------------------------------------------------------------------------
   Debug message
   ------------------------------------------------------------------------- */
static void add_debug_message(const char *msg) {
  if (!g_debug_message_list) {
    g_debug_message_list = PyList_New(0);
    if (!g_debug_message_list)
      return;
  }
  PyObject *py_msg = PyUnicode_FromString(msg);
  if (py_msg) {
    PyList_Append(g_debug_message_list, py_msg);
    Py_DECREF(py_msg);
  }
}

/* -------------------------------------------------------------------------
   Debug callback
   ------------------------------------------------------------------------- */
static VKAPI_ATTR VkBool32 VKAPI_CALL
debug_callback(VkDebugUtilsMessageSeverityFlagBitsEXT severity,
               VkDebugUtilsMessageTypeFlagsEXT type,
               const VkDebugUtilsMessengerCallbackDataEXT *pCallbackData,
               void *pUserData) {
  (void)severity;
  (void)type;
  (void)pUserData;
  add_debug_message(pCallbackData->pMessage);
  return VK_FALSE;
}

static VkResult create_debug_messenger(VkInstance instance) {
  VkDebugUtilsMessengerCreateInfoEXT create_info = {
      .sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT,
      .messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT |
                         VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT |
                         VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                         VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
      .messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                     VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                     VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
      .pfnUserCallback = debug_callback,
  };
  PFN_vkCreateDebugUtilsMessengerEXT func =
      (PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(
          instance, "vkCreateDebugUtilsMessengerEXT");
  if (!func)
    return VK_ERROR_EXTENSION_NOT_PRESENT;
  return func(instance, &create_info, NULL, &g_debug_messenger);
}

static bool init_vulkan_instance(void) {
  if (g_vulkan_instance != VK_NULL_HANDLE)
    return true;

  VkApplicationInfo app_info = {
      .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
      .pApplicationName = "VkCompute Python Backend",
      .applicationVersion = VK_MAKE_VERSION(1, 0, 0),
      .pEngineName = "VkCompute",
      .engineVersion = VK_MAKE_VERSION(1, 0, 0),
      .apiVersion = VK_API_VERSION_1_3,
  };

  const char *extensions[] = {
      VK_KHR_SURFACE_EXTENSION_NAME,
      VK_KHR_XLIB_SURFACE_EXTENSION_NAME,
  };
  uint32_t ext_count = 2;

  const char *layers[] = {"VK_LAYER_KHRONOS_validation"};
  uint32_t layer_count = g_debug_enabled ? 1 : 0;

  VkInstanceCreateInfo create_info = {
      .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
      .pApplicationInfo = &app_info,
      .enabledExtensionCount = ext_count,
      .ppEnabledExtensionNames = extensions,
      .enabledLayerCount = layer_count,
      .ppEnabledLayerNames = layers,
  };

  VkDebugUtilsMessengerCreateInfoEXT debug_create_info = {
      .sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT,
      .messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT |
                         VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT |
                         VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                         VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
      .messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                     VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                     VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
      .pfnUserCallback = debug_callback,
  };
  if (g_debug_enabled) {
    create_info.pNext = &debug_create_info;
  }

  VkResult res = vkCreateInstance(&create_info, NULL, &g_vulkan_instance);
  if (res != VK_SUCCESS)
    return false;

  if (g_debug_enabled) {
    create_debug_messenger(g_vulkan_instance);
  }
  return true;
}

/* -------------------------------------------------------------------------
   Retrieve and clear debug messages
   ------------------------------------------------------------------------- */
PyObject *vulkan_get_and_clear_debug_messages(void) {
  PyObject *result = g_debug_message_list;
  if (!result) {
    result = PyList_New(0);
  } else {
    g_debug_message_list = NULL;
  }
  return result;
}

/* -------------------------------------------------------------------------
   Python: get_discovered_devices()
   ------------------------------------------------------------------------- */
static PyObject *vulkan_get_discovered_devices(PyObject *self, PyObject *args) {
  if (!init_vulkan_instance()) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to create Vulkan instance");
    return NULL;
  }

  uint32_t count = 0;
  vkEnumeratePhysicalDevices(g_vulkan_instance, &count, NULL);
  if (count == 0)
    return PyList_New(0);

  VkPhysicalDevice *devices = PyMem_Malloc(count * sizeof(VkPhysicalDevice));
  if (!devices)
    return PyErr_NoMemory();
  vkEnumeratePhysicalDevices(g_vulkan_instance, &count, devices);

  PyObject *list = PyList_New(count);
  for (uint32_t i = 0; i < count; i++) {
    VkComp_Device *dev = PyObject_New(VkComp_Device, &VkComp_Device_Type);
    if (!dev) {
      Py_DECREF(list);
      PyMem_Free(devices);
      return PyErr_NoMemory();
    }
    VKCOMP_CLEAR_OBJECT(dev);
    dev->physical_device = devices[i];

    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(devices[i], &props);
    dev->name = PyUnicode_FromString(props.deviceName);
    dev->is_discrete =
        (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU);
    dev->is_hardware =
        (props.deviceType != VK_PHYSICAL_DEVICE_TYPE_CPU &&
         props.deviceType != VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU &&
         props.deviceType != VK_PHYSICAL_DEVICE_TYPE_OTHER);
    dev->vendor_id = props.vendorID;
    dev->device_id = props.deviceID;
    dev->supports_swapchain = true; // X11 assumed

    vkGetPhysicalDeviceMemoryProperties(devices[i], &dev->mem_props);
    for (uint32_t j = 0; j < dev->mem_props.memoryHeapCount; j++) {
      if (dev->mem_props.memoryHeaps[j].flags &
          VK_MEMORY_HEAP_DEVICE_LOCAL_BIT) {
        dev->dedicated_video_memory += dev->mem_props.memoryHeaps[j].size;
      } else {
        dev->shared_system_memory += dev->mem_props.memoryHeaps[j].size;
      }
    }

    PyList_SetItem(list, i, (PyObject *)dev);
  }
  PyMem_Free(devices);
  return list;
}

/* -------------------------------------------------------------------------
   Python: enable_debug()
   ------------------------------------------------------------------------- */
static PyObject *vulkan_enable_debug(PyObject *self, PyObject *args) {
  g_debug_enabled = true;
  Py_RETURN_NONE;
}

/* -------------------------------------------------------------------------
   Python: get_shader_binary_type()
   ------------------------------------------------------------------------- */
static PyObject *vulkan_get_shader_binary_type(PyObject *self) {
  return PyLong_FromLong(1); // SPIR-V
}

/* -------------------------------------------------------------------------
   Module method table
   ------------------------------------------------------------------------- */
static PyMethodDef vulkan_methods[] = {
    {"get_discovered_devices", vulkan_get_discovered_devices, METH_NOARGS,
     "Return a list of available Vulkan devices."},
    {"enable_debug", vulkan_enable_debug, METH_NOARGS,
     "Enable Vulkan validation layers and debug output."},
    {"get_shader_binary_type", (PyCFunction)vulkan_get_shader_binary_type,
     METH_NOARGS,
     "Return the shader binary type supported by this backend (SPIR-V = 1)."},
    {NULL, NULL, 0, NULL}};

/* -------------------------------------------------------------------------
   Module definition
   ------------------------------------------------------------------------- */
static struct PyModuleDef vulkan_module = {PyModuleDef_HEAD_INIT, "vulkan",
                                           NULL, -1, vulkan_methods};

/* -------------------------------------------------------------------------
   Module initialization
   ------------------------------------------------------------------------- */
PyMODINIT_FUNC PyInit_vulkan(void) {
  PyObject *m = PyModule_Create(&vulkan_module);
  if (!m)
    return NULL;

/* Create error objects */
#define ADD_ERROR(name, base)                                                  \
  VkComp_##name = PyErr_NewException("vulkan." #name, base, NULL);             \
  PyModule_AddObject(m, #name, VkComp_##name)

  ADD_ERROR(Texture2DError, NULL);
  ADD_ERROR(BufferError, NULL);
  ADD_ERROR(ComputeError, NULL);
  ADD_ERROR(SwapchainError, NULL);
  ADD_ERROR(HeapError, NULL);
  ADD_ERROR(SamplerError, NULL);
  ADD_ERROR(Texture1DError, NULL);
  ADD_ERROR(Texture3DError, NULL);
#undef ADD_ERROR

/* Initialize format table – matches Python pixel format constants */
#define ADD_FORMAT(idx, vk_fmt, bpp)                                           \
  g_vulkan_format_table[idx] = (VkComp_FormatInfo) { vk_fmt, bpp }

  ADD_FORMAT(2, VK_FORMAT_R32G32B32A32_SFLOAT, 16);
  ADD_FORMAT(3, VK_FORMAT_R32G32B32A32_UINT, 16);
  ADD_FORMAT(4, VK_FORMAT_R32G32B32A32_SINT, 16);
  ADD_FORMAT(6, VK_FORMAT_R32G32B32_SFLOAT, 12);
  ADD_FORMAT(7, VK_FORMAT_R32G32B32_UINT, 12);
  ADD_FORMAT(8, VK_FORMAT_R32G32B32_SINT, 12);
  ADD_FORMAT(10, VK_FORMAT_R16G16B16A16_SFLOAT, 8);
  ADD_FORMAT(11, VK_FORMAT_R16G16B16A16_UNORM, 8);
  ADD_FORMAT(12, VK_FORMAT_R16G16B16A16_UINT, 8);
  ADD_FORMAT(13, VK_FORMAT_R16G16B16A16_SNORM, 8);
  ADD_FORMAT(14, VK_FORMAT_R16G16B16A16_SINT, 8);
  ADD_FORMAT(16, VK_FORMAT_R32G32_SFLOAT, 8);
  ADD_FORMAT(17, VK_FORMAT_R32G32_UINT, 8);
  ADD_FORMAT(18, VK_FORMAT_R32G32_SINT, 8);
  ADD_FORMAT(24, VK_FORMAT_A2B10G10R10_UNORM_PACK32, 4);
  ADD_FORMAT(25, VK_FORMAT_A2B10G10R10_UINT_PACK32, 4);
  ADD_FORMAT(28, VK_FORMAT_R8G8B8A8_UNORM, 4);
  ADD_FORMAT(29, VK_FORMAT_R8G8B8A8_SRGB, 4);
  ADD_FORMAT(30, VK_FORMAT_R8G8B8A8_UINT, 4);
  ADD_FORMAT(31, VK_FORMAT_R8G8B8A8_SNORM, 4);
  ADD_FORMAT(32, VK_FORMAT_R8G8B8A8_SINT, 4);
  ADD_FORMAT(34, VK_FORMAT_R16G16_SFLOAT, 4);
  ADD_FORMAT(35, VK_FORMAT_R16G16_UNORM, 4);
  ADD_FORMAT(36, VK_FORMAT_R16G16_UINT, 4);
  ADD_FORMAT(37, VK_FORMAT_R16G16_SNORM, 4);
  ADD_FORMAT(38, VK_FORMAT_R16G16_SINT, 4);
  ADD_FORMAT(41, VK_FORMAT_R32_SFLOAT, 4);
  ADD_FORMAT(42, VK_FORMAT_R32_UINT, 4);
  ADD_FORMAT(43, VK_FORMAT_R32_SINT, 4);
  ADD_FORMAT(49, VK_FORMAT_R8G8_UNORM, 2);
  ADD_FORMAT(50, VK_FORMAT_R8G8_UINT, 2);
  ADD_FORMAT(51, VK_FORMAT_R8G8_SNORM, 2);
  ADD_FORMAT(52, VK_FORMAT_R8G8_SINT, 2);
  ADD_FORMAT(54, VK_FORMAT_R16_SFLOAT, 2);
  ADD_FORMAT(55, VK_FORMAT_R16_UNORM, 2);
  ADD_FORMAT(57, VK_FORMAT_R16_UINT, 2);
  ADD_FORMAT(58, VK_FORMAT_R16_SNORM, 2);
  ADD_FORMAT(59, VK_FORMAT_R16_SINT, 2);
  ADD_FORMAT(61, VK_FORMAT_R8_UNORM, 1);
  ADD_FORMAT(62, VK_FORMAT_R8_UINT, 1);
  ADD_FORMAT(63, VK_FORMAT_R8_SNORM, 1);
  ADD_FORMAT(64, VK_FORMAT_R8_SINT, 1);
  ADD_FORMAT(87, VK_FORMAT_B8G8R8A8_UNORM, 4);
  ADD_FORMAT(91, VK_FORMAT_B8G8R8A8_SRGB, 4);
#undef ADD_FORMAT

  /* Register all Python types */
  if (PyType_Ready(&VkComp_Device_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Device", (PyObject *)&VkComp_Device_Type);

  if (PyType_Ready(&VkComp_Heap_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Heap", (PyObject *)&VkComp_Heap_Type);

  if (PyType_Ready(&VkComp_Resource_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Resource", (PyObject *)&VkComp_Resource_Type);

  if (PyType_Ready(&VkComp_Sampler_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Sampler", (PyObject *)&VkComp_Sampler_Type);

  if (PyType_Ready(&VkComp_Compute_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Compute", (PyObject *)&VkComp_Compute_Type);

  if (PyType_Ready(&VkComp_Swapchain_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Swapchain", (PyObject *)&VkComp_Swapchain_Type);

  return m;
}