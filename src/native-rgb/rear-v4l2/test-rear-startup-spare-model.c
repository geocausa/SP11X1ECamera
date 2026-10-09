/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual startup helper with explicit hardware-API models and fault injection. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef unsigned long long u64;
#define U64_MAX UINT64_MAX
#define GFP_KERNEL 0
#define E007Z_REAR_WMS 10
#define E008H_REAR_SLOTS 2
#define VFE_LINE_PIX 0
#define READ_ONCE(x) (x)
#define dev_info(dev,...) printf(__VA_ARGS__)
#define spin_lock_irqsave(lock,flags) ((void)(lock),(flags)=0)
#define spin_unlock_irqrestore(lock,flags) ((void)(lock),(void)(flags))
struct camss_buffer {int id;};
struct fake_list {struct camss_buffer *head;};
#define list_empty(p) (!(p)->head)
#define list_first_entry(p,type,member) ((p)->head)
struct lease {bool acquired,exposed,stop_proven;};
struct e008d_rear_dma_set {
 struct lease public_full;
 struct {bool in_flight;} full;
 bool allocated,prepared_disabled,public_full_retired,auxiliary_live_retired;
 int allocation;
};
struct e007z_rear_frame {u64 owner_epoch,request_generation;};
struct e008d_rear_addresses {int token;};
struct e007z_rear_binding {int token;};
struct native_rear_startup_spare;
struct e008h_rear_prime_pair {
 struct native_rear_startup_spare *startup_spare;
 struct e008d_rear_dma_set dma[2];
 struct e008d_rear_addresses addr[2];
 struct e007z_rear_frame frame[2];
 bool allocated,enabled,slot0_preloaded_disabled,faulted,ledgers_bound;
};
struct camss_video {bool x1e_pix_stop_requested;};
struct vfe_output {struct fake_list pending_bufs;};
struct camss {int dev;};
struct vfe_device {
 struct camss *camss;
 struct {struct camss_video video_out;struct vfe_output output;} line[1];
 int output_lock;
};
struct e008k_rear_request {struct camss_buffer *public_video[2];u64 first_request_generation;};
static int fail_heap,heap_calls,heaps_live,fail_stage,api_calls,allocated_live;
static int alloc_calls,free_calls,aliases_calls,command_calls,wait_calls,cache_dirty;
static struct vfe_device *wait_vfe;
static struct camss_buffer third={3};
static bool reject_api(void) {return ++api_calls==fail_stage;}
static void *model_kzalloc(size_t n,int g) {
 (void)g;if(++heap_calls==fail_heap)return NULL;
 void *p=calloc(1,n);assert(p);heaps_live++;return p;
}
static void model_kfree(void *p) {if(p){heaps_live--;free(p);}}
#define kzalloc model_kzalloc
#define kfree model_kfree
static bool native_rear_full_cache_idle(void) {return !cache_dirty;}
static bool native_rear_dma_full_valid(const struct e008d_rear_dma_set *d) {return d->allocated && d->public_full.acquired;}
static int native_rear_public_dma_alloc(struct vfe_device *v,struct e008d_rear_dma_set *d,struct camss_buffer *b) {
 (void)v;assert(b==&third);alloc_calls++;
 if(reject_api())return -ENOMEM;
 d->allocated=d->public_full.acquired=true;d->allocation=++allocated_live;return 0;
}
static void e008d_rear_release_partial(struct vfe_device *v,struct e008d_rear_dma_set *d) {
 (void)v;if(d->allocated){assert(d->public_full.acquired&&!d->public_full.exposed&&!d->full.in_flight);allocated_live--;free_calls++;}
 memset(d,0,sizeof(*d));
}
static int e008d_rear_build_addresses(struct vfe_device *v,struct e008d_rear_dma_set *d,struct e008d_rear_addresses *a) {
 (void)v;assert(d->allocated);if(reject_api())return -EPROTO;a->token=3;return 0;
}
static int e008h_rear_build_binding(struct e008h_rear_prime_pair *p,unsigned s,struct e007z_rear_binding *b) {
 assert(s==1 && p->dma[s].allocated);if(reject_api())return -EPROTO;b[0].token=3;return 0;
}
static int e007z_rear_bind(struct e007z_rear_frame *f,u64 o,u64 g,struct e007z_rear_binding *b) {
 assert(b[0].token==3);if(reject_api())return -EPROTO;f->owner_epoch=o;f->request_generation=g;return 0;
}
static int native_rear_queue_allocations_check(struct e008h_rear_prime_pair *p) {
 aliases_calls++;assert(p->dma[0].allocation==aliases_calls && p->dma[1].allocated);
 assert(p->frame[1].request_generation==3);return reject_api() ? -EADDRINUSE : 0;
}
static int native_rear_command_allocations_check(struct e008k_rear_request *r,struct e008h_rear_prime_pair *p,u64 o) {
 (void)r;command_calls++;assert(command_calls==aliases_calls && p->frame[1].owner_epoch==o);
 return reject_api() ? -EADDRINUSE : 0;
}
static void usleep_range(unsigned a,unsigned b) {
 assert(a==500 && b==1000);wait_calls++;
 if(wait_vfe)wait_vfe->line[0].output.pending_bufs.head=&third;
}
/* ACTUAL_HELPER */
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
static struct camss cam;
static struct vfe_device v;
static struct camss_buffer first={1},second={2};
static struct e008h_rear_prime_pair pair;
static struct e008k_rear_request req;
static void reset(void) {
 assert(!heaps_live && !allocated_live);
 memset(&pair,0,sizeof(pair));memset(&v,0,sizeof(v));v.camss=&cam;
 v.line[0].output.pending_bufs.head=&third;
 req=(struct e008k_rear_request){{&first,&second},1};
 pair.allocated=pair.ledgers_bound=true;
 for(unsigned i=0;i<2;i++){pair.dma[i].allocation=i+1;pair.frame[i].owner_epoch=2;pair.frame[i].request_generation=i+1;}
 fail_heap=heap_calls=fail_stage=api_calls=alloc_calls=free_calls=aliases_calls=command_calls=wait_calls=cache_dirty=0;wait_vfe=NULL;
}
static u64 ktime_get_ns(void); /* replaced before actual helper */
int main(void) {
 for(int fail=1;fail<=8;fail++) {
  reset();fail_stage=fail;
  CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)<0);
  CHECK(v.line[0].output.pending_bufs.head==&third);
  native_rear_startup_spare_release(&v,&pair,false);
  CHECK(!heaps_live&&!allocated_live&&!pair.startup_spare);
 }
 for(int fail=1;fail<=2;fail++) {
  reset();fail_heap=fail;CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)==-ENOMEM);
  native_rear_startup_spare_release(&v,&pair,false);CHECK(!heaps_live&&!allocated_live);
 }
 for(int bad=0;bad<8;bad++) {
  reset();
  if(bad==0)pair.enabled=true;
  if(bad==1)pair.faulted=true;
  if(bad==2)pair.allocated=false;
  if(bad==3)pair.ledgers_bound=false;
  if(bad==4)pair.slot0_preloaded_disabled=true;
  if(bad==5)req.first_request_generation=U64_MAX-1;
  if(bad==6)cache_dirty=1;
  CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,bad==7?0:2)==-EBUSY);
  CHECK(!heap_calls&&!alloc_calls&&!pair.startup_spare);
 }
 reset();v.line[0].video_out.x1e_pix_stop_requested=true;
 CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)==-ECANCELED);
 native_rear_startup_spare_release(&v,&pair,false);CHECK(!heaps_live&&!allocated_live);
 reset();v.line[0].output.pending_bufs.head=NULL;
 CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)==-ENOBUFS);CHECK(wait_calls==1000);
 native_rear_startup_spare_release(&v,&pair,false);CHECK(!heaps_live&&!allocated_live);
 reset();v.line[0].output.pending_bufs.head=&first;
 CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)==-EADDRINUSE);
 native_rear_startup_spare_release(&v,&pair,false);CHECK(!alloc_calls&&!heaps_live);
 reset();v.line[0].output.pending_bufs.head=NULL;wait_vfe=&v;
 CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)==0);
 CHECK(wait_calls==1&&aliases_calls==2&&command_calls==2&&alloc_calls==1&&allocated_live==1);
 CHECK(v.line[0].output.pending_bufs.head==&third); /* original FIFO preserved */
 struct native_rear_startup_spare *sp=pair.startup_spare;
 struct e008d_rear_dma_set dst={0};
 for(int bad=0;bad<11;bad++) {
  struct e008d_rear_dma_set saved=sp->dma;
  if(bad==0)sp->dma.public_full.acquired=false;
  if(bad==1)sp->dma.public_full.exposed=true;
  if(bad==2)sp->dma.public_full.stop_proven=true;
  if(bad==3)sp->dma.full.in_flight=true;
  if(bad==4)sp->dma.prepared_disabled=true;
  if(bad==5)sp->dma.public_full_retired=true;
  if(bad==6)sp->dma.auxiliary_live_retired=true;
  if(bad==7)dst.allocated=true;
  if(bad==8)dst.public_full.acquired=true;
  CHECK(native_rear_startup_spare_take(&pair,&dst,bad==9?&second:&third,bad==10?3:2)==-ESTALE);
  CHECK(!sp->taken&&sp->buffer==&third);sp->dma=saved;memset(&dst,0,sizeof(dst));
 }
 pair.frame[1].request_generation=3;
 CHECK(native_rear_startup_spare_take(&pair,&dst,&third,2)==-ESTALE);
 pair.frame[1].request_generation=2;
 CHECK(native_rear_startup_spare_take(&pair,&dst,&third,2)==0);
 CHECK(sp->taken&&!sp->buffer&&!sp->dma.allocated&&dst.allocated&&allocated_live==1);
 CHECK(native_rear_startup_spare_take(&pair,&sp->dma,&third,2)==-ENOENT);
 CHECK(free_calls==0&&allocated_live==1); /* failure/exposure owner stays held */
 e008d_rear_release_partial(&v,&dst); /* modeled later original strict retirement */
 native_rear_startup_spare_release(&v,&pair,true);
 CHECK(!heaps_live&&!allocated_live&&!pair.startup_spare&&free_calls==1);
 reset();CHECK(native_rear_startup_spare_prepare(&v,&pair,&req,2)==0);
 native_rear_startup_spare_release(&v,&pair,true);CHECK(!heaps_live&&!allocated_live&&free_calls==1);
 printf("STARTUP_MODEL_PASS assertions=%u failure_stages=10 stale_take_cases=12\n",checks);
 return 0;
}
