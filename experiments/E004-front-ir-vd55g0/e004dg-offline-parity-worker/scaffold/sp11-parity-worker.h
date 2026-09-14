/* SPDX-License-Identifier: MIT */
#ifndef SP11_PARITY_WORKER_H
#define SP11_PARITY_WORKER_H

#include <stddef.h>
#include <stdint.h>

enum sp11_worker_status {
    SP11_WORKER_OK = 0,
    SP11_WORKER_EINVAL = -1,
    SP11_WORKER_EBOUNDS = -2,
    SP11_WORKER_EWORK = -3,
};

struct sp11_worker_request {
    uint8_t *dst_base;
    size_t dst_extent;
    const uint8_t *src;
    size_t src_extent;
    uint32_t width;
    uint32_t height;
    uint64_t request_id;
    size_t payload_offset;
    size_t captured_extent;
    size_t serialized_extent;
    uint8_t synthetic_fill;
    /* Caller-owned offline scratch; required only by request_id >= 10. */
    uint8_t *work_base;
    size_t work_extent;
};

int sp11_parity_worker_run(struct sp11_worker_request *req);

#endif
