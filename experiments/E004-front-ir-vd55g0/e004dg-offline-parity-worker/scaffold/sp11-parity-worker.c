/* SPDX-License-Identifier: MIT */
/*
 * E004dg/E004dh OFFLINE parity worker.
 *
 * This is source-controlled algorithm work only. It is not signed, admitted,
 * installed or runnable in production CPZ.  The later request branch composes
 * the Windows-proven SWABF and SWASF scalar stages; Linux SecureISP runtime is
 * intentionally not involved.
 */
#include "sp11-parity-worker.h"
#include "../../e004dh-swab-exact-offline-port/scaffold/sp11-swabf-reference.h"
#include "../../e004dh-swab-exact-offline-port/scaffold/sp11-swasf-reference.h"

static int sp11_mul_size(size_t a, size_t b, size_t *out)
{
    if (a && b > (size_t)-1 / a)
        return SP11_WORKER_EBOUNDS;
    *out = a * b;
    return SP11_WORKER_OK;
}

static void sp11_fill(uint8_t *dst, uint8_t value, size_t len)
{
    size_t i;
    for (i = 0; i < len; i++)
        dst[i] = value;
}

static void sp11_move(uint8_t *dst, const uint8_t *src, size_t len)
{
    size_t i;

    if (dst == src || !len)
        return;
    if (dst < src || dst >= src + len) {
        for (i = 0; i < len; i++)
            dst[i] = src[i];
    } else {
        for (i = len; i; i--)
            dst[i - 1] = src[i - 1];
    }
}

static int sp11_swab_two_pass_exact(struct sp11_worker_request *req,
                                    uint8_t *dst, size_t y_size)
{
    size_t raw_off, smooth_off, plane_bytes, need;
    uint8_t *swab;
    int16_t *raw16, *smooth16;
    int ret;

    if (!req->work_base)
        return SP11_WORKER_EWORK;
    if (((uintptr_t)req->work_base & 1u) != 0u)
        return SP11_WORKER_EWORK;
    if (y_size > ((size_t)-1 - 1u) / 2u)
        return SP11_WORKER_EBOUNDS;
    raw_off = (y_size + 1u) & ~(size_t)1u;
    if (sp11_mul_size(y_size, sizeof(int16_t), &plane_bytes))
        return SP11_WORKER_EBOUNDS;
    if (raw_off > (size_t)-1 - plane_bytes)
        return SP11_WORKER_EBOUNDS;
    smooth_off = raw_off + plane_bytes;
    if (smooth_off > (size_t)-1 - plane_bytes)
        return SP11_WORKER_EBOUNDS;
    need = smooth_off + plane_bytes;
    if (req->work_extent < need)
        return SP11_WORKER_EWORK;

    swab = req->work_base;
    raw16 = (int16_t *)(void *)(req->work_base + raw_off);
    smooth16 = (int16_t *)(void *)(req->work_base + smooth_off);

    ret = sp11_swabf_reference(swab, y_size, req->src, req->src_extent,
                               req->width, req->height,
                               &sp11_swabf_windows_oracle_tuning);
    if (ret)
        return ret == -2 ? SP11_WORKER_EBOUNDS : SP11_WORKER_EINVAL;

    ret = sp11_swasf_reference(dst, y_size, swab, y_size,
                               req->width, req->height,
                               raw16, y_size, smooth16, y_size,
                               sp11_swasf_windows_oracle_tuning,
                               SP11_SWASF_WINDOWS_ACTIVITY_SCALE);
    if (ret)
        return ret == -2 ? SP11_WORKER_EBOUNDS : SP11_WORKER_EINVAL;
    return SP11_WORKER_OK;
}

int sp11_parity_worker_run(struct sp11_worker_request *req)
{
    size_t y_size, tail_size, frame_size, dst_end;
    uint8_t *dst;
    int ret;

    if (!req || !req->dst_base || !req->src || !req->width || !req->height)
        return SP11_WORKER_EINVAL;
    if (!req->captured_extent || req->serialized_extent > req->captured_extent ||
        req->payload_offset > req->serialized_extent)
        return SP11_WORKER_EBOUNDS;
    if (req->captured_extent > req->dst_extent ||
        req->serialized_extent > req->dst_extent)
        return SP11_WORKER_EBOUNDS;

    ret = sp11_mul_size((size_t)req->width, (size_t)req->height, &y_size);
    if (ret)
        return ret;
    tail_size = y_size / 2;
    if (y_size > (size_t)-1 - tail_size)
        return SP11_WORKER_EBOUNDS;
    frame_size = y_size + tail_size;
    if (req->payload_offset > (size_t)-1 - frame_size)
        return SP11_WORKER_EBOUNDS;
    dst_end = req->payload_offset + frame_size;
    if (dst_end > req->serialized_extent || dst_end > req->captured_extent ||
        dst_end > req->dst_extent)
        return SP11_WORKER_EBOUNDS;
    if (req->src_extent < y_size)
        return SP11_WORKER_EBOUNDS;

    dst = req->dst_base + req->payload_offset;

    /* Windows FUN_1800033d8: Y=100, UV/tail=0x80; source unused. */
    if (req->synthetic_fill) {
        sp11_fill(dst, 100, y_size);
        sp11_fill(dst + y_size, 0x80, tail_size);
        return SP11_WORKER_OK;
    }

    /* Windows FUN_180003718: request IDs below 10 copy luma then neutral tail. */
    if (req->request_id < 10) {
        sp11_move(dst, req->src, y_size);
        sp11_fill(dst + y_size, 0x80, tail_size);
        return SP11_WORKER_OK;
    }

    /* Windows FUN_180003478: SWABF(source->scratch) -> SWASF(scratch->dst). */
    ret = sp11_swab_two_pass_exact(req, dst, y_size);
    if (ret)
        return ret;
    sp11_fill(dst + y_size, 0x80, tail_size);
    return SP11_WORKER_OK;
}
