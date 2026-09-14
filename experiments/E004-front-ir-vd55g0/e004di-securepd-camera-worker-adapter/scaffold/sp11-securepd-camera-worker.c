/* SPDX-License-Identifier: MIT */
/*
 * E004di offline SecurePD image-side adapter for the exact E004dg/E004dh
 * camera parity worker.  No mailbox, FastRPC, ownership or runtime action is
 * performed here: the recovered SecurePD mapping operations are injected as
 * callbacks and are host-mocked by the verifier.
 */
#include <stdint.h>
#include "sp11-securepd-camera-worker.h"
#include "../../e004dg-offline-parity-worker/scaffold/sp11-parity-worker.h"

_Static_assert(sizeof(struct sp11_securepd_loadalgo_packet) == 12, "loadalgo ABI");
_Static_assert(sizeof(struct sp11_securepd_camera_packet) == 80, "camera packet ABI");
_Static_assert(offsetof(struct sp11_securepd_camera_packet, src) == 0x08, "src offset");
_Static_assert(offsetof(struct sp11_securepd_camera_packet, dst) == 0x14, "dst offset");
_Static_assert(offsetof(struct sp11_securepd_camera_packet, work) == 0x20, "work offset");
_Static_assert(offsetof(struct sp11_securepd_camera_packet, request_id) == 0x48, "request offset");
_Static_assert(sizeof(struct sp11_securepd_camera_result) == 16, "result ABI");

static void zero_bytes(void *ptr, size_t len)
{
    uint8_t *p = (uint8_t *)ptr;
    size_t i;
    for (i = 0; i < len; ++i) p[i] = 0;
}

static int frame_sizes(uint32_t width, uint32_t height,
                       uint64_t *y, uint64_t *frame)
{
    uint64_t yy;
    if (!width || !height) return SP11_SECUREPD_CAMERA_EINVAL;
    yy = (uint64_t)width * (uint64_t)height;
    if (yy > UINT32_MAX) return SP11_SECUREPD_CAMERA_EINVAL;
    *y = yy;
    *frame = yy + yy / 2u;
    if (*frame > UINT32_MAX) return SP11_SECUREPD_CAMERA_EINVAL;
    return 0;
}

size_t sp11_securepd_camera_required_work(uint32_t width, uint32_t height)
{
    uint64_t y, frame, raw_off, need;
    (void)frame;
    if (frame_sizes(width, height, &y, &frame)) return 0;
    raw_off = (y + 1u) & ~(uint64_t)1u;
    need = raw_off + 4u * y;
    if (need > (uint64_t)(size_t)-1) return 0;
    return (size_t)need;
}

int sp11_securepd_camera_build_packet(
    struct sp11_securepd_camera_packet *p,
    uint32_t src_paddr, uint32_t src_len,
    uint32_t dst_paddr, uint32_t dst_len,
    uint32_t work_paddr, uint32_t work_len,
    uint32_t width, uint32_t height, uint64_t request_id,
    uint32_t payload_offset, uint32_t captured_extent,
    uint32_t serialized_extent, int synthetic_fill)
{
    if (!p) return SP11_SECUREPD_CAMERA_EINVAL;
    zero_bytes(p, sizeof(*p));
    p->version = SP11_SECUREPD_CAMERA_PACKET_VERSION;
    if (synthetic_fill) p->flags |= SP11_SECUREPD_CAMERA_F_SYNTHETIC;
    p->src.paddr = src_paddr; p->src.len = src_len; p->src.type = SP11_SECUREPD_DATA;
    p->dst.paddr = dst_paddr; p->dst.len = dst_len; p->dst.type = SP11_SECUREPD_DATA;
    p->work.paddr = work_paddr; p->work.len = work_len; p->work.type = SP11_SECUREPD_HEAP;
    p->width = width; p->height = height;
    p->src_stride = width; p->dst_stride = width;
    p->request_id = request_id;
    p->payload_offset = payload_offset;
    p->captured_extent = captured_extent;
    p->serialized_extent = serialized_extent;
    return 0;
}

static int validate_packet(const struct sp11_securepd_camera_packet *p,
                           uint64_t *y_out)
{
    uint64_t y, frame, end;
    size_t work_need;
    if (!p || p->version != SP11_SECUREPD_CAMERA_PACKET_VERSION) return SP11_SECUREPD_CAMERA_EINVAL;
    if (p->flags & ~SP11_SECUREPD_CAMERA_F_SYNTHETIC) return SP11_SECUREPD_CAMERA_EINVAL;
    if (frame_sizes(p->width, p->height, &y, &frame)) return SP11_SECUREPD_CAMERA_EINVAL;
    if (p->src_stride != p->width || p->dst_stride != p->width) return SP11_SECUREPD_CAMERA_EINVAL;
    if (p->src.type != SP11_SECUREPD_DATA || p->dst.type != SP11_SECUREPD_DATA) return SP11_SECUREPD_CAMERA_EINVAL;
    if (!p->src.paddr || !p->dst.paddr || p->src.len < y) return SP11_SECUREPD_CAMERA_EINVAL;
    if (!p->captured_extent || p->serialized_extent > p->captured_extent ||
        p->captured_extent > p->dst.len || p->payload_offset > p->serialized_extent)
        return SP11_SECUREPD_CAMERA_EINVAL;
    end = (uint64_t)p->payload_offset + frame;
    if (end > p->serialized_extent || end > p->captured_extent) return SP11_SECUREPD_CAMERA_EINVAL;
    if (!(p->flags & SP11_SECUREPD_CAMERA_F_SYNTHETIC) && p->request_id >= 10u) {
        work_need = sp11_securepd_camera_required_work(p->width, p->height);
        if (!work_need || !p->work.paddr || p->work.type != SP11_SECUREPD_HEAP ||
            p->work.len < work_need)
            return SP11_SECUREPD_CAMERA_EINVAL;
    }
    *y_out = y;
    return 0;
}

