#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "sp11-securepd-camera-worker.h"
#define W 644u
#define H 604u
#define SRC_TOKEN 0x1000u
#define DST_TOKEN 0x2000u
#define WORK_TOKEN 0x3000u
struct ctx { uint8_t *src,*dst,*work; };
static int verify(void *c,uint32_t p,uint32_t n,int32_t t,uint32_t a){(void)c;(void)n;(void)a;return ((p==SRC_TOKEN||p==DST_TOKEN)&&t==SP11_SECUREPD_DATA)||(p==WORK_TOKEN&&t==SP11_SECUREPD_HEAP)?0:-1;}
static int map(void *c,uint32_t p,uint32_t n,uint32_t a,uint64_t *v){struct ctx*x=c;(void)n;(void)a;void*q=p==SRC_TOKEN?x->src:p==DST_TOKEN?x->dst:p==WORK_TOKEN?x->work:0;if(!q)return-1;*v=(uint64_t)(uintptr_t)q;return 0;}
static int unmap(void*c,uint64_t v,uint32_t n){(void)c;(void)v;(void)n;return 0;}
static int read_exact(const char *p,uint8_t*b,size_t n){FILE*f=fopen(p,"rb");size_t g;if(!f)return-1;g=fread(b,1,n,f);fclose(f);return g==n?0:-1;}
int main(int argc,char**argv){
 const size_t y=(size_t)W*H, frame=y+y/2, workn=sp11_securepd_camera_required_work(W,H); size_t i,ld=0,td=0;
 uint8_t *src,*win,*dst,*work; struct ctx c; struct sp11_securepd_camera_packet p; struct sp11_securepd_camera_result r; struct sp11_securepd_camera_map_ops ops={verify,map,unmap}; int ret;
 if(argc!=3)return 2; src=malloc(frame);win=malloc(frame);dst=malloc(frame);work=malloc(workn);if(!src||!win||!dst||!work)return 3;
 if(read_exact(argv[1],src,frame)||read_exact(argv[2],win,frame))return 4; memset(dst,0xa5,frame); c.src=src;c.dst=dst;c.work=work;
 if(sp11_securepd_camera_build_packet(&p,SRC_TOKEN,(uint32_t)frame,DST_TOKEN,(uint32_t)frame,WORK_TOKEN,(uint32_t)workn,W,H,10,0,(uint32_t)frame,(uint32_t)frame,0))return 5;
 ret=sp11_securepd_camera_process_packet(&p,&ops,&c,&r); if(ret){fprintf(stderr,"adapter=%d worker=%d cleanup=%d\n",ret,r.worker_status,r.cleanup_status);return 6;}
 for(i=0;i<y;i++)if(dst[i]!=win[i])ld++; for(i=y;i<frame;i++)if(dst[i]!=0x80)td++;
 printf("SECUREPD_ADAPTER_FULL_LUMA_DIFF=%zu\nSECUREPD_ADAPTER_NEUTRAL_TAIL_DIFF=%zu\n",ld,td); return(ld||td)?1:0;
}
