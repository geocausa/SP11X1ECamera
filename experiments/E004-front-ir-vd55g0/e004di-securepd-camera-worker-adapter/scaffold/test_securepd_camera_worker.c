#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "sp11-securepd-camera-worker.h"

static int failures;
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x); failures++; } } while (0)

struct mock_ctx {
    uint8_t *src, *dst, *work;
    uint32_t src_token, dst_token, work_token;
    int verify_fail_token, map_fail_token, unmap_fail_token;
    int verify_count, map_count, unmap_count;
    uint32_t unmap_order[3];
};

static uint8_t *token_ptr(struct mock_ctx *m, uint32_t token)
{
    if (token==m->src_token) return m->src;
    if (token==m->dst_token) return m->dst;
    if (token==m->work_token) return m->work;
    return 0;
}
static int mock_verify(void *ctx,uint32_t p,uint32_t n,int32_t type,uint32_t access)
{
    struct mock_ctx*m=ctx; (void)n; (void)type; (void)access; m->verify_count++;
    return p==(uint32_t)m->verify_fail_token ? -1 : token_ptr(m,p)?0:-2;
}
static int mock_map(void *ctx,uint32_t p,uint32_t n,uint32_t access,uint64_t *va)
{
    struct mock_ctx*m=ctx; uint8_t*q; (void)n; (void)access; m->map_count++;
    if(p==(uint32_t)m->map_fail_token)return -1; q=token_ptr(m,p); if(!q)return -2;
    *va=(uint64_t)(uintptr_t)q; return 0;
}
static int mock_unmap(void *ctx,uint64_t va,uint32_t n)
{
    struct mock_ctx*m=ctx; uint32_t token=0; (void)n;
    if((uint8_t *)(uintptr_t)va==m->src)token=m->src_token;
    if((uint8_t *)(uintptr_t)va==m->dst)token=m->dst_token;
    if((uint8_t *)(uintptr_t)va==m->work)token=m->work_token;
    if(m->unmap_count<3)m->unmap_order[m->unmap_count]=token;
    m->unmap_count++;
    return token==(uint32_t)m->unmap_fail_token ? -9 : 0;
}

int main(void)
{
    uint8_t src[64], dst[96], work[320];
    struct mock_ctx m={0};
    struct sp11_securepd_camera_packet p;
    struct sp11_securepd_camera_result r;
    struct sp11_securepd_camera_map_ops ops={mock_verify,mock_map,mock_unmap};
    int i, ret;

    memset(src,42,sizeof(src)); memset(dst,0xcc,sizeof(dst)); memset(work,0,sizeof(work));
    m.src=src; m.dst=dst; m.work=work; m.src_token=0x1000; m.dst_token=0x2000; m.work_token=0x3000;
    CHECK(sp11_securepd_camera_required_work(8,8)==320);
    CHECK(sp11_securepd_camera_build_packet(&p,m.src_token,sizeof(src),m.dst_token,sizeof(dst),
        m.work_token,sizeof(work),8,8,10,0,sizeof(dst),sizeof(dst),0)==0);
    CHECK(sizeof(p)==80); CHECK(sizeof(r)==16);
    ret=sp11_securepd_camera_process_packet(&p,&ops,&m,&r);
    CHECK(ret==SP11_SECUREPD_CAMERA_OK); CHECK(r.status==0); CHECK(r.worker_status==0); CHECK(r.cleanup_status==0);
    CHECK(m.verify_count==3); CHECK(m.map_count==3); CHECK(m.unmap_count==3);
    CHECK(m.unmap_order[0]==m.work_token && m.unmap_order[1]==m.dst_token && m.unmap_order[2]==m.src_token);
    for(i=0;i<64;i++)CHECK(dst[i]==42); for(i=64;i<96;i++)CHECK(dst[i]==0x80);

    /* Early-copy branch needs no scratch mapping. */
    memset(dst,0,sizeof(dst)); memset(&m.unmap_order,0,sizeof(m.unmap_order)); m.verify_count=m.map_count=m.unmap_count=0;
    CHECK(sp11_securepd_camera_build_packet(&p,m.src_token,sizeof(src),m.dst_token,sizeof(dst),
        0,0,8,8,9,0,sizeof(dst),sizeof(dst),0)==0);
    ret=sp11_securepd_camera_process_packet(&p,&ops,&m,&r); CHECK(ret==0); CHECK(m.verify_count==2); CHECK(m.map_count==2); CHECK(m.unmap_count==2);
    CHECK(memcmp(dst,src,64)==0); for(i=64;i<96;i++)CHECK(dst[i]==0x80);

    /* Synthetic still verifies/maps the established source+destination pair, as Windows dispatcher does. */
    memset(dst,0,sizeof(dst)); m.verify_count=m.map_count=m.unmap_count=0;
    CHECK(sp11_securepd_camera_build_packet(&p,m.src_token,sizeof(src),m.dst_token,sizeof(dst),0,0,8,8,0,0,sizeof(dst),sizeof(dst),1)==0);
    ret=sp11_securepd_camera_process_packet(&p,&ops,&m,&r); CHECK(ret==0); CHECK(m.verify_count==2); CHECK(m.map_count==2);
    for(i=0;i<64;i++)CHECK(dst[i]==100); for(i=64;i<96;i++)CHECK(dst[i]==0x80);

    /* Exact geometry and scratch fail closed. */
    p.src_stride=9; CHECK(sp11_securepd_camera_process_packet(&p,&ops,&m,&r)==SP11_SECUREPD_CAMERA_EINVAL); p.src_stride=8;
    CHECK(sp11_securepd_camera_build_packet(&p,m.src_token,sizeof(src),m.dst_token,sizeof(dst),0,0,8,8,10,0,sizeof(dst),sizeof(dst),0)==0);
    CHECK(sp11_securepd_camera_process_packet(&p,&ops,&m,&r)==SP11_SECUREPD_CAMERA_EINVAL);

    /* Verification failure maps nothing. */
    CHECK(sp11_securepd_camera_build_packet(&p,m.src_token,sizeof(src),m.dst_token,sizeof(dst),m.work_token,sizeof(work),8,8,10,0,sizeof(dst),sizeof(dst),0)==0);
    m.verify_count=m.map_count=m.unmap_count=0; m.verify_fail_token=(int)m.dst_token;
    CHECK(sp11_securepd_camera_process_packet(&p,&ops,&m,&r)==SP11_SECUREPD_CAMERA_EVERIFY); CHECK(m.map_count==0); CHECK(m.unmap_count==0); m.verify_fail_token=0;

    /* Destination-map failure cleans the source map. */
    m.verify_count=m.map_count=m.unmap_count=0; m.map_fail_token=(int)m.dst_token;
    CHECK(sp11_securepd_camera_process_packet(&p,&ops,&m,&r)==SP11_SECUREPD_CAMERA_EMAP); CHECK(m.unmap_count==1); CHECK(m.unmap_order[0]==m.src_token); m.map_fail_token=0;

    /* Successful work with an unmap failure reports cleanup failure after attempting all unmaps. */
    m.verify_count=m.map_count=m.unmap_count=0; m.unmap_fail_token=(int)m.dst_token;
    CHECK(sp11_securepd_camera_process_packet(&p,&ops,&m,&r)==SP11_SECUREPD_CAMERA_EUNMAP); CHECK(m.unmap_count==3); CHECK(r.cleanup_status==-9); m.unmap_fail_token=0;

    if(failures)return 1; puts("E004di SecurePD adapter vectors: PASS"); return 0;
}
