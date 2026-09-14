/* SPDX-License-Identifier: MIT */
#ifndef SP11_SECUREPD_CAMERA_WORKER_H
#define SP11_SECUREPD_CAMERA_WORKER_H

#include <stddef.h>
#include <stdint.h>
#include "../../e004dc-cpz-protected-frame-worker-image-and-invoke-abi/scaffold/sp11-securepd-worker-abi.h"

#define SP11_SECUREPD_CAMERA_PACKET_VERSION 1u
#define SP11_SECUREPD_CAMERA_F_SYNTHETIC    (1u << 0)

#define SP11_SECUREPD_ACCESS_READ  (1u << 0)
#define SP11_SECUREPD_ACCESS_WRITE (1u << 1)

/*
 * Proxy -> trusted image work packet.  Each protected object uses the exact
 * same-machine SecurePD {paddr,len,type} identity recovered in E004dc.
 */
struct sp11_securepd_camera_packet {
    uint32_t version;                   /* +0x00 */
    uint32_t flags;                     /* +0x04 */
    struct sp11_securepd_loadalgo_packet src;  /* +0x08 */
    struct sp11_securepd_loadalgo_packet dst;  /* +0x14 */
    struct sp11_securepd_loadalgo_packet work; /* +0x20 */
    uint32_t width;                     /* +0x2c */
    uint32_t height;                    /* +0x30 */
    uint32_t src_stride;                /* +0x34 */
    uint32_t dst_stride;                /* +0x38 */
    uint32_t payload_offset;            /* +0x3c */
    uint32_t captured_extent;           /* +0x40 */
    uint32_t serialized_extent;         /* +0x44 */
    uint64_t request_id;                /* +0x48 */
};

struct sp11_securepd_camera_result {
    int32_t status;
    int32_t worker_status;
    int32_t cleanup_status;
    uint32_t reserved;
};

enum sp11_securepd_camera_status {
    SP11_SECUREPD_CAMERA_OK      = 0,
    SP11_SECUREPD_CAMERA_EINVAL  = -1,
    SP11_SECUREPD_CAMERA_EVERIFY = -2,
    SP11_SECUREPD_CAMERA_EMAP    = -3,
    SP11_SECUREPD_CAMERA_EWORKER = -4,
    SP11_SECUREPD_CAMERA_EUNMAP  = -5,
    SP11_SECUREPD_CAMERA_EADDR   = -6,
};

struct sp11_securepd_camera_map_ops {
    int (*verify)(void *ctx, uint32_t paddr, uint32_t len,
                  int32_t type, uint32_t access);
    int (*map)(void *ctx, uint32_t paddr, uint32_t len,
               uint32_t access, uint64_t *trusted_vaddr);
    int (*unmap)(void *ctx, uint64_t trusted_vaddr, uint32_t len);
};

int sp11_securepd_camera_build_packet(
    struct sp11_securepd_camera_packet *packet,
    uint32_t src_paddr, uint32_t src_len,
    uint32_t dst_paddr, uint32_t dst_len,
    uint32_t work_paddr, uint32_t work_len,
    uint32_t width, uint32_t height, uint64_t request_id,
    uint32_t payload_offset, uint32_t captured_extent,
    uint32_t serialized_extent, int synthetic_fill);

size_t sp11_securepd_camera_required_work(uint32_t width, uint32_t height);

int sp11_securepd_camera_process_packet(
    const struct sp11_securepd_camera_packet *packet,
    const struct sp11_securepd_camera_map_ops *ops,
    void *ops_ctx,
    struct sp11_securepd_camera_result *result);

#endif
