/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "sp11-securepd-camera-wire.h"
#include "../../e004dg-offline-parity-worker/scaffold/sp11-parity-worker.h"

_Static_assert(sizeof(struct sp11_securepd_gaussian_packet) == 96, "shipping proxy packet ABI");
_Static_assert(sizeof(struct sp11_securepd_camera_control) == 32, "camera control ABI");
_Static_assert(offsetof(struct sp11_securepd_camera_control, request_id) == 0x08, "request offset");
_Static_assert(offsetof(struct sp11_securepd_camera_control, flags) == 0x1c, "flags offset");
_Static_assert(sizeof(sp11_securepd_camera_response_t) == 8, "proxy response ABI");

static void zero_bytes(void *ptr, size_t len)
{
    uint8_t *p=(uint8_t *)ptr; size_t i;
    for (i=0;i<len;i++) p[i]=0;
}

static int ptr_from_u64(uint64_t v, void **out)
{
    uintptr_t p=(uintptr_t)v;
    if (!p || (uint64_t)p != v) return SP11_SECUREPD_WIRE_EADDR;
    *out=(void *)p;
    return 0;
}

static size_t worker_scratch_required(uint32_t width, uint32_t height)
{
    uint64_t y, raw_off, need;
    if (!width || !height) return 0;
    y=(uint64_t)width*height;
    if (y > (uint64_t)(size_t)-1) return 0;
    raw_off=(y+1u)&~(uint64_t)1u;
    need=raw_off+4u*y;
    if (need > (uint64_t)(size_t)-1) return 0;
    return (size_t)need;
}

size_t sp11_securepd_camera_heap_required(uint32_t width, uint32_t height)
{
    size_t scratch=worker_scratch_required(width,height);
    if (!scratch || scratch > (size_t)-1-sizeof(struct sp11_securepd_camera_control)) return 0;
    return sizeof(struct sp11_securepd_camera_control)+scratch;
}

void sp11_securepd_camera_init_control(struct sp11_securepd_camera_control *c,
                                       uint64_t request_id,
                                       uint32_t payload_offset,
                                       uint32_t captured_extent,
                                       uint32_t serialized_extent,
                                       int synthetic_fill)
{
    if (!c) return;
    zero_bytes(c,sizeof(*c));
    c->magic=SP11_CAMERA_CONTROL_MAGIC;
    c->version=SP11_CAMERA_CONTROL_VERSION;
    c->request_id=request_id;
    c->payload_offset=payload_offset;
    c->captured_extent=captured_extent;
    c->serialized_extent=serialized_extent;
    if (synthetic_fill) c->flags|=SP11_CAMERA_CONTROL_F_SYNTHETIC;
}

static int validate_packet_shape(const struct sp11_securepd_gaussian_packet *p)
{
    uint64_t y;
    if (!p || !p->src_width || !p->src_height) return SP11_SECUREPD_WIRE_EINVAL;
    if (p->src_stride != p->src_width || p->dst_stride != p->src_width)
        return SP11_SECUREPD_WIRE_EINVAL;
    y=(uint64_t)p->src_width*p->src_height;
    if (y > UINT32_MAX || p->src.size < y || !p->src.addr || !p->dst.addr || !p->heap.addr)
        return SP11_SECUREPD_WIRE_EINVAL;
    if (p->heap.size < sizeof(struct sp11_securepd_camera_control))
        return SP11_SECUREPD_WIRE_EINVAL;
    return 0;
}

static int validate_control(const struct sp11_securepd_camera_control *c,
                            const struct sp11_securepd_gaussian_packet *p)
{
    uint64_t y, frame, end;
    size_t need;
    if (!c || c->magic != SP11_CAMERA_CONTROL_MAGIC || c->version != SP11_CAMERA_CONTROL_VERSION)
        return SP11_SECUREPD_WIRE_ECONTROL;
    if (c->flags & ~SP11_CAMERA_CONTROL_F_SYNTHETIC) return SP11_SECUREPD_WIRE_ECONTROL;
    y=(uint64_t)p->src_width*p->src_height;
    frame=y+y/2u;
    if (!c->captured_extent || c->captured_extent > p->dst.size ||
        c->serialized_extent > c->captured_extent || c->payload_offset > c->serialized_extent)
        return SP11_SECUREPD_WIRE_ECONTROL;
    end=(uint64_t)c->payload_offset+frame;
    if (end > c->serialized_extent || end > c->captured_extent)
        return SP11_SECUREPD_WIRE_ECONTROL;
    if (!(c->flags & SP11_CAMERA_CONTROL_F_SYNTHETIC) && c->request_id >= 10u) {
        need=sp11_securepd_camera_heap_required(p->src_width,p->src_height);
        if (!need || p->heap.size < need) return SP11_SECUREPD_WIRE_ECONTROL;
    }
    return 0;
}

