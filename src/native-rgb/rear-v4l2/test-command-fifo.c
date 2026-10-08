/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual staged wait/commit/current helpers; IRQ/MMIO/timeouts explicitly modelled. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint32_t u32;typedef uint16_t u16;
#define BIT(n) (1U<<(n))
#define U32_MAX UINT32_MAX
#define U16_MAX UINT16_MAX
#define READ_ONCE(x) (x)
#define WRITE_ONCE(x,v) ((x)=(v))
#define CAMSS_RTCDM_IRQ_BL_DONE BIT(2)
#define CAMSS_RTCDM_IRQ_KNOWN 0x70007U
#define CAMSS_RTCDM_WINDOWS_WAIT_MS 100
#define CAMSS_RTCDM_WINDOWS_FIFO_LOW20 0xfffffU
#define CAMSS_RTCDM_WINDOWS_FIFO_LEN_HIGH 0x100000U
#define CAMSS_RTCDM_FIFO0_BASE 0
#define CAMSS_RTCDM_FIFO0_LEN 4
#define CAMSS_RTCDM_FIFO0_STORE 8
#define CAMSS_RTCDM_DIAG_FIFO_WAIT 1
#define CAMSS_RTCDM_DIAG_FIFO_DONE 2
#include "native-rear-command-receipt.h"
static unsigned assertions,negative_cases,writes,synchronizations,order[3];
#define CHECK(x) do{assertions++;if(!(x)){fprintf(stderr,"FAIL:%d %s\n",__LINE__,#x);exit(2);}}while(0)
struct camss_rtcdm {bool present,irq_armed,faulted;unsigned char *base;int lock,completion;unsigned irq;
 u32 last_irq_context,last_irq_status,last_irq_status1,last_irq_status2,last_irq_status3,last_user_data;
 u32 diag_fifo_seq,diag_base,diag_len_low20;};
