#include "vk_utils.h"
#include <cstring>

/* ----------------------------------------------------------------------------
   Memory type selection
   ------------------------------------------------------------------------- */
uint32_t vk_find_memory_type_index(VkPhysicalDeviceMemoryProperties *props,
                                   VkMemoryPropertyFlags flags) {
    for (uint32_t i = 0; i < props->memoryTypeCount; i++) {
        if ((props->memoryTypes[i].propertyFlags & flags) == flags)
            return i;
    }
    return 0;
}

/* ----------------------------------------------------------------------------
   Command buffer execution
   ------------------------------------------------------------------------- */
VkResult vk_execute_command_buffer(vk_Device *dev, VkCommandBuffer cmd,
                                   VkFence fence,
                                   uint32_t wait_semaphore_count,
                                   VkSemaphore *wait_semaphores,
                                   VkPipelineStageFlags *wait_stages,
                                   uint32_t signal_semaphore_count,
                                   VkSemaphore *signal_semaphores) {
    VkSubmitInfo submit = { VK_STRUCTURE_TYPE_SUBMIT_INFO };
    submit.commandBufferCount = 1;
    submit.pCommandBuffers = &cmd;
    submit.waitSemaphoreCount = wait_semaphore_count;
    submit.pWaitSemaphores = wait_semaphores;
    submit.pWaitDstStageMask = wait_stages;
    submit.signalSemaphoreCount = signal_semaphore_count;
    submit.pSignalSemaphores = signal_semaphores;

    VkResult res = vkQueueSubmit(dev->queue, 1, &submit, fence);
    if (res != VK_SUCCESS)
        return res;

    if (fence != VK_NULL_HANDLE) {
        Py_BEGIN_ALLOW_THREADS;
        vkWaitForFences(dev->device, 1, &fence, VK_TRUE, UINT64_MAX);
        vkResetFences(dev->device, 1, &fence);
        Py_END_ALLOW_THREADS;
    }
    return VK_SUCCESS;
}

/* ----------------------------------------------------------------------------
   Image barrier helper
   ------------------------------------------------------------------------- */
void vk_image_barrier(VkCommandBuffer cmd, VkImage image,
                      VkImageLayout old_layout, VkImageLayout new_layout,
                      VkPipelineStageFlags src_stage, VkPipelineStageFlags dst_stage,
                      VkAccessFlags src_access, VkAccessFlags dst_access,
                      uint32_t base_mip, uint32_t mip_count,
                      uint32_t base_layer, uint32_t layer_count) {
    VkImageMemoryBarrier barrier = { VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER };
    barrier.srcAccessMask = src_access;
    barrier.dstAccessMask = dst_access;
    barrier.oldLayout = old_layout;
    barrier.newLayout = new_layout;
    barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
    barrier.image = image;
    barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
    barrier.subresourceRange.baseMipLevel = base_mip;
    barrier.subresourceRange.levelCount = mip_count;
    barrier.subresourceRange.baseArrayLayer = base_layer;
    barrier.subresourceRange.layerCount = layer_count;

    vkCmdPipelineBarrier(cmd, src_stage, dst_stage, 0, 0, NULL, 0, NULL, 1, &barrier);
}

/* ----------------------------------------------------------------------------
   Staging buffer acquisition
   ------------------------------------------------------------------------- */
