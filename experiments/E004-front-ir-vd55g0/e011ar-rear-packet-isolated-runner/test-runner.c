/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual E011AR orchestration under host-only fault-injected providers.
 * These providers simulate lifecycle contracts; they do not prove hardware. */
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint64_t u64;
#define __used __attribute__((used))
#define GFP_KERNEL 0
#define BIT(x) (1U << (x))
#define U64_MAX UINT64_MAX
#define E007Y_STARTUP_PACKETS 4
#define E007Y_MAX_BL 2
#define E008I_REAR_WMS 10
#define E008H_REAR_SLOTS 2
#define E005Y_VFE1_OWNER_REAR 2
#define VFE_LINE_PIX 0
#define E006Z_EPOCH_STARTUP 1
#define E007C_PERIOD_VALID_MASK 7
#define CAMSS_E008K_REAR_BRIDGE_H
typedef int atomic_t;
#define ATOMIC_INIT(x) (x)
static int atomic_cmpxchg(int *p,int a,int b) {int old=*p;if(old==a)*p=b;return old;}
static unsigned assertions;
#define CHECK(x) do { assertions++; assert(x); } while (0)
static int seq, fail_at, failed, materializations, released_commands, unsafe_release;
static int pm_refs, stopped, stopped_at, release_at, malformed_at, mark_fail;
static int allocation_count, allocation_fail;
static unsigned attempted, halted;
static void *allocations[64]; static unsigned alloc_n;
static bool faultable[256];
static void notify(void) { seq++; }
static int step(void) { seq++; faultable[seq]=true; if(seq==fail_at) { failed=1; return -EIO; } return 0; }
static void *zalloc(size_t n) {
 allocation_count++; if(allocation_count==allocation_fail)return NULL;
 void *p=calloc(1,n); CHECK(p); allocations[alloc_n++]=p; CHECK(alloc_n<64); return p;
}
#define kzalloc(n,g) zalloc(n)
static void kfree(void *p) {if(!p)return;for(unsigned i=0;i<alloc_n;i++)if(allocations[i]==p){allocations[i]=NULL;free(p);return;}CHECK(0);}
struct v4l2_subdev {int id;}; struct media_entity {int id;};
struct csid_device {int dummy;}; struct csiphy_device {struct v4l2_subdev subdev;};
struct camss;
struct vfe_device {struct camss *camss;struct {struct {struct {struct media_entity entity;}vdev;}video_out;}line[1];};
struct camss {struct vfe_device vfe[2];struct csid_device csid[2];struct csiphy_device csiphy[2];int e005y_vfe1_owner;};
struct e007d_rear_register_state {
 struct {int epoch_kind;u8 startup_phase;u64 request_id;}scalar;
 struct {u32 valid_mask;}period; u32 fingerprint;
};
struct e007v_rear_dmi_state {u64 request_id;u32 fingerprint;};
struct e007y_rear_startup_output {u32 bl_count;struct {u32 dma;u16 bytes;}bl[2];u64 tag;u8 phase;};
struct e008l_rear_command_set {
 struct {bool allocated,submitted;struct e007y_rear_startup_output out;}packet[4];
 bool allocated,hardware_exposed;
};
static int e007v_rear_validate_request(struct e007v_rear_dmi_state *d,u64 id) {return d->request_id==id?0:-ESTALE;}
static struct e007y_rear_startup_output *e008l_rear_command_output(struct e008l_rear_command_set *c,u8 p) {
 if(!c||!c->allocated||p>=4||!c->packet[p].allocated)return NULL;
 return &c->packet[p].out;
}
static int e007y_rear_materialize(struct e007d_rear_register_state *r,struct e007v_rear_dmi_state *d,u64 id,u8 p,struct e007y_rear_startup_output *out) {
 int ret=step(); if(ret)return ret; materializations++;
 CHECK(r->scalar.request_id==id);CHECK(r->scalar.startup_phase==p);
 CHECK(r->fingerprint==100U+p);CHECK(d->fingerprint==200U+p);
 out->tag=id;out->phase=p;out->bl_count=1;out->bl[0].dma=1000U+p;out->bl[0].bytes=16;
 if(malformed_at==p+1)out->bl_count=0;
 return 0;
}
#include "../e008o-rear-packet-semantic-state-contract/camss-vfe-e008o-rear-semantic-state.inc"
struct e008h_rear_prime_pair {struct {u64 request_generation;}frame[2];bool enabled,slot0_preloaded_disabled;int observations;};
struct e008i_rear_done_event {u64 owner_epoch;u32 raw_buf_done_status;u16 wm_mask;u32 addr_status0[10];};
static const u8 e008i_rear_wm[10]={0,1,2,3,11,12,13,14,16,18};
static int e008k_rear_validate_route(struct camss *c,struct v4l2_subdev *s) {CHECK(c);CHECK(s);return step();}
static int e008l_rear_command_alloc(struct vfe_device *v,struct e008l_rear_command_set *c) {
 CHECK(v);int ret=step();if(ret)return ret;c->allocated=true;for(int i=0;i<4;i++)c->packet[i].allocated=true;return 0;
}
static int e008l_rear_command_mark_submitted(struct e008l_rear_command_set *c,u8 p) {
 if(mark_fail==p+1)return -EINVAL;
 if(!c->allocated||!c->packet[p].allocated||c->packet[p].submitted||!c->packet[p].out.bl_count)return -EINVAL;
 c->packet[p].submitted=true;c->hardware_exposed=true;return 0;
}
static int e008l_rear_command_release(struct vfe_device *v,struct e008l_rear_command_set *c,bool proof) {
 CHECK(v);CHECK(c->allocated);CHECK(!c->hardware_exposed||proof);
 if(proof){CHECK(stopped);CHECK(stopped_at>0);CHECK(stopped_at<seq+1);}
 int ret=step();if(ret)return ret;released_commands++;release_at=seq;c->allocated=false;return 0;
}
static int e005y_vfe1_owner_acquire(int *o,int owner,bool exact,u64 *epoch) {CHECK(owner==2&&exact);int ret=step();if(ret)return ret;*o=2;*epoch=41;return 0;}
static int e005y_vfe1_owner_release(int *o,int owner,u64 epoch,bool safe) {CHECK(owner==2&&epoch==41);if(!safe)unsafe_release++;int ret=step();if(ret)return ret;*o=safe?0:3;return 0;}
static int e008j_rear_alloc_pair_no_mmio(struct vfe_device *v,struct e008h_rear_prime_pair *p) {CHECK(v&&p);return step();}
static int e008j_rear_bind_pair_no_mmio(struct e008h_rear_prime_pair *p,u64 epoch,u64 gen) {CHECK(epoch==41&&gen);int ret=step();if(ret)return ret;p->frame[0].request_generation=gen;p->frame[1].request_generation=gen+1;return 0;}
static int e008k_rear_pipeline_pm_get(struct media_entity *e) {CHECK(e);int ret=step();if(!ret)pm_refs++;return ret;}
static void e008k_rear_pipeline_pm_put(struct media_entity *e) {CHECK(e);CHECK(pm_refs>0);pm_refs--; notify();}
static int csid680_e008i_rear_reset(struct csid_device *c,u64 epoch) {CHECK(c&&epoch==41);return step();}
static int e008k_rear_rtcdm_open_start(struct camss *c) {CHECK(c);attempted|=1;stopped=0;return step();}
static int e008k_rear_rtcdm_submit_bl(struct camss *c,u32 dma,u16 bytes) {CHECK(c&&dma>=1000&&dma<=1003&&bytes==16);return step();}
static void e008k_rear_rtcdm_stop_close(struct camss *c) {CHECK(c);halted|=1;stopped=1;stopped_at=seq+1;notify();}
static bool e008k_rear_rtcdm_stopped(struct camss *c) {CHECK(c);return !step()&&stopped;}
static int e008j_rear_prepare_slot0_after_packet0(struct vfe_device *v,struct e008h_rear_prime_pair *p) {CHECK(v);attempted|=2;p->slot0_preloaded_disabled=true;return step();}
static int e008h_rear_enable_slot0(struct vfe_device *v,struct e008h_rear_prime_pair *p) {CHECK(v);p->enabled=true;return step();}
static int csid680_e008k_rear_enable(struct csid_device *c) {CHECK(c);attempted|=4;return step();}
static int e008k_rear_subdev_stream(struct v4l2_subdev *s,bool on) {CHECK(s);unsigned bit=s->id==9?16:8;if(on)attempted|=bit;else halted|=bit;return step();}
static int csid680_e008i_rear_poll_next_epoch0(struct csid_device *c,u32 after,unsigned long us) {CHECK(c&&after<2&&us);return step();}
static int e008h_rear_epoch0_retarget_slot1(struct vfe_device *v,struct e008h_rear_prime_pair *p) {CHECK(v&&p);return step();}
static bool e008h_rear_both_complete(struct e008h_rear_prime_pair *p,u64 epoch) {CHECK(epoch==41);return p->observations==20;}
static u32 csid680_e008i_rear_done_count(struct csid_device *c) {CHECK(c);return 2;}
static int csid680_e008i_rear_done_event(struct csid_device *c,u32 i,struct e008i_rear_done_event *e) {
 CHECK(c&&i<2);int ret=step();if(ret)return ret;memset(e,0,sizeof(*e));e->owner_epoch=41;e->wm_mask=0x3ff;e->raw_buf_done_status=0x2f1;return 0;
}
static int e008h_rear_observe_consumed(struct e008h_rear_prime_pair *p,u64 epoch,u32 status,u8 wm,u32 addr) {
 CHECK(epoch==41&&status==0x2f1);(void)wm;(void)addr;int ret=step();if(ret)return ret;p->observations++;return 0;
}
static int csid680_e008i_rear_poll_done(struct csid_device *c,u32 n,unsigned long us) {CHECK(c&&n&&us);return -ETIMEDOUT;}
static int csid680_e008a_rear_quiesce(struct csid_device *c,bool owner) {CHECK(c&&owner);halted|=4;return step();}
static int vfe680_e008a_rear_bus_stop(struct vfe_device *v,bool owner) {CHECK(v&&owner);halted|=2;return step();}
static bool e007z_rear_retireable(void *f,u64 epoch,u64 gen,bool csid,bool bus) {CHECK(f&&epoch==41&&gen&&csid&&bus);return !step();}
static int e007z_rear_release_ledger(void *f,u64 epoch,u64 gen,bool csid,bool bus) {CHECK(f&&epoch==41&&gen&&csid&&bus);return step();}
static void e008h_rear_fault_ledgers(struct e008h_rear_prime_pair *p,u64 epoch) {CHECK(p&&epoch==41);}
static void e008h_rear_release_before_mmio(struct vfe_device *v,struct e008h_rear_prime_pair *p) {CHECK(v&&p);CHECK(!p->enabled);}
#include "camss-vfe-e011ar-rear-runner.inc"
#include "camss-vfe-e011ar-rear-single-use.inc"
static void reset(void) {
 for(unsigned i=0;i<alloc_n;i++)free(allocations[i]);
 memset(allocations,0,sizeof(allocations));alloc_n=0;
 seq=fail_at=failed=materializations=released_commands=unsafe_release=pm_refs=stopped=stopped_at=release_at=malformed_at=mark_fail=allocation_count=allocation_fail=0;
 e011ar_rear_consumed=0;attempted=halted=0;memset(faultable,0,sizeof(faultable));
}
static void init(struct camss *c,struct e008o_rear_semantic_set *set) {
 memset(c,0,sizeof(*c));for(int i=0;i<2;i++)c->vfe[i].camss=c;
 memset(set,0,sizeof(*set));set->sealed=true;
 for(int i=0;i<4;i++){set->packet[i].ready=true;set->packet[i].request_id=10U+i;
 set->packet[i].regs.scalar.epoch_kind=1;set->packet[i].regs.scalar.startup_phase=i;
 set->packet[i].regs.scalar.request_id=10U+i;set->packet[i].regs.period.valid_mask=7;
 set->packet[i].regs.fingerprint=100U+i;set->packet[i].dmi.request_id=10U+i;set->packet[i].dmi.fingerprint=200U+i;}
}
static int run_case(int fail,int invalid,int allocfail,int markfail) {
 reset();struct camss c;struct e008o_rear_semantic_set set;init(&c,&set);
 struct v4l2_subdev sensor={.id=9};
 struct e011ar_rear_once_request req={.sensor=&sensor,.semantics=&set,.first_request_generation=1};
 struct e011ar_rear_once_result res;
 fail_at=fail;allocation_fail=allocfail;mark_fail=markfail;
 if(invalid==1)set.sealed=false;
 if(invalid>=2&&invalid<=5)set.packet[invalid-2].ready=false;
 if(invalid>=6&&invalid<=9)set.packet[invalid-6].regs.scalar.startup_phase=4;
 if(invalid>=10&&invalid<=13)set.packet[invalid-10].dmi.request_id=99;
 if(invalid==14)req.first_request_generation=U64_MAX;
 if(invalid==15)req.sensor=NULL;
 int ret=e011ar_rear_run_once_unreachable(&c.vfe[1],&req,&res);
 CHECK(res.identity_consumed);
 if(!ret){CHECK(materializations==4);CHECK(released_commands==1);CHECK(res.reboot_required);
 CHECK(res.transaction.both_frames_complete&&res.transaction.owner_released&&res.transaction.dma_intentionally_pinned);
 CHECK(pm_refs==0);CHECK(release_at>stopped_at);}
 else if(res.reboot_required){CHECK(released_commands==0);CHECK(res.command_arena_allocated);
 CHECK((halted&attempted)==attempted);if(attempted&&!res.transaction.owner_released)CHECK(unsafe_release>0);}
 else {CHECK(!unsafe_release);CHECK(pm_refs==0);CHECK(!materializations||materializations<=4);}
 if(invalid){CHECK(ret);CHECK(materializations==0);CHECK(allocation_count==0);}
 if(fail)CHECK(failed);
 int before=seq;
 CHECK(e011ar_rear_run_once_unreachable(&c.vfe[1],&req,&res)==-EALREADY);
 CHECK(seq==before);
 return ret;
}
int main(void) {
 CHECK(e011ar_rear_runtime_authorization()==-EOPNOTSUPP);
 CHECK(e011ar_rear_once_runtime_authorization()==-EOPNOTSUPP);
 CHECK(run_case(0,0,0,0)==0);int stages=seq, injected=0;bool points[256];memcpy(points,faultable,sizeof(points));
 for(int i=1;i<=stages;i++) if(points[i]) {CHECK(run_case(i,0,0,0)!=0);injected++;}
 for(int i=1;i<=15;i++)CHECK(run_case(0,i,0,0)!=0);
 for(int i=1;i<=2;i++)CHECK(run_case(0,0,i,0)==-ENOMEM);
 for(int i=1;i<=4;i++)CHECK(run_case(0,0,0,i)!=0);
 reset();
 printf("{\"assertions\":%u,\"lifecycle_steps\":%d,\"injected_lifecycle_failures\":%d,\"semantic_negatives\":15,\"allocation_negatives\":2,\"exposure_negatives\":4,\"hardware_proof\":false}\n",assertions,stages,injected);
 return 0;
}
