/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
typedef uint8_t u8;typedef uint32_t u32;typedef uint64_t u64;
#include "native-rear-stats.h"
#define VFE_LINE_PIX 0
#define E008D_REAR_AUX_COUNT 8
struct camss_video{void *native_rear_inflight[2];u32 native_rear_completed;u64 native_rear_statistics_tick;};
struct vfe_device{struct{struct camss_video video_out;}line[1];};
struct e008d_rear_aux_buffer{void *cpu;u64 dma;size_t size;u8 wm;};
struct e008d_rear_dma_set{struct e008d_rear_aux_buffer aux[8];bool allocated,auxiliary_live_retired;};
struct e007z_rear_frame{bool active,pending,faulted;u64 owner_epoch,request_generation;struct{u64 owned_base_iova;size_t owned_bytes;}slot[10];};
struct e008h_rear_prime_pair{struct e008d_rear_dma_set dma[2];struct e007z_rear_frame frame[2];};
struct e008k_rear_result{bool both_frames_complete,live_full_retired,live_aux_retired;u64 owner_epoch;};
static unsigned calls,barriers,checks,negatives;
static int reply;
static int e007z_rear_index(u8 wm){for(unsigned i=0;i<6;i++)if(wm==native_rear_stats_wm(i))return i+2;return -1;}
#define dma_rmb() do{barriers++;}while(0)
static u64 ktime_get_ns(void){return 12345;}
static int camss_x1e_rear_meta_publish(struct camss_video *video,u64 owner,u64 generation,u32 cursor,u64 ts,const void *const p[6],const size_t n[6]){
 calls++;if(!video||owner!=7||generation!=1||cursor!=37||ts!=12345)abort();
 for(unsigned i=0;i<6;i++)if(!p[i]||n[i]!=native_rear_stats_capacity[i])abort();
 return reply;
}
#include "native-rear-statistics-copy.inc"
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"check %u line %d\n",checks,__LINE__);abort();}}while(0)
int main(void){
 struct vfe_device v={0};struct e008h_rear_prime_pair pair={0};
 struct e008k_rear_result r={true,true,false,7};
 v.line[0].video_out.native_rear_inflight[0]=(void *)(uintptr_t)1;
 pair.dma[0].allocated=true;pair.frame[0].active=true;
 pair.frame[0].owner_epoch=7;pair.frame[0].request_generation=1;
 for(unsigned i=0;i<6;i++){
  pair.dma[0].aux[i]=(struct e008d_rear_aux_buffer){(void *)(uintptr_t)(100+i),0x100000+i*0x200000,native_rear_stats_capacity[i],native_rear_stats_wm(i)};
  pair.frame[0].slot[i+2].owned_base_iova=pair.dma[0].aux[i].dma;
  pair.frame[0].slot[i+2].owned_bytes=pair.dma[0].aux[i].size;
 }
 struct e008h_rear_prime_pair original=pair;
 for(unsigned i=0;i<6;i++){
  pair=original;pair.dma[0].aux[i].cpu=NULL;CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
  pair=original;pair.dma[0].aux[i].size--;CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
  pair=original;pair.dma[0].aux[i].dma++;CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
 }
 pair=original;pair.frame[0].owner_epoch=8;CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
 pair=original;pair.frame[0].request_generation=2;CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
 pair=original;pair.frame[0].pending=true;CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
 pair=original;pair.dma[0].aux[6]=pair.dma[0].aux[0];CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
 CHECK(calls==0&&barriers==0&&v.line[0].video_out.native_rear_statistics_tick==0);
 pair=original;reply=-EIO;
 CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)==-EIO);
 CHECK(calls==1&&barriers==1&&v.line[0].video_out.native_rear_statistics_tick==0);
 reply=0;
 CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)==0);
 CHECK(calls==2&&barriers==2&&v.line[0].video_out.native_rear_statistics_tick==12345);
 CHECK(memcmp(&pair,&original,sizeof(pair))==0);
 CHECK(native_rear_statistics_before_aux_release(&v,&pair,&r,37)!=0);negatives++;
 CHECK(calls==2&&barriers==2);
 printf("{\"status\":\"PASS_REAR_STATISTICS_COPY_ADMISSION\",\"assertions\":%u,\"negative_cases\":%u}\n",checks,negatives);
}