struct camss {struct camss_rtcdm rtcdm1;};
static struct camss cam;
static unsigned char registers[12];
static int timeout_kind,sync_kind;
static void mutex_lock(int *p){CHECK(*p==0);*p=1;}
static void mutex_unlock(int *p){CHECK(*p==1);*p=0;}
static void reinit_completion(int *p){*p=0;}
static unsigned long msecs_to_jiffies(unsigned long t){return t;}
static unsigned long wait_for_completion_timeout(int *p,unsigned long t){
 CHECK(p==&cam.rtcdm1.completion&&cam.rtcdm1.lock==1&&t==100);
 if(timeout_kind==1)return 0;
 cam.rtcdm1.last_irq_status=CAMSS_RTCDM_IRQ_BL_DONE;
 if(timeout_kind==2)cam.rtcdm1.faulted=true;
 if(timeout_kind==3)cam.rtcdm1.last_irq_status=0;
 if(timeout_kind==4)cam.rtcdm1.last_irq_status|=BIT(30);
 if(timeout_kind==5)cam.rtcdm1.last_irq_status|=BIT(1);
 return 1;
}
static void camss_rtcdm1_diag_set(struct camss *c,int stage,u32 required,int error){
 CHECK(c==&cam&&cam.rtcdm1.lock==1&&required==BIT(2));
 CHECK(stage==1||stage==2);(void)error;
}
static void writel_relaxed(u32 value,void *addr){
 CHECK(cam.rtcdm1.lock==1&&writes<3);
 order[writes++]=(unsigned)((unsigned char*)addr-registers);
 memcpy(addr,&value,4);
}
static void synchronize_irq(unsigned irq){
 CHECK(irq==19&&cam.rtcdm1.lock==1);synchronizations++;
 switch(sync_kind){
  case 1:cam.rtcdm1.irq_armed=false;break;
  case 2:cam.rtcdm1.faulted=true;break;
  case 3:cam.rtcdm1.last_irq_status=0;break;
  case 4:cam.rtcdm1.diag_base++;break;
  case 5:cam.rtcdm1.diag_len_low20++;break;
  case 6:cam.rtcdm1.diag_fifo_seq=0;break;
  case 7:cam.rtcdm1.last_irq_status|=BIT(0);break;
 }
}
#include "actual-fifo-functions.h"
static void fixture(void){
 memset(&cam,0,sizeof(cam));memset(registers,0,sizeof(registers));
 cam.rtcdm1.present=cam.rtcdm1.irq_armed=true;cam.rtcdm1.base=registers;cam.rtcdm1.irq=19;
 writes=synchronizations=0;timeout_kind=sync_kind=0;
}
static bool zero(const struct native_rear_bl_receipt *r){
 return !r->sequence&&!r->dma&&!r->bytes&&!r->irq_status&&!r->complete;
}
int main(void){
 struct native_rear_bl_receipt r,saved;
 fixture();
 for(unsigned i=0;i<22;i++){
  writes=0;
  CHECK(e008k_rear_rtcdm_submit_bl_receipt(&cam,0x1000+i*4,4,&r)==0);
  CHECK(r.complete&&r.sequence==i+1&&r.dma==0x1000+i*4&&r.bytes==4&&r.irq_status==BIT(2));
  CHECK(writes==3&&order[0]==0&&order[1]==4&&order[2]==8);
  CHECK(e008k_rear_rtcdm_receipt_current(&cam,&r)==0);
 }
 for(unsigned f=0;f<20;f++){
  fixture();memset(&r,0xff,sizeof(r));u32 dma=0x1000,len=3;
  switch(f){
   case 0:cam.rtcdm1.present=false;break;case 1:cam.rtcdm1.base=NULL;break;
   case 2:dma=0;break;case 3:len=0;break;case 4:len=0x100000;break;
   case 5:cam.rtcdm1.irq_armed=false;break;case 6:cam.rtcdm1.faulted=true;break;
   case 7:cam.rtcdm1.diag_fifo_seq=U32_MAX;break;
   case 8:timeout_kind=1;break;case 9:timeout_kind=2;break;
   case 10:timeout_kind=3;break;case 11:timeout_kind=4;break;
   case 12:timeout_kind=5;break;
   default:sync_kind=(int)f-12;break;
  }
  CHECK(camss_rtcdm1_windows_fifo0_commit_receipt(&cam,dma,len,&r)<0);
  CHECK(zero(&r)&&cam.rtcdm1.lock==0);negative_cases++;
  if(f<8)CHECK(writes==0);
 }
 fixture();CHECK(e008k_rear_rtcdm_submit_bl_receipt(&cam,0x1000,4,&r)==0);saved=r;
 for(unsigned f=0;f<13;f++){
  fixture();cam.rtcdm1.diag_fifo_seq=saved.sequence;cam.rtcdm1.diag_base=saved.dma;
  cam.rtcdm1.diag_len_low20=saved.bytes-1;cam.rtcdm1.last_irq_status=BIT(2);r=saved;
  switch(f){
   case 0:r.complete=false;break;case 1:r.sequence=0;break;case 2:r.dma=0;break;
   case 3:r.bytes=0;break;case 4:r.irq_status=0;break;case 5:r.sequence++;break;
   case 6:r.dma++;break;case 7:r.bytes++;break;
   case 8:cam.rtcdm1.irq_armed=false;break;case 9:cam.rtcdm1.faulted=true;break;
   case 10:cam.rtcdm1.last_irq_status|=BIT(1);break;
   case 11:cam.rtcdm1.present=false;break;case 12:cam.rtcdm1.base=NULL;break;
  }
  CHECK(e008k_rear_rtcdm_receipt_current(&cam,&r)<0);CHECK(writes==0&&cam.rtcdm1.lock==0);negative_cases++;
 }
 for(unsigned f=1;f<=7;f++){
  fixture();cam.rtcdm1.diag_fifo_seq=saved.sequence;cam.rtcdm1.diag_base=saved.dma;
  cam.rtcdm1.diag_len_low20=saved.bytes-1;cam.rtcdm1.last_irq_status=BIT(2);sync_kind=f;
  CHECK(e008k_rear_rtcdm_receipt_current(&cam,&saved)<0);CHECK(writes==0&&cam.rtcdm1.lock==0);negative_cases++;
 }
 fixture();cam.rtcdm1.diag_fifo_seq=U32_MAX;
 CHECK(camss_rtcdm1_windows_fifo0_commit(&cam,0x1000,3)==0);CHECK(cam.rtcdm1.diag_fifo_seq==0);CHECK(synchronizations==0);
 fixture();CHECK(e008k_rear_rtcdm_submit_bl_receipt(&cam,0x1000,4,NULL)==-EINVAL);CHECK(writes==0);
 fixture();memset(&r,0xff,sizeof(r));CHECK(e008k_rear_rtcdm_submit_bl_receipt(NULL,0x1000,4,&r)==-EINVAL);CHECK(zero(&r));
 printf("{\"assertions\":%u,\"negative_cases\":%u,\"actual_FIFO_commit_wait_and_current_check\":true}\n",assertions,negative_cases);
 return 0;
}
