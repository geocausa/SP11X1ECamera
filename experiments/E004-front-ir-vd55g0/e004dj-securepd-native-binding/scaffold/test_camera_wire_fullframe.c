#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "sp11-securepd-camera-wire.h"
#define W 644u
#define H 604u
#define ST 0x11110000ULL
#define DT 0x22220000ULL
#define HT 0x33330000ULL
struct ctx{uint8_t*src,*dst,*heap;};
static int verify(void*c,uint64_t p,uint32_t n,int32_t t,uint32_t a){(void)c;(void)n;(void)a;return ((p==ST||p==DT)&&t==7)||(p==HT&&t==5)?0:-1;}
static int map(void*c,uint64_t p,uint32_t n,uint32_t a,uint64_t*v){struct ctx*x=c;void*q=p==ST?x->src:p==DT?x->dst:p==HT?x->heap:0;(void)n;(void)a;if(!q)return-1;*v=(uint64_t)(uintptr_t)q;return 0;}
static int unmap(void*c,uint64_t v,uint32_t n){(void)c;(void)v;(void)n;return 0;}
static int rd(const char*p,uint8_t*b,size_t n){FILE*f=fopen(p,"rb");size_t g;if(!f)return-1;g=fread(b,1,n,f);fclose(f);return g==n?0:-1;}
int main(int argc,char**argv){
 const size_t y=(size_t)W*H,frame=y+y/2,heapn=sp11_securepd_camera_heap_required(W,H);size_t i,ld=0,td=0;uint8_t*src,*win,*dst,*heap;struct ctx c;struct sp11_securepd_gaussian_packet p={0};struct sp11_securepd_camera_map_ops ops={verify,map,unmap};sp11_securepd_camera_response_t resp;int r;
 if(argc!=3)return 2;src=malloc(frame);win=malloc(frame);dst=malloc(frame);heap=malloc(heapn);if(!src||!win||!dst||!heap)return 3;if(rd(argv[1],src,frame)||rd(argv[2],win,frame))return 4;memset(dst,0xa5,frame);memset(heap,0,heapn);c.src=src;c.dst=dst;c.heap=heap;
 p.src.addr=ST;p.src.size=frame;p.src_width=W;p.src_height=H;p.src_stride=W;p.dst.addr=DT;p.dst.size=frame;p.dst_stride=W;p.heap.addr=HT;p.heap.size=heapn;sp11_securepd_camera_init_control((void*)heap,10,0,frame,frame,0);
 r=sp11_securepd_camera_process_gaussian_packet(&p,&ops,&c,&resp);if(r){fprintf(stderr,"wire=%d response=%llu\n",r,(unsigned long long)resp);return 5;}for(i=0;i<y;i++)if(dst[i]!=win[i])ld++;for(i=y;i<frame;i++)if(dst[i]!=0x80)td++;printf("GAUSSIAN_WIRE_FULL_LUMA_DIFF=%zu\nGAUSSIAN_WIRE_NEUTRAL_TAIL_DIFF=%zu\n",ld,td);return(ld||td)?1:0;
}