bool vk_staging_buffer_acquire(vk_Device *dev, VkDeviceSize size,
                               VkBuffer *out_buffer, VkDeviceMemory *out_memory,
                               void **out_mapped, bool *used_pool) {
    // Try from pool first
    if (dev->staging_pool.count > 0 &&
        size <= dev->staging_pool.sizes[dev->staging_pool.next]) {
        int idx = dev->staging_pool.next;
        dev->staging_pool.next = (idx + 1) % dev->staging_pool.count;
        *out_buffer = dev->staging_pool.buffers[idx];
        *out_memory = dev->staging_pool.memories[idx];
        *used_pool = true;
    } else {
        // Allocate new
        VkBufferCreateInfo binfo = { VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO };
        binfo.size = size;
        binfo.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;
        if (vkCreateBuffer(dev->device, &binfo, NULL, out_buffer) != VK_SUCCESS)
            return false;

        VkMemoryRequirements req;
        vkGetBufferMemoryRequirements(dev->device, *out_buffer, &req);
        VkMemoryAllocateInfo alloc = { VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO };
        alloc.allocationSize = req.size;
        alloc.memoryTypeIndex = vk_find_memory_type_index(&dev->mem_props,
            VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
        if (vkAllocateMemory(dev->device, &alloc, NULL, out_memory) != VK_SUCCESS) {
            vkDestroyBuffer(dev->device, *out_buffer, NULL);
            return false;
        }
        vkBindBufferMemory(dev->device, *out_buffer, *out_memory, 0);
        *used_pool = false;
    }

    if (vkMapMemory(dev->device, *out_memory, 0, size, 0, out_mapped) != VK_SUCCESS) {
        if (!*used_pool) {
            vkDestroyBuffer(dev->device, *out_buffer, NULL);
            vkFreeMemory(dev->device, *out_memory, NULL);
        }
        return false;
    }
    return true;
}

/* ----------------------------------------------------------------------------
   Staging buffer release
   ------------------------------------------------------------------------- */
void vk_staging_buffer_release(vk_Device *dev, VkBuffer buffer,
                               VkDeviceMemory memory, bool used_pool) {
    vkUnmapMemory(dev->device, memory);
    if (!used_pool) {
        vkDestroyBuffer(dev->device, buffer, NULL);
        vkFreeMemory(dev->device, memory, NULL);
    }
}

/* ----------------------------------------------------------------------------
   SPIR-V entry point extraction
   ------------------------------------------------------------------------- */
const char *vk_spirv_get_entry_point(const uint32_t *code, size_t size) {
    if (size < 20 || (size % 4) != 0) return NULL;
    if (code[0] != 0x07230203) return NULL;  // SPIR-V magic

    size_t word_count = size / 4;
    size_t offset = 5;  // Skip header (5 words)

    while (offset < word_count) {
        uint32_t word = code[offset];
        uint16_t opcode = word & 0xFFFF;
        uint16_t length = word >> 16;
        if (length == 0) return NULL;

        // OpEntryPoint (0x0F) with ExecutionModel GLCompute (5)
        if (opcode == 0x0F && (offset + length < word_count) &&
            code[offset + 1] == 5) {
            if (length > 3) {
                const char *name = (const char *)&code[offset + 3];
                // Ensure null termination within the SPIR-V data
                size_t max_name_len = (length - 3) * 4;
                for (size_t i = 0; i < max_name_len; i++) {
                    if (name[i] == 0)
                        return name;
                }
            }
        }
        offset += length;
    }
    return NULL;
}

/* ----------------------------------------------------------------------------
   SPIR-V NonReadable decoration patching
   ------------------------------------------------------------------------- */
uint32_t *vk_spirv_patch_nonreadable_uav(const uint32_t *code, size_t size,
                                         uint32_t binding) {
    if (size < 20 || (size % 4) != 0) return NULL;
    if (code[0] != 0x07230203) return NULL;

    size_t word_count = size / 4;
    size_t offset = 5;
    bool found_binding = false;
    uint32_t target_id = 0;
    size_t inject_offset = 0;

    // Find OpDecorate Binding for the given binding number
    while (offset < word_count) {
        uint32_t word = code[offset];
        uint16_t opcode = word & 0xFFFF;
        uint16_t length = word >> 16;
        if (length == 0) return NULL;

        // OpDecorate = 71, Decoration Binding = 33
        if (opcode == 71 && length >= 4 &&
            code[offset + 2] == 33 && code[offset + 3] == binding) {
            target_id = code[offset + 1];
            found_binding = true;
            inject_offset = offset + length;  // position after this OpDecorate
            break;
        }
        offset += length;
    }
    if (!found_binding) return NULL;

    // Check if NonReadable (25) already exists for this id
    offset = 5;
    while (offset < word_count) {
        uint32_t word = code[offset];
        uint16_t opcode = word & 0xFFFF;
        uint16_t length = word >> 16;
        if (opcode == 71 && length >= 3 &&
            code[offset + 1] == target_id && code[offset + 2] == 25) {
            return NULL;  // Already has NonReadable
        }
        offset += length;
    }

    // Inject OpDecorate %id NonReadable (3 words)
    uint32_t *patched = (uint32_t *)PyMem_Malloc(size + 12);
    if (!patched) return NULL;

    memcpy(patched, code, inject_offset * 4);
    patched[inject_offset++] = (3 << 16) | 71;   // OpDecorate, 3 words
    patched[inject_offset++] = target_id;
    patched[inject_offset++] = 25;               // NonReadable
    memcpy(patched + inject_offset, code + (inject_offset - 3),
           size - ((inject_offset - 3) * 4));

    return patched;
}

/* ----------------------------------------------------------------------------
   Public helpers: allocate a temporary command buffer
   ------------------------------------------------------------------------- */
VkCommandBuffer vk_allocate_temp_cmd(vk_Device *dev) {
    VkCommandBufferAllocateInfo allocInfo = { VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO };
    allocInfo.commandPool = dev->command_pool;
    allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    allocInfo.commandBufferCount = 1;
    VkCommandBuffer cmd = VK_NULL_HANDLE;
    vkAllocateCommandBuffers(dev->device, &allocInfo, &cmd);
    return cmd;
}

void vk_free_temp_cmd(vk_Device *dev, VkCommandBuffer cmd) {
    if (cmd)
        vkFreeCommandBuffers(dev->device, dev->command_pool, 1, &cmd);
}