/* SPDX-License-Identifier: MIT */
#include "sp11-loadalgo-camera-proxy.h"

static void zero_bytes(void *ptr, unsigned long n)
{
    unsigned char *p=(unsigned char *)ptr; unsigned long i;
    for(i=0;i<n;i++)p[i]=0;
}

int sp11_loadalgo_camera_build_call(struct sp11_loadalgo_gaussian_call *c,
                                    uint64_t handle,
                                    int src_fd, uint32_t src_len,
                                    int dst_fd, uint32_t captured_extent,
                                    int heap_fd, uint32_t heap_len,
                                    uint32_t width, uint32_t height)
{
    uint64_t y, frame;
    size_t heap_need;
    if(!c || src_fd<0 || dst_fd<0 || heap_fd<0 || !width || !height)return -1;
    y=(uint64_t)width*height; frame=y+y/2u;
    if(y>UINT32_MAX || src_len<y || captured_extent<frame)return -2;
    heap_need=sp11_securepd_camera_heap_required(width,height);
    if(!heap_need || heap_len<heap_need)return -2;
    zero_bytes(c,sizeof(*c));
    c->handle=handle;
    c->src_fd=src_fd; c->src_len=src_len;
    c->src_width=width; c->src_height=height; c->src_stride=width;
    c->dst_fd=dst_fd; c->dst_len=captured_extent; c->dst_stride=width;
    c->heap_fd=heap_fd; c->heap_len=heap_len;
    /* Shipping implementation does not consume src/dst/heap offsets; keep zero. */
    c->src_offset=0; c->dst_offset=0; c->heap_offset=0;
    /* 0 selects the dynamically admitted ALGO worker; 1 selects built-in Gaussian. */
    c->mode_static=0;
    return 0;
}
