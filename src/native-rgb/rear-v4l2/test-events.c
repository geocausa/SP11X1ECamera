/* SPDX-License-Identifier: GPL-2.0-only */
/* Hosted actual event queue. MMIO, route and IRQ drain are explicit mocks. */
#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <sched.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint64_t u64;
#define U32_MAX UINT32_MAX
#define CSID_IPP_CAMIF_EPOCH0 (1U << 6)
#define READ_ONCE(x) __atomic_load_n(&(x), __ATOMIC_RELAXED)
#define WRITE_ONCE(x,v) __atomic_store_n(&(x),(v),__ATOMIC_RELAXED)
#define smp_load_acquire(p) __atomic_load_n((p),__ATOMIC_ACQUIRE)
#define smp_store_release(p,v) __atomic_store_n((p),(v),__ATOMIC_RELEASE)
#define read_poll_timeout(op,val,cond,delay,timeout,initial,arg) \
 ({ (void)(delay); (void)(timeout); (void)(initial); (val)=op(arg); (cond)?0:-ETIMEDOUT; })
#include "camss-e008i-rear-observer.h"
struct vfe_device {int dummy;};
struct camss {struct vfe_device vfe[2];};
struct csid_device {
 struct camss *camss;bool rear_mode;unsigned int irq;
 u64 e008i_rear_owner_epoch;
 u32 e008i_rear_epoch0_count,e008i_rear_done_count,native_rear_done_consumed;
 u32 e008i_rear_done_overflow,e008i_rear_latch_errors;
 struct e008i_rear_done_event e008i_rear_done[E008I_REAR_DONE_DEPTH];
};
static uint64_t assertions;
static unsigned int irq_drains,sample_index;
static int sample_fail;
static struct camss board;
static struct csid_device device;
#define CHECK(x) do {__atomic_fetch_add(&assertions,1,__ATOMIC_RELAXED); if(!(x)){\
 fprintf(stderr,"FAIL line=%d expression=%s\n",__LINE__,#x);abort();}}while(0)
static bool csid_e004ns_rear_ipp_mode0(struct csid_device *c){return c&&c->rear_mode;}
static void synchronize_irq(unsigned int irq){CHECK(irq==7);irq_drains++;}
int vfe680_e008i_rear_snapshot_addr_status0(struct vfe_device *v,u32 status,
                                          u16 *mask,u32 address[E008I_REAR_WMS])
{
 CHECK(v==&board.vfe[1]&&(status&E008I_REAR_BUF_DONE_MASK));
 if(sample_fail)return sample_fail;
 *mask=(1U<<E008I_REAR_WMS)-1;
 for(unsigned int i=0;i<E008I_REAR_WMS;i++)
  address[i]=0x100000U+sample_index*0x1000U+i*0x40U;
 sample_index++;
 return 0;
}
#include "native-rear-event-queue.inc"
static void reset(void)
{
 device.camss=&board;device.rear_mode=true;device.irq=7;sample_index=0;sample_fail=0;
 unsigned int before=irq_drains;
 CHECK(csid680_e008i_rear_reset(&device,77)==0);
 CHECK(irq_drains==before+1);
 CHECK(device.e008i_rear_owner_epoch==77&&device.e008i_rear_done_count==0&&
       device.native_rear_done_consumed==0&&!device.e008i_rear_done_overflow&&
       !device.e008i_rear_latch_errors&&!device.e008i_rear_epoch0_count);
}
static void produce(void){e008i_rear_latch_buf_done(&device,E008I_REAR_BUF_DONE_MASK);}
static void read_and_retire(u32 index)
{
 struct e008i_rear_done_event event={0};
 CHECK(csid680_e008i_rear_done_event(&device,index,&event)==0);
 CHECK(event.sequence==index+1&&event.owner_epoch==77&&event.wm_mask==0x3ff);
 for(unsigned int i=0;i<E008I_REAR_WMS;i++)
  CHECK(event.addr_status0[i]==0x100000U+index*0x1000U+i*0x40U);
 CHECK(csid680_e008i_rear_retire_event(&device,index,77)==0);
 CHECK(smp_load_acquire(&device.native_rear_done_consumed)==index+1);
}
static void negatives(void)
{
 struct e008i_rear_done_event event;
 reset();
 CHECK(csid680_e008i_rear_done_event(&device,0,&event)==-ENOENT);
 CHECK(csid680_e008i_rear_done_event(NULL,0,&event)==-EINVAL);
 CHECK(csid680_e008i_rear_done_event(&device,0,NULL)==-EINVAL);
 CHECK(csid680_e008i_rear_retire_event(&device,0,77)==-ENOENT);
 CHECK(csid680_e008i_rear_reset(&device,0)==-EINVAL);
 device.rear_mode=false;produce();e008i_rear_latch_ipp(&device,CSID_IPP_CAMIF_EPOCH0);
 CHECK(device.e008i_rear_done_count==0&&device.e008i_rear_epoch0_count==0);
 CHECK(csid680_e008i_rear_done_event(&device,0,&event)==-EINVAL);
 device.rear_mode=true;
 e008i_rear_latch_buf_done(&device,0);
 CHECK(device.e008i_rear_done_count==0);
 produce();
 CHECK(csid680_e008i_rear_retire_event(&device,1,77)==-ESTALE);
 CHECK(csid680_e008i_rear_retire_event(&device,0,78)==-ESTALE);
 CHECK(csid680_e008i_rear_retire_event(&device,0,0)==-ESTALE);
 CHECK(device.native_rear_done_consumed==0);
 struct e008i_rear_done_event good=device.e008i_rear_done[0];
 for(unsigned int field=0;field<6;field++){
  device.e008i_rear_done[0]=good;
  switch(field){
  case 0:device.e008i_rear_done[0].owner_epoch=78;break;
  case 1:device.e008i_rear_done[0].sequence=2;break;
  case 2:device.e008i_rear_done[0].wm_mask=0;break;
  case 3:device.e008i_rear_done[0].wm_mask=0x400;break;
  case 4:device.e008i_rear_done[0].reserved=1;break;
  default:device.e008i_rear_done[0].raw_buf_done_status=0;break;
  }
  CHECK(csid680_e008i_rear_done_event(&device,0,&event)==-EPROTO);
  CHECK(csid680_e008i_rear_retire_event(&device,0,77)==-EPROTO);
  CHECK(device.native_rear_done_consumed==0);
 }
 device.e008i_rear_done[0]=good;
 read_and_retire(0);
 CHECK(csid680_e008i_rear_done_event(&device,0,&event)==-ESTALE);
 CHECK(csid680_e008i_rear_retire_event(&device,0,77)==-ESTALE);
 WRITE_ONCE(device.native_rear_done_consumed,2);
 CHECK(csid680_e008i_rear_done_event(&device,1,&event)==-EPROTO);
 reset();
 for(unsigned int i=0;i<16;i++)produce();
 CHECK(device.e008i_rear_done_count==16&&!device.e008i_rear_done_overflow);
 produce();
 CHECK(device.e008i_rear_done_count==16&&device.e008i_rear_done_overflow==1&&
       device.native_rear_done_consumed==0);
 CHECK(csid680_e008i_rear_done_event(&device,0,&event)==-EOVERFLOW);
 CHECK(csid680_e008i_rear_retire_event(&device,0,77)==-EOVERFLOW);
 CHECK(csid680_e008i_rear_poll_done(&device,0,100)==-EOVERFLOW);
 CHECK(csid680_e008i_rear_poll_next_epoch0(&device,0,100)==-EOVERFLOW);
 reset();sample_fail=-EIO;produce();
 CHECK(device.e008i_rear_done_count==0&&device.e008i_rear_latch_errors==1);
 CHECK(csid680_e008i_rear_done_event(&device,0,&event)==-EOVERFLOW);
 reset();
 WRITE_ONCE(device.e008i_rear_done_count,U32_MAX);
 WRITE_ONCE(device.native_rear_done_consumed,U32_MAX);
 produce();
 CHECK(device.e008i_rear_done_count==U32_MAX&&device.e008i_rear_done_overflow==1);
 reset();WRITE_ONCE(device.e008i_rear_epoch0_count,U32_MAX);
 e008i_rear_latch_ipp(&device,CSID_IPP_CAMIF_EPOCH0);
 CHECK(device.e008i_rear_epoch0_count==U32_MAX&&device.e008i_rear_latch_errors==1);
 CHECK(csid680_e008i_rear_poll_next_epoch0(&device,U32_MAX,100)==-EOVERFLOW);
 reset();
 CHECK(csid680_e008i_rear_poll_next_epoch0(&device,0,100)==-ETIMEDOUT);
 e008i_rear_latch_ipp(&device,CSID_IPP_CAMIF_EPOCH0);
 CHECK(csid680_e008i_rear_poll_next_epoch0(&device,0,100)==0);
 e008i_rear_latch_ipp(&device,CSID_IPP_CAMIF_EPOCH0);
 CHECK(csid680_e008i_rear_poll_next_epoch0(&device,0,100)==-EPROTO);
 CHECK(csid680_e008i_rear_poll_done(&device,0,100)==-ETIMEDOUT);
 produce();CHECK(csid680_e008i_rear_poll_done(&device,0,100)==0);
}
static void wraps(void)
{
 reset();
 for(unsigned int i=0;i<14;i++)produce();
 for(unsigned int i=0;i<7;i++)read_and_retire(i);
 for(unsigned int i=14;i<23;i++)produce();
 CHECK(csid680_e008i_rear_done_count(&device)==23);
 CHECK(csid680_e008i_rear_done_overflow(&device)==0);
 for(unsigned int i=7;i<23;i++)read_and_retire(i);
 for(unsigned int i=23;i<1024;i++){produce();read_and_retire(i);}
 CHECK(device.e008i_rear_done_count==1024&&device.native_rear_done_consumed==1024);
}
#define THREADED_EVENTS 4096U
static void *producer(void *unused)
{
 (void)unused;
 for(u32 i=0;i<THREADED_EVENTS;i++){
  while(smp_load_acquire(&device.e008i_rear_done_count)-
        smp_load_acquire(&device.native_rear_done_consumed)>=16)sched_yield();
  produce();
 }
 return NULL;
}
static void *consumer(void *unused)
{
 (void)unused;
 for(u32 i=0;i<THREADED_EVENTS;i++){
  while(csid680_e008i_rear_done_count(&device)<=i)sched_yield();
  read_and_retire(i);
 }
 return NULL;
}
int main(void)
{
 negatives();wraps();reset();
 pthread_t irq_thread,runner_thread;
 CHECK(!pthread_create(&irq_thread,NULL,producer,NULL));
 CHECK(!pthread_create(&runner_thread,NULL,consumer,NULL));
 CHECK(!pthread_join(irq_thread,NULL));
 CHECK(!pthread_join(runner_thread,NULL));
 CHECK(device.e008i_rear_done_count==THREADED_EVENTS&&
       device.native_rear_done_consumed==THREADED_EVENTS&&
       !device.e008i_rear_done_overflow&&!device.e008i_rear_latch_errors);
 printf("{\"assertions\":%" PRIu64 ",\"sequential_wrap_events\":1024,"
        "\"concurrent_events\":4096,\"capacity\":16,\"event_storage_reuse_only\":true,"
        "\"hardware_MMIO_IRQ_route_are_mocks\":true}\n",READ_ONCE(assertions));
 return 0;
}