static sp11_securepd_camera_response_t response_from_status(int status)
{
    return status == 0 ? 0u : (sp11_securepd_camera_response_t)(uint32_t)status;
}

int sp11_securepd_camera_process_gaussian_packet(
    const struct sp11_securepd_gaussian_packet *p,
    const struct sp11_securepd_camera_map_ops *ops,
    void *ctx,
    sp11_securepd_camera_response_t *response)
{
    struct sp11_worker_request req;
    struct sp11_securepd_camera_control *ctl=0;
    uint8_t *src=0,*dst=0,*heap=0;
    uint64_t src_va=0,dst_va=0,heap_va=0;
    int src_mapped=0,dst_mapped=0,heap_mapped=0;
    int status, worker_status=0, cleanup_status=0, ret;

    if (response) *response=response_from_status(SP11_SECUREPD_WIRE_EINVAL);
    if (!ops || !ops->verify || !ops->map || !ops->unmap) return SP11_SECUREPD_WIRE_EINVAL;
    status=validate_packet_shape(p); if (status) goto done;

    /* Same-machine SecurePD registrations use DATA(7) for images, HEAP(5) for scratch. */
    if (ops->verify(ctx,p->src.addr,p->src.size,SP11_SECUREPD_DATA,SP11_SECUREPD_ACCESS_READ) ||
        ops->verify(ctx,p->dst.addr,p->dst.size,SP11_SECUREPD_DATA,SP11_SECUREPD_ACCESS_WRITE) ||
        ops->verify(ctx,p->heap.addr,p->heap.size,SP11_SECUREPD_HEAP,
                    SP11_SECUREPD_ACCESS_READ|SP11_SECUREPD_ACCESS_WRITE)) {
        status=SP11_SECUREPD_WIRE_EVERIFY; goto done;
    }
    if (ops->map(ctx,p->src.addr,p->src.size,SP11_SECUREPD_ACCESS_READ,&src_va)) {
        status=SP11_SECUREPD_WIRE_EMAP; goto done;
    }
    src_mapped=1;
    if (ops->map(ctx,p->dst.addr,p->dst.size,SP11_SECUREPD_ACCESS_WRITE,&dst_va)) {
        status=SP11_SECUREPD_WIRE_EMAP; goto cleanup;
    }
    dst_mapped=1;
    if (ops->map(ctx,p->heap.addr,p->heap.size,
                 SP11_SECUREPD_ACCESS_READ|SP11_SECUREPD_ACCESS_WRITE,&heap_va)) {
        status=SP11_SECUREPD_WIRE_EMAP; goto cleanup;
    }
    heap_mapped=1;
    if (ptr_from_u64(src_va,(void **)&src) || ptr_from_u64(dst_va,(void **)&dst) ||
        ptr_from_u64(heap_va,(void **)&heap)) {
        status=SP11_SECUREPD_WIRE_EADDR; goto cleanup;
    }
    ctl=(struct sp11_securepd_camera_control *)(void *)heap;
    status=validate_control(ctl,p); if (status) goto cleanup;

    zero_bytes(&req,sizeof(req));
    req.dst_base=dst; req.dst_extent=p->dst.size;
    req.src=src; req.src_extent=p->src.size;
    req.width=p->src_width; req.height=p->src_height;
    req.request_id=ctl->request_id;
    req.payload_offset=ctl->payload_offset;
    req.captured_extent=ctl->captured_extent;
    req.serialized_extent=ctl->serialized_extent;
    req.synthetic_fill=(ctl->flags&SP11_CAMERA_CONTROL_F_SYNTHETIC)?1u:0u;
    req.work_base=heap+sizeof(*ctl);
    req.work_extent=p->heap.size-sizeof(*ctl);
    worker_status=sp11_parity_worker_run(&req);
    status=worker_status?SP11_SECUREPD_WIRE_EWORKER:SP11_SECUREPD_WIRE_OK;

cleanup:
    if (heap_mapped) { ret=ops->unmap(ctx,heap_va,p->heap.size); if(ret&&!cleanup_status)cleanup_status=ret; }
    if (dst_mapped) { ret=ops->unmap(ctx,dst_va,p->dst.size); if(ret&&!cleanup_status)cleanup_status=ret; }
    if (src_mapped) { ret=ops->unmap(ctx,src_va,p->src.size); if(ret&&!cleanup_status)cleanup_status=ret; }
    if (cleanup_status && status==SP11_SECUREPD_WIRE_OK) status=SP11_SECUREPD_WIRE_EUNMAP;

done:
    if (response) *response=response_from_status(status);
    return status;
}