static int addr_to_ptr(uint64_t addr, void **ptr)
{
    uintptr_t p = (uintptr_t)addr;
    if ((uint64_t)p != addr || !p) return SP11_SECUREPD_CAMERA_EADDR;
    *ptr = (void *)p;
    return 0;
}

int sp11_securepd_camera_process_packet(
    const struct sp11_securepd_camera_packet *p,
    const struct sp11_securepd_camera_map_ops *ops,
    void *ctx,
    struct sp11_securepd_camera_result *result)
{
    struct sp11_worker_request req;
    uint64_t y, src_va = 0, dst_va = 0, work_va = 0;
    uint8_t *src_ptr = 0, *dst_ptr = 0, *work_ptr = 0;
    int need_work, src_mapped = 0, dst_mapped = 0, work_mapped = 0;
    int status, worker_status = 0, cleanup_status = 0, ret;

    if (result) zero_bytes(result, sizeof(*result));
    if (!ops || !ops->verify || !ops->map || !ops->unmap) {
        status = SP11_SECUREPD_CAMERA_EINVAL;
        goto out_result;
    }
    status = validate_packet(p, &y);
    if (status) goto out_result;
    need_work = !(p->flags & SP11_SECUREPD_CAMERA_F_SYNTHETIC) && p->request_id >= 10u;

    if (ops->verify(ctx, p->src.paddr, p->src.len, p->src.type, SP11_SECUREPD_ACCESS_READ) ||
        ops->verify(ctx, p->dst.paddr, p->dst.len, p->dst.type, SP11_SECUREPD_ACCESS_WRITE) ||
        (need_work && ops->verify(ctx, p->work.paddr, p->work.len, p->work.type,
                                  SP11_SECUREPD_ACCESS_READ | SP11_SECUREPD_ACCESS_WRITE))) {
        status = SP11_SECUREPD_CAMERA_EVERIFY;
        goto out_result;
    }

    if (ops->map(ctx, p->src.paddr, p->src.len, SP11_SECUREPD_ACCESS_READ, &src_va)) {
        status = SP11_SECUREPD_CAMERA_EMAP; goto out_result;
    }
    src_mapped = 1;
    if (ops->map(ctx, p->dst.paddr, p->dst.len, SP11_SECUREPD_ACCESS_WRITE, &dst_va)) {
        status = SP11_SECUREPD_CAMERA_EMAP; goto cleanup;
    }
    dst_mapped = 1;
    if (need_work) {
        if (ops->map(ctx, p->work.paddr, p->work.len,
                     SP11_SECUREPD_ACCESS_READ | SP11_SECUREPD_ACCESS_WRITE, &work_va)) {
            status = SP11_SECUREPD_CAMERA_EMAP; goto cleanup;
        }
        work_mapped = 1;
    }
    if (addr_to_ptr(src_va, (void **)&src_ptr) || addr_to_ptr(dst_va, (void **)&dst_ptr) ||
        (need_work && addr_to_ptr(work_va, (void **)&work_ptr))) {
        status = SP11_SECUREPD_CAMERA_EADDR; goto cleanup;
    }

    zero_bytes(&req, sizeof(req));
    req.dst_base = dst_ptr;
    req.dst_extent = p->dst.len;
    req.src = src_ptr;
    req.src_extent = p->src.len;
    req.width = p->width;
    req.height = p->height;
    req.request_id = p->request_id;
    req.payload_offset = p->payload_offset;
    req.captured_extent = p->captured_extent;
    req.serialized_extent = p->serialized_extent;
    req.synthetic_fill = (p->flags & SP11_SECUREPD_CAMERA_F_SYNTHETIC) ? 1u : 0u;
    req.work_base = work_ptr;
    req.work_extent = need_work ? p->work.len : 0u;
    worker_status = sp11_parity_worker_run(&req);
    status = worker_status ? SP11_SECUREPD_CAMERA_EWORKER : SP11_SECUREPD_CAMERA_OK;

cleanup:
    if (work_mapped) {
        ret = ops->unmap(ctx, work_va, p->work.len);
        if (ret && !cleanup_status) cleanup_status = ret;
    }
    if (dst_mapped) {
        ret = ops->unmap(ctx, dst_va, p->dst.len);
        if (ret && !cleanup_status) cleanup_status = ret;
    }
    if (src_mapped) {
        ret = ops->unmap(ctx, src_va, p->src.len);
        if (ret && !cleanup_status) cleanup_status = ret;
    }
    if (cleanup_status && status == SP11_SECUREPD_CAMERA_OK)
        status = SP11_SECUREPD_CAMERA_EUNMAP;

out_result:
    if (result) {
        result->status = status;
        result->worker_status = worker_status;
        result->cleanup_status = cleanup_status;
    }
    return status;
}
