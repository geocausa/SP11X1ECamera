#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "sp11-securepd-camera-wire.h"

static int failures;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL %s:%d %s\n",__FILE__,__LINE__,#x);failures++;}}while(0)

struct mock {
    uint8_t *src,*dst,*heap;
    uint64_t st,dt,ht;
    int verify_count,map_count,unmap_count;
    int types[3]; uint64_t unmap_order[3];
    uint64_t fail_verify,fail_map,fail_unmap;
};
static uint8_t *ptr(struct mock*m,uint64_t t){return t==m->st?m->src:t==m->dt?m->dst:t==m->ht?m->heap:0;}
static int verify(void*c,uint64_t p,uint32_t n,int32_t type,uint32_t a){struct mock*m=c;(void)n;(void)a;if(m->verify_count<3)m->types[m->verify_count]=type;m->verify_count++;return p==m->fail_verify?-1:ptr(m,p)?0:-2;}
static int map(void*c,uint64_t p,uint32_t n,uint32_t a,uint64_t*v){struct mock*m=c;uint8_t*q;(void)n;(void)a;m->map_count++;if(p==m->fail_map)return-1;q=ptr(m,p);if(!q)return-2;*v=(uint64_t)(uintptr_t)q;return 0;}
static int unmap(void*c,uint64_t v,uint32_t n){struct mock*m=c;uint64_t t=0;(void)n;if((void*)(uintptr_t)v==m->src)t=m->st;if((void*)(uintptr_t)v==m->dst)t=m->dt;if((void*)(uintptr_t)v==m->heap)t=m->ht;if(m->unmap_count<3)m->unmap_order[m->unmap_count]=t;m->unmap_count++;return t==m->fail_unmap?-9:0;}
static void packet(struct sp11_securepd_gaussian_packet*p,struct mock*m,uint32_t heapn){memset(p,0,sizeof(*p));p->src.size=64;p->src.addr=m->st;p->src_width=8;p->src_height=8;p->src_stride=8;p->dst.size=96;p->dst.addr=m->dt;p->dst_stride=8;p->heap.size=heapn;p->heap.addr=m->ht;}
int main(void){
    uint8_t src[64],dst[96],heap[352]; struct mock m={0}; struct sp11_securepd_gaussian_packet p; struct sp11_securepd_camera_control*c=(void*)heap; struct sp11_securepd_camera_map_ops ops={verify,map,unmap}; sp11_securepd_camera_response_t resp; int i,r;
    memset(src,42,sizeof(src));memset(dst,0,sizeof(dst));memset(heap,0,sizeof(heap));m.src=src;m.dst=dst;m.heap=heap;m.st=0x11110000;m.dt=0x22220000;m.ht=0x33330000;
    CHECK(sizeof(struct sp11_securepd_gaussian_packet)==96);CHECK(sizeof(*c)==32);CHECK(sp11_securepd_camera_heap_required(8,8)==352);
    packet(&p,&m,sizeof(heap));sp11_securepd_camera_init_control(c,10,0,sizeof(dst),sizeof(dst),0);
    r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==0);CHECK(resp==0);CHECK(m.verify_count==3&&m.map_count==3&&m.unmap_count==3);CHECK(m.types[0]==7&&m.types[1]==7&&m.types[2]==5);CHECK(m.unmap_order[0]==m.ht&&m.unmap_order[1]==m.dt&&m.unmap_order[2]==m.st);for(i=0;i<64;i++)CHECK(dst[i]==42);for(i=64;i<96;i++)CHECK(dst[i]==0x80);
    /* Control metadata, not proxy stride/offset abuse, selects early copy. */
    memset(dst,0,sizeof(dst));m.verify_count=m.map_count=m.unmap_count=0;sp11_securepd_camera_init_control(c,9,0,sizeof(dst),sizeof(dst),0);r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==0&&resp==0);CHECK(memcmp(dst,src,64)==0);for(i=64;i<96;i++)CHECK(dst[i]==0x80);
    /* Synthetic selection also lives in protected control header. */
    memset(dst,0,sizeof(dst));sp11_securepd_camera_init_control(c,0,0,sizeof(dst),sizeof(dst),1);r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==0);for(i=0;i<64;i++)CHECK(dst[i]==100);
    /* Bad control is rejected after trusted map, then all maps are removed. */
    c->magic=0;m.verify_count=m.map_count=m.unmap_count=0;r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==SP11_SECUREPD_WIRE_ECONTROL);CHECK(resp!=0);CHECK(m.unmap_count==3);
    /* Verification failure maps nothing. */
    sp11_securepd_camera_init_control(c,10,0,sizeof(dst),sizeof(dst),0);m.verify_count=m.map_count=m.unmap_count=0;m.fail_verify=m.dt;r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==SP11_SECUREPD_WIRE_EVERIFY);CHECK(m.map_count==0&&m.unmap_count==0);m.fail_verify=0;
    /* Partial map failure reverses prior map. */
    m.verify_count=m.map_count=m.unmap_count=0;m.fail_map=m.dt;r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==SP11_SECUREPD_WIRE_EMAP);CHECK(m.unmap_count==1&&m.unmap_order[0]==m.st);m.fail_map=0;
    /* Cleanup failure is returned after successful worker execution. */
    m.verify_count=m.map_count=m.unmap_count=0;m.fail_unmap=m.dt;r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&m,&resp);CHECK(r==SP11_SECUREPD_WIRE_EUNMAP);CHECK(resp!=0&&m.unmap_count==3);m.fail_unmap=0;
    if(failures)return 1;puts("E004dj Gaussian-wire vectors: PASS");return 0;
}
