/* SPDX-License-Identifier: MIT */
#ifndef SP11_LOADALGO_CAMERA_PROXY_H
#define SP11_LOADALGO_CAMERA_PROXY_H
#include <stdint.h>
#include "sp11-securepd-camera-wire.h"

/* Exact argument order recovered from libloadalgo_skel.so DWARF. */
struct sp11_loadalgo_gaussian_call {
    uint64_t handle;
    int32_t src_fd;
    uint32_t src_offset;
    uint32_t src_len;
    uint32_t src_width;
    uint32_t src_height;
    uint32_t src_stride;
    int32_t dst_fd;
    uint32_t dst_offset;
    uint32_t dst_len;
    uint32_t dst_stride;
    int32_t heap_fd;
    uint32_t heap_offset;
    uint32_t heap_len;
    uint32_t mode_static;
};

int sp11_loadalgo_camera_build_call(struct sp11_loadalgo_gaussian_call *call,
                                    uint64_t handle,
                                    int src_fd, uint32_t src_len,
                                    int dst_fd, uint32_t captured_extent,
                                    int heap_fd, uint32_t heap_len,
                                    uint32_t width, uint32_t height);
#endif
