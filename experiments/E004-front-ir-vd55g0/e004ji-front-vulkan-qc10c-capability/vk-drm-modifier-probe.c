/* SPDX-License-Identifier: MIT
 * E004ji: Vulkan read-only physical-device format/modifier probe.
 * Queries device capabilities, never creates VkDevice, imports DMA-BUF,
 * opens cameras, decodes pixels, or writes to GPU.
 */
#include <vulkan/vulkan.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct candidate { const char *name; VkFormat fmt; };
static const struct candidate formats[]={
    {"NV12_8BIT", VK_FORMAT_G8_B8R8_2PLANE_420_UNORM},
    {"YUV420_8BIT_3PLANE", VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM},
    {"P010_10BIT_16_CONTAINER", VK_FORMAT_G10X6_B10X6R10X6_2PLANE_420_UNORM_3PACK16},
    {"YUV420_10BIT_3PLANE", VK_FORMAT_G10X6_B10X6_R10X6_3PLANE_420_UNORM_3PACK16},
    {"P016_16BIT_CONTAINER", VK_FORMAT_G16_B16R16_2PLANE_420_UNORM},
};

static void die(const char *name,VkResult code) {
    fprintf(stderr,"E004JI_VULKAN_QUERY_FAIL %s code=%d\n",name,(int)code);exit(1);
}
static int has_extension(VkPhysicalDevice dev,const char *name) {
    uint32_t n=0;
    VkResult rc=vkEnumerateDeviceExtensionProperties(dev,NULL,&n,NULL);
    if(rc!=VK_SUCCESS) die("device-extensions-count",rc);
    VkExtensionProperties *ext=calloc(n+1,sizeof(*ext));
    if(!ext) die("calloc",VK_ERROR_OUT_OF_HOST_MEMORY);
    rc=vkEnumerateDeviceExtensionProperties(dev,NULL,&n,ext);
    if(rc!=VK_SUCCESS) die("device-extensions-list",rc);
    int found=0;
    for(uint32_t i=0;i<n;i++) if(strcmp(ext[i].extensionName,name)==0) found=1;
    free(ext);
    return found;
}
int main(void) {
    const VkApplicationInfo ai={
       .sType=VK_STRUCTURE_TYPE_APPLICATION_INFO,
       .pApplicationName="SP11-readonly-front-UBWC-audit",
       .apiVersion=VK_API_VERSION_1_2
    };
    const VkInstanceCreateInfo ci={.sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
                                  .pApplicationInfo=&ai};
    VkInstance instance=VK_NULL_HANDLE;
    VkResult rc=vkCreateInstance(&ci,NULL,&instance);
    if(rc!=VK_SUCCESS) die("vkCreateInstance",rc);
    uint32_t count=0;rc=vkEnumeratePhysicalDevices(instance,&count,NULL);
    if(rc!=VK_SUCCESS||count==0)die("no-physical-device",rc);
    VkPhysicalDevice *devs=calloc(count,sizeof(*devs));
    if(!devs)die("calloc-devices",VK_ERROR_OUT_OF_HOST_MEMORY);
    rc=vkEnumeratePhysicalDevices(instance,&count,devs);
    if(rc!=VK_SUCCESS)die("physical-device-list",rc);
    for(uint32_t k=0;k<count;k++){
        VkPhysicalDeviceProperties props={0};
        vkGetPhysicalDeviceProperties(devs[k],&props);
        int drm=has_extension(devs[k],"VK_EXT_image_drm_format_modifier");
        int dma=has_extension(devs[k],"VK_EXT_external_memory_dma_buf");
        printf("VULKAN_GPU name=%s api=%u.%u driver=%u vendor=0x%x device=0x%x drm_modifier_ext=%d dma_buf_ext=%d\n",
             props.deviceName,VK_API_VERSION_MAJOR(props.apiVersion),
             VK_API_VERSION_MINOR(props.apiVersion),props.driverVersion,
             props.vendorID,props.deviceID,drm,dma);
        for(size_t f=0;f<sizeof(formats)/sizeof(formats[0]);f++){
            const struct candidate *spec=&formats[f];
            VkDrmFormatModifierPropertiesListEXT mods={
                .sType=VK_STRUCTURE_TYPE_DRM_FORMAT_MODIFIER_PROPERTIES_LIST_EXT
            };
            VkFormatProperties2 format={
                .sType=VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_2,
                .pNext=drm?&mods:NULL
            };
            vkGetPhysicalDeviceFormatProperties2(devs[k],spec->fmt,&format);
            uint32_t n=drm?mods.drmFormatModifierCount:0;
            VkDrmFormatModifierPropertiesEXT *entries=calloc(n+1,sizeof(*entries));
            if(!entries)die("calloc-modifiers",VK_ERROR_OUT_OF_HOST_MEMORY);
            mods.pDrmFormatModifierProperties=entries;
            if(drm)vkGetPhysicalDeviceFormatProperties2(devs[k],spec->fmt,&format);
            printf("VK_FORMAT name=%s value=%d optimal=0x%" PRIx64
                   " linear=0x%" PRIx64 " modifiers=%u\n",spec->name,
                spec->fmt,(uint64_t)format.formatProperties.optimalTilingFeatures,
                (uint64_t)format.formatProperties.linearTilingFeatures,
                n);
            for(uint32_t i=0;i<n;i++){
                printf("DRM_MODIFIER format=%s modifier=0x%016" PRIx64
                       " planes=%u features=0x%" PRIx64 "\n",
                    spec->name,entries[i].drmFormatModifier,
                    entries[i].drmFormatModifierPlaneCount,
                    (uint64_t)entries[i].drmFormatModifierTilingFeatures);
            }
            free(entries);
        }
    }
    free(devs);
    vkDestroyInstance(instance,NULL);
    return 0;
}
