/* SPDX-License-Identifier: GPL-2.0-only
 * E004ii offline model. No physical ISP access.
 */
#include "nv12-buffer-plan.h"
#include <limits.h>
#include <string.h>

int sp11_nv12_plan_create(uint32_t width, uint32_t height, uint32_t stride,
                          struct sp11_nv12_buffer_plan *out)
{
    struct sp11_nv12_buffer_plan p = {0};
    uint64_t y, uv, total;

    if (out == NULL)
        return -1;
    /* Never produce a partial plan on invalid input. */
    memset(out, 0, sizeof(*out));
    /* The only candidate geometry studied so far; do not pretend arbitrary
     * ISP crops, active widths or strides have been validated. */
    if (width != SP11_NV12_WIDTH || height != SP11_NV12_HEIGHT ||
        stride != SP11_NV12_STRIDE_PROPOSED)
        return -1;
    if ((width & 1u) || (height & 1u) || stride < width ||
        (stride % 64u))
        return -1;
    y = (uint64_t)stride * height;
    uv = (uint64_t)stride * (height / 2u);
    total = y + uv;
    if (total > UINT32_MAX || total == 0)
        return -1;

    p.y.offset = 0;
    p.y.bytes = (uint32_t)y;
    p.y.rows = height;
    p.y.stride = stride;
    p.uv.offset = (uint32_t)y;
    p.uv.bytes = (uint32_t)uv;
    p.uv.rows = height / 2u;
    p.uv.stride = stride;
    p.allocation_bytes = (uint32_t)total;
    p.bus_packer = SP11_NV12_BUS_PACKER_PROPOSED;
    p.num_v4l2_memory_planes = 1;
    p.num_isp_clients = 2;
    p.compression_enabled = 0;
    *out = p;
    return 0;
}

int sp11_nv12_plan_bind_dma(struct sp11_nv12_buffer_plan *plan,
                            uint64_t base, size_t allocated_len)
{
    uint64_t end, chroma;
    if (!plan)
        return -1;
    /* A failed attempt cannot retain stale valid DMA pointers. */
    plan->y.dma32 = 0;
    plan->uv.dma32 = 0;
    if (plan->allocation_bytes != 5529600u ||
        plan->y.offset != 0 || plan->y.bytes != 3686400u ||
        plan->uv.offset != plan->y.bytes || plan->uv.bytes != 1843200u ||
        plan->bus_packer != SP11_NV12_BUS_PACKER_PROPOSED ||
        plan->compression_enabled || plan->num_isp_clients != 2 ||
        plan->num_v4l2_memory_planes != 1)
        return -1;
    /* Require a 64-byte aligned nonzero base, both FULL client addresses
     * and last byte in the 32-bit device address window. */
    if (!base || (base & 63u) || allocated_len < plan->allocation_bytes)
        return -1;
    end = base + plan->allocation_bytes;
    chroma = base + plan->uv.offset;
    if (end > (UINT64_C(1) << 32) || end <= base || chroma > UINT32_MAX)
        return -1;
    plan->y.dma32 = (uint32_t)base;
    plan->uv.dma32 = (uint32_t)chroma;
    return 0;
}
