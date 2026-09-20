/* SPDX-License-Identifier: GPL-2.0-only */
#include "nv12-buffer-plan.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void assert_unbound(const struct sp11_nv12_buffer_plan *p)
{
    assert(p->y.dma32 == 0 && p->uv.dma32 == 0);
}
int main(void)
{
    struct sp11_nv12_buffer_plan p, tampered;
    unsigned tests = 0;
    assert(sp11_nv12_plan_create(2560,1440,2560,&p) == 0); ++tests;
    assert(p.y.bytes == 3686400u && p.uv.offset == 3686400u &&
           p.uv.bytes == 1843200u && p.allocation_bytes == 5529600u); ++tests;
    assert(p.y.rows == 1440u && p.uv.rows == 720u &&
           p.y.stride == 2560u && p.uv.stride == 2560u); ++tests;
    assert(p.bus_packer == 3u && !p.compression_enabled &&
           p.num_isp_clients == 2u && p.num_v4l2_memory_planes == 1u); ++tests;
    assert_unbound(&p); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, 0x10000000u, p.allocation_bytes) == 0 &&
           p.y.dma32 == 0x10000000u && p.uv.dma32 == 0x10384000u); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, 0x10000000u, p.allocation_bytes - 1u) != 0); ++tests;
    assert_unbound(&p); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, 0, p.allocation_bytes) != 0); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, 0x10000001u, p.allocation_bytes) != 0); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, UINT64_C(0xffffffff), p.allocation_bytes) != 0); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, UINT64_C(0xff000000), p.allocation_bytes) == 0); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, UINT64_C(0xffc00000), p.allocation_bytes) != 0); ++tests;
    assert_unbound(&p); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, UINT64_C(0x100000000), p.allocation_bytes) != 0); ++tests;
    assert(sp11_nv12_plan_bind_dma(&p, UINT64_MAX-63u, p.allocation_bytes) != 0); ++tests;
    tampered = p; tampered.bus_packer = 11;
    assert(sp11_nv12_plan_bind_dma(&tampered, 0x10000000u, tampered.allocation_bytes) != 0); ++tests;
    tampered = p; tampered.compression_enabled = 1;
    assert(sp11_nv12_plan_bind_dma(&tampered, 0x10000000u, tampered.allocation_bytes) != 0); ++tests;
    tampered = p; tampered.uv.offset += 64;
    assert(sp11_nv12_plan_bind_dma(&tampered, 0x10000000u, tampered.allocation_bytes) != 0); ++tests;
    tampered = p; tampered.num_isp_clients = 1;
    assert(sp11_nv12_plan_bind_dma(&tampered, 0x10000000u, tampered.allocation_bytes) != 0); ++tests;
    assert(sp11_nv12_plan_create(3840,2160,3840,&p) != 0); ++tests;
    assert(sp11_nv12_plan_create(2560,1440,3584,&p) != 0); ++tests;
    assert(sp11_nv12_plan_create(2559,1440,2560,&p) != 0); ++tests;
    assert(sp11_nv12_plan_create(2560,1439,2560,&p) != 0); ++tests;
    assert(sp11_nv12_plan_create(2560,1440,2560,NULL) != 0); ++tests;
    assert(sp11_nv12_plan_create(2560,1440,2560,&p) == 0); ++tests;
    puts("PASS: 26 offline C layout/DMA/format guard checks; no hardware accessed");
    (void)tests;
    return 0;
}
