/* SPDX-License-Identifier: MIT */
#ifndef SP11_SECUREPD_CAMERA_WIRE_H
#define SP11_SECUREPD_CAMERA_WIRE_H

#include <stddef.h>
#include <stdint.h>
#include "../../e004dc-cpz-protected-frame-worker-image-and-invoke-abi/scaffold/sp11-securepd-worker-abi.h"

#define SP11_CAMERA_CONTROL_MAGIC   0x314d4143u /* "CAM1" little-endian */
#define SP11_CAMERA_CONTROL_VERSION 1u
#define SP11_CAMERA_CONTROL_F_SYNTHETIC (1u << 0)

#define SP11_SECUREPD_ACCESS_READ  (1u << 0)
#define SP11_SECUREPD_ACCESS_WRITE (1u << 1)

/* Lives at offset zero of the proxy-supplied protected HEAP buffer. */
struct sp11_securepd_camera_control {
    uint32_t magic;             /* +0x00 */
    uint32_t version;           /* +0x04 */
    uint64_t request_id;        /* +0x08 */
    uint32_t payload_offset;    /* +0x10 */
    uint32_t captured_extent;   /* +0x14 */
    uint32_t serialized_extent; /* +0x18 */
    uint32_t flags;             /* +0x1c */
};

/* Existing proxy expects exactly one 64-bit completion value. */
typedef uint64_t sp11_securepd_camera_response_t;

struct sp11_securepd_camera_map_ops {
    int (*verify)(void *ctx, uint64_t paddr, uint32_t len,
                  int32_t type, uint32_t access);
    int (*map)(void *ctx, uint64_t paddr, uint32_t len,
               uint32_t access, uint64_t *trusted_vaddr);
    int (*unmap)(void *ctx, uint64_t trusted_vaddr, uint32_t len);
};

enum sp11_securepd_wire_status {
    SP11_SECUREPD_WIRE_OK       = 0,
    SP11_SECUREPD_WIRE_EINVAL   = -1,
    SP11_SECUREPD_WIRE_EVERIFY  = -2,
    SP11_SECUREPD_WIRE_EMAP     = -3,
    SP11_SECUREPD_WIRE_ECONTROL = -4,
    SP11_SECUREPD_WIRE_EWORKER  = -5,
    SP11_SECUREPD_WIRE_EUNMAP   = -6,
    SP11_SECUREPD_WIRE_EADDR    = -7,
};

size_t sp11_securepd_camera_heap_required(uint32_t width, uint32_t height);
void sp11_securepd_camera_init_control(struct sp11_securepd_camera_control *ctl,
                                       uint64_t request_id,
                                       uint32_t payload_offset,
                                       uint32_t captured_extent,
                                       uint32_t serialized_extent,
                                       int synthetic_fill);
int sp11_securepd_camera_process_gaussian_packet(
    const struct sp11_securepd_gaussian_packet *packet,
    const struct sp11_securepd_camera_map_ops *ops,
    void *ops_ctx,
    sp11_securepd_camera_response_t *response);

#endif
