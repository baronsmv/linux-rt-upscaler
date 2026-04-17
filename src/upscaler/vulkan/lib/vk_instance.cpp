#include "vk_instance.h"
#include <cstring>
#include <xcb/xcb.h>
#include <vulkan/vulkan_xcb.h>
#include <vulkan/vulkan_wayland.h>

/* ----------------------------------------------------------------------------
   Global state definitions
   ------------------------------------------------------------------------- */
VkInstance vk_instance = VK_NULL_HANDLE;
bool vk_supports_swapchain = false;
bool vk_debug_enabled = false;
std::unordered_map<uint32_t, std::pair<VkFormat, uint32_t>> vk_format_map;
std::vector<std::string> vk_debug_messages;

/* ----------------------------------------------------------------------------
   Debug callback
   ------------------------------------------------------------------------- */
static VKAPI_ATTR VkBool32 VKAPI_CALL vk_debug_callback(
    VkDebugUtilsMessageSeverityFlagBitsEXT severity,
    VkDebugUtilsMessageTypeFlagsEXT type,
    const VkDebugUtilsMessengerCallbackDataEXT *data,
    void *user_data) {
    vk_debug_messages.push_back(data->pMessage);
    return VK_FALSE;
}

/* ----------------------------------------------------------------------------
   vk_instance_ensure - creates the global Vulkan instance (Vulkan 1.2)
   ------------------------------------------------------------------------- */
bool vk_instance_ensure(void) {
    if (vk_instance != VK_NULL_HANDLE)
        return true;

    // Enumerate instance extensions
    uint32_t ext_count;
    vkEnumerateInstanceExtensionProperties(NULL, &ext_count, NULL);
    std::vector<VkExtensionProperties> exts(ext_count);
    vkEnumerateInstanceExtensionProperties(NULL, &ext_count, exts.data());

    std::vector<const char *> enabled_exts;
    bool has_surface = false, has_xcb_surface = false, has_wayland_surface = false;

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

    vk_supports_swapchain = has_surface && (has_xcb_surface || has_wayland_surface);

    VkApplicationInfo app_info = { VK_STRUCTURE_TYPE_APPLICATION_INFO };
    app_info.pApplicationName = "Vulkan Python Backend";
    app_info.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
    app_info.pEngineName = "vk_backend";
    app_info.engineVersion = VK_MAKE_VERSION(1, 0, 0);
    app_info.apiVersion = VK_API_VERSION_1_2;   // Request Vulkan 1.2

    VkInstanceCreateInfo inst_info = { VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO };
    inst_info.pApplicationInfo = &app_info;
    inst_info.enabledExtensionCount = (uint32_t)enabled_exts.size();
    inst_info.ppEnabledExtensionNames = enabled_exts.data();

    // Validation layers (optional)
    const char *validation_layers[] = { "VK_LAYER_KHRONOS_validation" };
    if (vk_debug_enabled) {
        inst_info.enabledLayerCount = 1;
        inst_info.ppEnabledLayerNames = validation_layers;
    }

    VkResult res = vkCreateInstance(&inst_info, NULL, &vk_instance);
    if (res != VK_SUCCESS) {
        PyErr_Format(PyExc_RuntimeError, "Failed to create Vulkan instance (error %d)", res);
        return false;
    }

    // Set up debug messenger if requested
    if (vk_debug_enabled) {
        PFN_vkCreateDebugUtilsMessengerEXT func =
            (PFN_vkCreateDebugUtilsMessengerEXT)vkGetInstanceProcAddr(
                vk_instance, "vkCreateDebugUtilsMessengerEXT");
        if (func) {
            VkDebugUtilsMessengerCreateInfoEXT dbg = {
                VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT
            };
            dbg.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                                  VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT;
            dbg.messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                              VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                              VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
            dbg.pfnUserCallback = vk_debug_callback;
            VkDebugUtilsMessengerEXT messenger;
            func(vk_instance, &dbg, NULL, &messenger);
        }
    }

    return true;
}

/* ----------------------------------------------------------------------------
   vk_enable_debug_mode
   ------------------------------------------------------------------------- */
PyObject *vk_enable_debug_mode(PyObject *self, PyObject *args) {
    vk_debug_enabled = true;
    Py_RETURN_NONE;
}

/* ----------------------------------------------------------------------------
   vk_get_shader_binary_type
   ------------------------------------------------------------------------- */
PyObject *vk_get_shader_binary_type(PyObject *self) {
    return PyLong_FromLong(1);   // SHADER_BINARY_TYPE_SPIRV = 1
}

/* ----------------------------------------------------------------------------
   vk_get_discovered_devices
   ------------------------------------------------------------------------- */
PyObject *vk_get_discovered_devices(PyObject *self, PyObject *args) {
    if (!vk_instance_ensure())
        return NULL;

    uint32_t count = 0;
    vkEnumeratePhysicalDevices(vk_instance, &count, NULL);
    if (count == 0) {
        return PyList_New(0);
    }

    VkPhysicalDevice *devices = (VkPhysicalDevice *)PyMem_Malloc(count * sizeof(VkPhysicalDevice));
    vkEnumeratePhysicalDevices(vk_instance, &count, devices);

    PyObject *list = PyList_New(count);
    for (uint32_t i = 0; i < count; i++) {
        vk_Device *dev = PyObject_New(vk_Device, &vk_Device_Type);
        if (!dev) {
            Py_DECREF(list);
            PyMem_Free(devices);
            return PyErr_NoMemory();
        }
        VK_CLEAR_OBJECT(dev);
        dev->physical_device = devices[i];

        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(devices[i], &props);
        dev->name = strdup(props.deviceName);
        dev->vendor_id = props.vendorID;
        dev->device_id = props.deviceID;
        dev->is_discrete = (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU);
        dev->is_hardware = (props.deviceType != VK_PHYSICAL_DEVICE_TYPE_CPU &&
                            props.deviceType != VK_PHYSICAL_DEVICE_TYPE_OTHER);

        vkGetPhysicalDeviceMemoryProperties(devices[i], &dev->mem_props);
        for (uint32_t j = 0; j < dev->mem_props.memoryHeapCount; j++) {
            if (dev->mem_props.memoryHeaps[j].flags & VK_MEMORY_HEAP_DEVICE_LOCAL_BIT)
                dev->dedicated_video_memory += dev->mem_props.memoryHeaps[j].size;
            else
                dev->shared_system_memory += dev->mem_props.memoryHeaps[j].size;
        }

        PyList_SetItem(list, i, (PyObject *)dev);
    }
    PyMem_Free(devices);
    return list;
}