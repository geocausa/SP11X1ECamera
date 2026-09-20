/* SPDX-License-Identifier: GPL-2.0-only
 * E004ii: standalone planning model for *proposed* SP11 linear NV12.
 * No MMIO, kernel hooks, device opening, or hardware authorization.
 */
#ifndef SP11_NV12_BUFFER_PLAN_H
#define SP11_NV12_BUFFER_PLAN_H
#include <stdint.h>
#include <stddef.h>
#define SP11_NV12_WIDTH 2560u
#define SP11_NV12_HEIGHT 1440u
#define SP11_NV12_STRIDE_PROPOSED 2560u
#define SP11_NV12_BUS_PACKER_PROPOSED 3u /* public VFE BUS ver3; unverified SP11 */
struct sp11_nv12_plane {
    uint32_t offset;
    uint32_t bytes;
    uint32_t rows;
    uint32_t stride;
    uint32_t dma32;
};
struct sp11_nv12_buffer_plan {
    struct sp11_nv12_plane y;
    struct sp11_nv12_plane uv;
    uint32_t allocation_bytes;
    uint8_t bus_packer;
    uint8_t num_v4l2_memory_planes;
    uint8_t num_isp_clients;
    uint8_t compression_enabled;
};
/* Returns 0 or -1. Caller must validate physical ISP format independently. */
int sp11_nv12_plan_create(uint32_t width, uint32_t height, uint32_t stride,
                          struct sp11_nv12_buffer_plan *out);
/* base and allocated_len are independently supplied by the DMA allocator. */
int sp11_nv12_plan_bind_dma(struct sp11_nv12_buffer_plan *plan,
                            uint64_t base, size_t allocated_len);
#endif
