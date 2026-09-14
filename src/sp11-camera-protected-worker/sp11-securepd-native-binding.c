/* SPDX-License-Identifier: MIT */
/* Native binding to the exact APIs imported by shipped SP11 example_image.so. */
#include <stdint.h>
#include "sp11-securepd-native-api.h"
#include "sp11-securepd-native-binding.h"

_Static_assert(sizeof(struct sp11_securepd_mailbox)==32, "SecurePDMailBox ABI");
_Static_assert(sizeof(struct sp11_securepd_gaussian_packet)==SP11_SECUREPD_PROXY_PACKET_BYTES,
               "proxy packet ABI");
_Static_assert(sizeof(sp11_securepd_camera_response_t)==SP11_SECUREPD_PROXY_RESPONSE_BYTES,
               "proxy response ABI");

struct native_ctx { struct sp11_dsc_feat_priv *dsc; };
static uint8_t camera_thread_stack[SP11_SECUREPD_CAMERA_THREAD_STACK];

static int native_verify(void *opaque, uint64_t paddr, uint32_t len,
                         int32_t type, uint32_t access)
{
    struct native_ctx *ctx=(struct native_ctx *)opaque;
    (void)access;
    if (!ctx || !ctx->dsc) return -1;
    return dsc_verify_buffer(ctx->dsc,(unsigned int)type,
                             (unsigned long long)paddr,len);
}

static int native_map(void *opaque, uint64_t paddr, uint32_t len,
                      uint32_t access, uint64_t *trusted_vaddr)
{
    unsigned int va=0; int ret;
    (void)opaque; (void)access;
    if (!trusted_vaddr) return -1;
    ret=secure_pd_mapping_create_64(&va,(unsigned long long)paddr,len,
                                    SP11_QURT_MEM_CACHE_WRITEBACK,
                                    SP11_SECUREPD_MAP_PERMISSION_RW);
    if (ret) return ret;
    *trusted_vaddr=(uint64_t)va;
    return 0;
}

static int native_unmap(void *opaque, uint64_t trusted_vaddr, uint32_t len)
{
    (void)opaque;
    if (trusted_vaddr > UINT32_MAX) return -1;
    return secure_pd_mapping_delete_64((unsigned int)trusted_vaddr,len);
}

int sp11_securepd_native_process_packet(
    const struct sp11_securepd_gaussian_packet *packet,
    sp11_securepd_camera_response_t *response)
{
    static const struct sp11_securepd_camera_map_ops ops={
        native_verify,native_map,native_unmap
    };
    struct native_ctx ctx={0};
    get_secure_channel_handle(&ctx.dsc);
    if (!ctx.dsc) {
        if (response) *response=(sp11_securepd_camera_response_t)(uint32_t)SP11_SECUREPD_WIRE_EVERIFY;
        return SP11_SECUREPD_WIRE_EVERIFY;
    }
    return sp11_securepd_camera_process_gaussian_packet(packet,&ops,&ctx,response);
}

void sp11_securepd_camera_worker_thread(void *arg)
{
    struct sp11_securepd_mailbox s2p={0}, p2s={0};
    struct sp11_securepd_gaussian_packet packet;
    sp11_securepd_camera_response_t response;
    unsigned int received=0;
    int ret;
    (void)arg;

    /* Shipping example: s2p_algo CREATE id=2, p2s_algo RETRIEVE id=3. */
    ret=secure_pd_mb_get(&s2p,"s2p_algo",SP11_MB_CREATE,2);
    if (ret) return;
    do {
        ret=secure_pd_mb_get(&p2s,"p2s_algo",SP11_MB_RETRIEVE,3);
        if (ret) qurt_sleep(2000000ULL);
    } while (ret);

    for (;;) {
        received=0;
        ret=secure_pd_mb_receive(&p2s,&packet,sizeof(packet),&received);
        if (ret) break;
        if (received != sizeof(packet))
            response=(sp11_securepd_camera_response_t)(uint32_t)SP11_SECUREPD_WIRE_EINVAL;
        else
            (void)sp11_securepd_native_process_packet(&packet,&response);
        ret=secure_pd_mb_send(&s2p,&response,sizeof(response));
        if (ret) break;
    }
    (void)secure_pd_mb_delete(&p2s);
    (void)secure_pd_mb_delete(&s2p);
}

void algo_main(void *arg)
{
    unsigned int tid=0;
    (void)arg;
    (void)secure_pd_thread_create("sec_camera",camera_thread_stack,
        sizeof(camera_thread_stack),SP11_SECUREPD_CAMERA_THREAD_PRIORITY,
        sp11_securepd_camera_worker_thread,0,&tid);
}
