/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef unsigned long long u64;typedef u64 dma_addr_t;
#define __used __attribute__((unused))
#define __iomem
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define static_assert(x) _Static_assert(x,#x)
#define BIT(n) (1U<<(n))
#define U32_MAX UINT32_MAX
#define U64_MAX UINT64_MAX
#define READ_ONCE(x) (x)
#define GFP_KERNEL 0
#define VFE_LINE_PIX 0
#define E008D_REAR_AUX_COUNT 8
#define E008H_REAR_SLOTS 2
#define E008I_REAR_WMS 10
#define E007Y_STARTUP_PACKETS 4
#define NATIVE_REAR_NV12_BYTES 12441600U
#define NATIVE_REAR_NV12_Y_BYTES 8294400U
#define NATIVE_REAR_NV12_UV_BYTES 4147200U
#define NATIVE_REAR_NV12_UV_OFFSET NATIVE_REAR_NV12_Y_BYTES
#define VFE680_E004NT_REAR_TOTAL_BYTES NATIVE_REAR_NV12_BYTES
#define VFE680_E004NT_REAR_Y_FRAME_INCR NATIVE_REAR_NV12_Y_BYTES
#define VFE680_E004NT_REAR_C_FRAME_INCR NATIVE_REAR_NV12_UV_BYTES
#define VFE680_E004NT_REAR_C_META_OFFSET NATIVE_REAR_NV12_Y_BYTES
#define VFE680_E004NU_REAR_CLIENTS 10
#define VFE680_X1E_BUS_CFG 0
#define VFE680_X1E_BUS_IMAGE_ADDR 4
#define VFE_BUS_WRITE_CLIENT_CFG_EN 1
#define DMA_FROM_DEVICE 2
#define VB2_BUF_STATE_DONE 1
#define VB2_BUF_STATE_ERROR 2
static unsigned assertions,negative_cases,live_allocations,map_refs[4];
#define CHECK(x) do{assertions++;if(!(x)){fprintf(stderr,"FAIL:%d:%s\n",__LINE__,#x);abort();}}while(0)
struct model_vb2 {unsigned id;u64 timestamp;};
struct camss_buffer {struct {struct model_vb2 vb2_buf;u32 sequence;}vb;};
struct camss_video {struct camss_buffer *native_rear_inflight[2];u32 native_rear_completed,native_rear_live_completed;bool x1e_pix_stop_requested;};
struct vfe_output {int model;};
struct vfe_device {struct camss *camss;int output_lock;struct {struct camss_video video_out;struct vfe_output output;}line[1];u32 regs[32][2];};
struct csid_device {unsigned epoch,produced,consumed;bool overflow,errors;};
struct camss {struct vfe_device vfe[2];struct csid_device csid[2];void *dev;};
struct v4l2_subdev {int model;};
struct e008l_rear_command_set {bool retired;};
struct vfe680_e004nt_rear_surface {void *cpu;dma_addr_t dma;size_t size;bool in_flight;};
struct native_rear_video_dma {u32 y_iova,uv_iova;u64 mapped_bytes;};
struct vfe680_e004nu_rear_wm_static {u8 wm;u32 cfg,frame_incr;};
/* ACTUAL_LEDGER */
/* ACTUAL_TYPES */
struct native_rear_live_observation {int model;};
static struct camss camera;
static struct camss_buffer buffers[4],*pending[1024];
static unsigned pending_head,pending_tail,step_calls;
static int injected=-1;
static struct vfe680_e004nu_rear_wm_static contracts[10];
static unsigned delivered[4],last_sequence;
static int step(void){return (int)step_calls++==injected?-EIO:0;}
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *v){return v&&v->camss;}
static bool vfe680_x1e_dma_span_32bit(dma_addr_t dma,size_t bytes){return bytes&&dma<=U32_MAX&&bytes-1<=U32_MAX-dma;}
static const struct vfe680_e004nu_rear_wm_static *e008d_rear_contract_for_wm(u8 wm){int i=e007z_rear_index(wm);return i<0?NULL:&contracts[i];}
static struct e008d_rear_aux_buffer *e008d_rear_aux_for_wm(struct e008d_rear_dma_set *d,u8 wm){for(unsigned i=0;i<8;i++)if(d->aux[i].wm==wm)return &d->aux[i];return NULL;}
static void *vfe680_x1e_bus_reg(struct vfe_device *v,u8 wm,unsigned unused){(void)unused;return v->regs[wm];}
static u32 readl_relaxed(const void *p){return *(const u32*)p;}
static void writel_relaxed(u32 value,void *p){*(u32*)p=value;}
#define wmb() ((void)0)
/* ACTUAL_PRIME_HELPERS */
static bool native_rear_memory_overlap(const void *a,size_t an,const void *b,size_t bn){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return !a||!b||!an||!bn||an>UINTPTR_MAX-x||bn>UINTPTR_MAX-y||(x<y+bn&&y<x+an);}
static void *kzalloc(size_t n,int flags){(void)flags;void *p=calloc(1,n);CHECK(p);return p;}
static void kfree(void *p){free(p);}
static void dma_free_coherent(void *dev,size_t size,void *cpu,dma_addr_t dma){(void)dev;(void)size;(void)dma;CHECK(live_allocations);live_allocations--;free(cpu);}
/* ACTUAL_AUX_FREE */
static void e008d_rear_release_partial(struct vfe_device *v,struct e008d_rear_dma_set *d){
 if(d->public_full.acquired){unsigned id=(unsigned)(uintptr_t)d->public_full.dbuf-1;CHECK(id<4&&map_refs[id]);map_refs[id]--;}
 for(unsigned i=0;i<8;i++)e008d_rear_aux_release(v,&d->aux[i]);
 memset(d,0,sizeof(*d));
}
static int native_rear_public_dma_alloc(struct vfe_device *v,struct e008d_rear_dma_set *d,struct camss_buffer *buffer){
 CHECK(v&&d&&buffer);int ret=step();if(ret)return ret;unsigned id=buffer->vb.vb2_buf.id;CHECK(id<4&&map_refs[id]==0);map_refs[id]++;
 u32 base=0x20000000+id*0x04000000;
 d->allocated=true;d->full.dma=base;d->full.size=NATIVE_REAR_NV12_BYTES;
 d->public_full=(struct native_rear_video_lease){.dbuf=(void*)(uintptr_t)(id+1),.attachment=(void*)(uintptr_t)(id+101),.table=(void*)(uintptr_t)(id+201),.span={base,base+NATIVE_REAR_NV12_UV_OFFSET,NATIVE_REAR_NV12_BYTES+2048},.acquired=true};
 for(unsigned i=0;i<8;i++){u8 wm=e008d_rear_aux_wms[i];const struct vfe680_e004nu_rear_wm_static *c=e008d_rear_contract_for_wm(wm);d->aux[i]=(struct e008d_rear_aux_buffer){calloc(1,c->frame_incr),0x60000000+id*0x04000000+i*0x00400000,c->frame_incr,wm};CHECK(d->aux[i].cpu);live_allocations++;}
 return 0;
}
static int e008d_rear_build_addresses(struct vfe_device *v,struct e008d_rear_dma_set *d,struct e008d_rear_addresses *a){
 CHECK(v&&d&&a);int ret=step();if(ret)return ret;
 for(unsigned i=0;i<10;i++){u8 wm=e007z_rear_wm_descs[i].wm;a->wm[i]=wm;a->image[i]=i<2?d->full.dma+(i?NATIVE_REAR_NV12_UV_OFFSET:0):e008d_rear_aux_for_wm(d,wm)->dma;}
 return 0;
}
static int native_rear_video_lease_expose(struct native_rear_video_lease *l){int ret=step();if(!ret)l->exposed=true;return ret;}
static bool native_rear_live_commands_retired_valid(const struct e008l_rear_command_set *s,u64 owner){return s&&s->retired&&owner==7;}
static void dma_buf_unmap_attachment_unlocked(void *attachment,void *table,int direction){CHECK(attachment&&table&&direction==DMA_FROM_DEVICE);}
static void dma_buf_detach(void *dbuf,void *attachment){CHECK(dbuf&&attachment);}
static void dma_buf_put(void *dbuf){unsigned id=(unsigned)(uintptr_t)dbuf-1;CHECK(id<4&&map_refs[id]);map_refs[id]--;}
static int native_rear_live_replacement_read(struct vfe_device *v,struct csid_device *c,const struct e008h_rear_prime_pair *p,const struct e008k_rear_result *r,u32 cursor,struct native_rear_live_observation *o){
 CHECK(o);int ret=step();if(ret)return ret;
 if(!e008h_rear_both_complete(p,r->owner_epoch)||cursor!=c->produced||cursor!=c->consumed||r->csid_quiesced||r->bus_stopped)return -EPROTO;
 return e008h_rear_check_slot_addresses(v,p,1,true);
}
static void model_log(void *dev,const char *format,...){(void)dev;(void)format;}
#define dev_info model_log
/* ACTUAL_RETIRE */
struct e008i_rear_done_event {u64 owner_epoch;u32 raw_buf_done_status;u16 wm_mask;u32 addr_status0[10];};
static const u8 e008i_rear_wm[10]={0,1,2,3,11,12,13,14,16,18};
static struct e008i_rear_done_event event;
static u32 csid680_e008i_rear_done_overflow(struct csid_device *c){return c->overflow;}
static u32 csid680_e008i_rear_latch_errors(struct csid_device *c){return c->errors;}
static u32 csid680_e008i_rear_done_count(struct csid_device *c){return c->produced;}
static int csid680_e008i_rear_done_event(struct csid_device *c,u32 cursor,struct e008i_rear_done_event *out){CHECK(cursor==c->consumed&&cursor<c->produced);*out=event;return 0;}
static int csid680_e008i_rear_retire_event(struct csid_device *c,u32 cursor,u64 owner){CHECK(owner==7&&cursor==c->consumed);c->consumed++;return 0;}
static u32 csid680_e008i_rear_epoch0_seq(struct csid_device *c){return c->epoch;}
static int csid680_e008i_rear_poll_next_epoch0(struct csid_device *c,u32 epoch,unsigned long timeout){CHECK(timeout&&epoch==c->epoch);int ret=step();if(!ret)c->epoch++;return ret;}
static int e008k_rear_collect_done(struct csid_device *c,struct e008h_rear_prime_pair *p,u64 owner,unsigned long timeout,u32 *cursor);
#define spin_lock_irqsave(lock,flags) do{(void)(lock);flags=0;}while(0)
#define spin_unlock_irqrestore(lock,flags) do{(void)(lock);(void)(flags);}while(0)
static struct camss_buffer *vfe_buf_get_pending(struct vfe_output *o){(void)o;return pending_head<pending_tail?pending[pending_head++]:NULL;}
static void usleep_range(unsigned low,unsigned high){CHECK(low<high);}
static void vb2_set_plane_payload(struct model_vb2 *b,unsigned plane,unsigned bytes){CHECK(b&&plane==0&&bytes==NATIVE_REAR_NV12_BYTES);}
static u64 ktime_get_ns(void){return (u64)assertions+1;}
static void vb2_buffer_done(struct model_vb2 *b,int state){
 unsigned id=b->id;struct camss_video *v=&camera.vfe[1].line[0].video_out;CHECK(id<4);
 if(state==VB2_BUF_STATE_ERROR)return;
 CHECK(!map_refs[id]);CHECK(v->native_rear_inflight[0]!=&buffers[id]&&v->native_rear_inflight[1]!=&buffers[id]);
 CHECK(buffers[id].vb.sequence==last_sequence++);delivered[id]++;
 if(v->native_rear_completed>=80)v->x1e_pix_stop_requested=true;
 else{CHECK(pending_tail<ARRAY_SIZE(pending));pending[pending_tail++]=&buffers[id];}
}
/* ACTUAL_QUEUE */
static int e008k_rear_collect_done(struct csid_device *c,struct e008h_rear_prime_pair *p,u64 owner,unsigned long timeout,u32 *cursor){
 CHECK(timeout&&owner==7);int ret=step();if(ret)return ret;
 event=(struct e008i_rear_done_event){.owner_epoch=owner,.raw_buf_done_status=0x3ff,.wm_mask=1023};
 for(unsigned i=0;i<10;i++)event.addr_status0[i]=p->frame[1].slot[i].programmed_image_iova;
 c->produced++;ret=native_rear_queue_drain(c,p,owner,cursor);CHECK(!ret);CHECK(e008h_rear_both_complete(p,owner));return 0;
}
static void fixture(struct e008h_rear_prime_pair *p,struct e008k_rear_request *q,struct e008k_rear_result *r,struct e008l_rear_command_set *commands){
 memset(&camera,0,sizeof(camera));camera.vfe[1].camss=&camera;pending_head=pending_tail=last_sequence=step_calls=0;injected=-1;memset(delivered,0,sizeof(delivered));memset(p,0,sizeof(*p));memset(q,0,sizeof(*q));memset(r,0,sizeof(*r));
 for(unsigned i=0;i<10;i++)contracts[i]=(struct vfe680_e004nu_rear_wm_static){e007z_rear_wm_descs[i].wm,0x21+i*0x20,e007z_rear_wm_descs[i].required_bytes};
 for(unsigned i=0;i<4;i++)buffers[i].vb.vb2_buf.id=i;
 struct vfe_device *v=&camera.vfe[1];struct csid_device *c=&camera.csid[1];
 for(unsigned s=0;s<2;s++){
  CHECK(!native_rear_public_dma_alloc(v,&p->dma[s],&buffers[s]));CHECK(!e008d_rear_build_addresses(v,&p->dma[s],&p->addr[s]));
  struct e007z_rear_binding binding[10];CHECK(!e008h_rear_build_binding(p,s,binding));CHECK(!e007z_rear_bind(&p->frame[s],7,s+1,binding));p->frame[s].pending=0;p->programmed[s]=true;p->dma[s].full.in_flight=true;p->dma[s].public_full.exposed=true;
 }
 p->dma[0].prepared_disabled=true;p->allocated=p->enabled=p->ledgers_bound=p->slot0_preloaded_disabled=true;
 for(unsigned i=0;i<10;i++)v->regs[contracts[i].wm][0]=contracts[i].cfg;
 CHECK(!e008h_rear_write_slot_addresses(v,p,1));c->epoch=3;
 r->owner_epoch=7;r->both_frames_complete=r->live_commands_retired=true;commands->retired=true;q->commands=commands;q->public_video[0]=&buffers[0];q->public_video[1]=&buffers[1];q->epoch_timeout_us=500000;q->done_timeout_us=1000000;
 CHECK(!native_rear_live_retire_full(v,c,p,r,0));CHECK(!native_rear_live_retire_aux(v,c,p,r,0));
 v->line[0].video_out.native_rear_inflight[0]=&buffers[0];v->line[0].video_out.native_rear_inflight[1]=&buffers[1];
 pending[pending_tail++]=&buffers[2];pending[pending_tail++]=&buffers[3];step_calls=0;
}
static void cleanup(struct e008h_rear_prime_pair *p){
 for(unsigned s=0;s<2;s++)e008d_rear_release_partial(&camera.vfe[1],&p->dma[s]);
 CHECK(!live_allocations);for(unsigned i=0;i<4;i++)CHECK(!map_refs[i]);
}
int main(void){
 struct e008h_rear_prime_pair p;struct e008k_rear_request q;struct e008k_rear_result r;struct e008l_rear_command_set commands;u32 cursor;
 fixture(&p,&q,&r,&commands);cursor=0;
 CHECK(native_rear_queue_run(&camera.vfe[1],&camera.csid[1],&p,&q,&r,&cursor)==0);
 CHECK(camera.vfe[1].line[0].video_out.native_rear_live_completed==80&&r.queue_handoffs==79);
 CHECK(p.frame[0].request_generation==80&&p.frame[1].request_generation==81);
 CHECK(native_rear_live_aux_retired_valid(&p.dma[0],&p.frame[0],7));CHECK(p.dma[1].full.in_flight&&map_refs[0]+map_refs[1]+map_refs[2]+map_refs[3]==1);
 for(unsigned i=0;i<4;i++)CHECK(delivered[i]==20);
 cleanup(&p);
 for(int fault=0;fault<90;fault++){
  fixture(&p,&q,&r,&commands);injected=fault;cursor=0;
  CHECK(native_rear_queue_run(&camera.vfe[1],&camera.csid[1],&p,&q,&r,&cursor)<0);
  CHECK(camera.vfe[1].line[0].video_out.native_rear_completed<80);
  cleanup(&p);negative_cases++;
 }
 fixture(&p,&q,&r,&commands);
 struct e008h_rear_prime_pair next;
 CHECK(!native_rear_queue_prepare(&camera.vfe[1],&p,&next,&buffers[2],7));
 for(unsigned s=0;s<2;s++)for(unsigned i=0;i<8;i++)for(unsigned o=0;o<=s;o++)for(unsigned j=0;j<8;j++){
  if(o==s&&j>=i)break;
  void *saved=next.dma[s].aux[i].cpu;next.dma[s].aux[i].cpu=next.dma[o].aux[j].cpu;
  CHECK(native_rear_queue_allocations_check(&next)==-EADDRINUSE);next.dma[s].aux[i].cpu=saved;negative_cases++;
 }
 next.dma[1].public_full.span.mapped_bytes+=1ULL<<32;CHECK(native_rear_queue_allocations_check(&next)==-EPROTO);negative_cases++;
 next.dma[1].public_full.span.mapped_bytes-=1ULL<<32;e008d_rear_release_partial(&camera.vfe[1],&next.dma[1]);cleanup(&p);
 printf("REAR_QUEUE_PASS assertions=%u live_frames=80 negative_cases=%u\n",assertions,negative_cases);return 0;
}
