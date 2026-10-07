/* SPDX-License-Identifier: GPL-2.0-only
 * Hosted tests for the actual allocator, wrapper, semantic handoff and validator.
 * Semantic providers and hardware callbacks are explicit mocks; no device access.
 */
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <limits.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef u64 dma_addr_t;
typedef int atomic_t;
#define __used __attribute__((used))
#define GFP_KERNEL 0
#define U64_MAX UINT64_MAX
#define ATOMIC_INIT(x) (x)
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#undef static_assert
#define static_assert(x) _Static_assert(x, #x)
#define ALIGN(x,a) (((x)+(a)-1)&~((size_t)(a)-1))
#define IS_ALIGNED(x,a) (((x)&((a)-1))==0)

struct camss { void *dev; };
struct vfe_device { struct camss *camss; };
struct v4l2_subdev { int dummy; };
struct e006g_rear_dynamic_payloads { u8 dummy[32]; };
static unsigned allocations, materializations, hardware_calls, tests;
static int fail_packet=-1;
static u64 next_dma=0x100000;
#define CHECK(x) do { tests++; if(!(x)){fprintf(stderr,"FAIL:%d %s\n",__LINE__,#x);abort();} } while(0)
static void *kzalloc(size_t n,int flags){void *p;(void)flags;p=calloc(1,n);if(p)allocations++;return p;}
static void *kcalloc(size_t n,size_t size,int flags){return kzalloc(n*size,flags);}
static void kfree(void *p){if(p){CHECK(allocations>0);allocations--;free(p);}}
static void memzero_explicit(void *p,size_t n){memset(p,0,n);}
static void *dma_alloc_coherent(void *dev,size_t n,dma_addr_t *dma,int flags){
 void *p=kzalloc(n,flags);(void)dev;*dma=next_dma;next_dma+=0x10000;return p;
}
static void dma_free_coherent(void *dev,size_t n,void *p,dma_addr_t dma){
 (void)dev;(void)n;(void)dma;kfree(p);
}
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *vfe){return vfe && vfe->camss;}
static bool vfe680_x1e_dma_span_32bit(dma_addr_t dma,size_t bytes){
 return bytes && dma<=UINT32_MAX && bytes-1<=UINT32_MAX-dma;
}
static u32 get_unaligned_le32(const void *p){const u8 *b=p;return (u32)b[0]|((u32)b[1]<<8)|((u32)b[2]<<16)|((u32)b[3]<<24);}
static void put_unaligned_le32(u32 v,void *p){u8 *b=p;b[0]=v;b[1]=v>>8;b[2]=v>>16;b[3]=v>>24;}
static int atomic_cmpxchg(atomic_t *p,int before,int after){int old=*p;if(old==before)*p=after;return old;}

/* Extracted unchanged from the staged, source-pinned E007Y source. */
#include "e007y-layout.h"

#include "camss-e006z-clean-scalar-bank.inc"
#define E007C_PERIOD_VALID_MASK 1
struct e007d_rear_register_state {
 struct e006z_rear_scalar_state scalar;
 struct { u8 gamma_lut_enable; } bfstats;
 struct { unsigned valid_mask; } period;
};
struct e007e_bf_dmi_state { bool gamma_valid, gamma_inactive; u16 gamma[32]; };
struct prepared_f { struct e007e_bf_dmi_state bfstats25; };
struct prepared_i { struct prepared_f dmi; };
struct prepared_q { struct prepared_i dmi; };
struct prepared_s { struct prepared_q dmi; };
struct prepared_t { struct prepared_s dmi; };
struct prepared_u { struct prepared_t dmi; };
struct e007v_rear_dmi_state { u64 request_id; struct prepared_u dmi; };
static int e007v_rear_validate_request(struct e007v_rear_dmi_state *d,u64 id){
 return d->request_id==id?0:-ESTALE;
}
static int e007y_rear_materialize(struct e007d_rear_register_state *r,
 struct e007v_rear_dmi_state *d,u64 id,u8 packet,struct e007y_rear_startup_output *out){
 materializations++;
 CHECK(r->scalar.startup_phase==packet);
 CHECK(r->scalar.request_id==id && d->request_id==id);
 /* Distinct mock semantic outputs; not Windows payload or ISP accuracy proof. */
 memset(out->main,(int)packet+1,out->main_bytes);
 put_unaligned_le32((u32)id,out->main);
 CHECK(e007y_rear_wrapper(packet,out)==0);
 if(fail_packet==(int)packet)return -EIO;
 return 0;
}

#include "camss-vfe-e008l-rear-command-dma.inc"
#include "native-rear-prepared-commands.inc"
#include "e008k-prepared-validator.h"

static int e008k_rear_validate_route(struct camss *c,struct v4l2_subdev *s){return c&&s?0:-EINVAL;}
static int e008k_rear_run_unreachable(struct vfe_device *v,struct e008k_rear_request *q,
 struct e008k_rear_result *r){(void)v;(void)q;(void)r;hardware_calls++;return -EIO;}
#include "camss-vfe-e008n-rear-single-use.inc"
#include "camss-vfe-e008o-rear-semantic-state.inc"
#include "native-rear-scalar-binding.inc"

static void init_semantics(struct e008o_rear_semantic_set *s){
 static const u64 ids[4]={4,5,6,6};unsigned p;
 memset(s,0,sizeof(*s));s->sealed=true;
 for(p=0;p<4;p++){
  s->packet[p].request_id=ids[p];s->packet[p].ready=true;
  s->packet[p].regs.scalar.epoch_kind=E006Z_EPOCH_STARTUP;
  s->packet[p].regs.scalar.startup_phase=p;s->packet[p].regs.scalar.request_id=ids[p];
  s->packet[p].regs.period.valid_mask=E007C_PERIOD_VALID_MASK;
  s->packet[p].dmi.request_id=ids[p];
  s->packet[p].regs.bfstats.gamma_lut_enable=!!p;
  s->packet[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25.gamma_valid=!!p;
  s->packet[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25.gamma_inactive=!p;
 }
}
static bool all_zero(const void *ptr,size_t n){
 const u8 *b=ptr;size_t i;for(i=0;i<n;i++)if(b[i])return false;return true;
}
static void positive_and_corruption_tests(struct vfe_device *v,struct v4l2_subdev *sensor){
 struct e008o_rear_semantic_set semantic;
 struct e008l_rear_command_set arena={0};
 struct e008k_rear_request req={0};
 u8 *snapshot[4];unsigned p,j;
 init_semantics(&semantic);
 CHECK(e008l_rear_command_alloc(v,&arena)==0);
 CHECK(e008o_rear_materialize_commands(&semantic,&arena)==0);
 CHECK(materializations==4);
 req.sensor=sensor;req.commands=&arena;req.first_request_generation=1;
 for(p=0;p<4;p++){
  req.packet_request_id[p]=semantic.packet[p].request_id;
  CHECK(arena.packet_request_id[p]==semantic.packet[p].request_id);
  CHECK(get_unaligned_le32(arena.packet[p].out.main)==semantic.packet[p].request_id);
  CHECK(arena.packet[p].out.main[4]==p+1);
  snapshot[p]=malloc(arena.packet[p].slab_bytes);CHECK(snapshot[p]!=NULL);
  memcpy(snapshot[p],arena.packet[p].slab_cpu,arena.packet[p].slab_bytes);
 }
 /* Once prepared, later producer-state edits must have no effect on commands. */
 for(p=0;p<4;p++){
  semantic.packet[p].request_id+=100;
  semantic.packet[p].regs.scalar.request_id+=100;
  semantic.packet[p].regs.scalar.startup_phase^=1;
  semantic.packet[p].ready=false;
 }
 /* Revalidation must never invoke the semantic writer or change commands. */
 req.first_request_generation=U64_MAX;
 CHECK(e008k_rear_validate_prepared_packets(&req)==-EINVAL);
 req.first_request_generation=1;
 for(j=0;j<20;j++)CHECK(e008k_rear_validate_prepared_packets(&req)==0);
 CHECK(materializations==4);
 for(p=0;p<4;p++){
  struct e007y_rear_startup_output *out=&arena.packet[p].out;
  u8 count=out->bl_count;u64 id=arena.packet_request_id[p];
  u32 dma=out->bl[1].dma;u16 bytes=out->bl[1].bytes;
  CHECK(memcmp(snapshot[p],arena.packet[p].slab_cpu,arena.packet[p].slab_bytes)==0);
  out->bl_count=0;CHECK(native_rear_validate_prepared_commands(&arena)<0);out->bl_count=count;
  arena.packet_request_id[p]=0;CHECK(native_rear_validate_prepared_commands(&arena)==-ESTALE);arena.packet_request_id[p]=id;
  req.packet_request_id[p]++;CHECK(e008k_rear_validate_prepared_packets(&req)==-ESTALE);req.packet_request_id[p]--;
  out->bl[1].dma+=4;CHECK(native_rear_validate_prepared_commands(&arena)<0);out->bl[1].dma=dma;
  out->bl[1].bytes--;CHECK(native_rear_validate_prepared_commands(&arena)<0);out->bl[1].bytes=bytes;
  out->dmi[0].dma+=4;CHECK(native_rear_validate_prepared_commands(&arena)<0);out->dmi[0].dma-=4;
  out->dmi[0].cpu++;CHECK(native_rear_validate_prepared_commands(&arena)<0);out->dmi[0].cpu--;
  out->wrapper_dma+=4;CHECK(native_rear_validate_prepared_commands(&arena)<0);out->wrapper_dma-=4;
  if(p){
   put_unaligned_le32(99,out->wrapper+E007Y_WRAPPER_IRQ_OFF+0x10);
   CHECK(native_rear_validate_prepared_commands(&arena)<0);
   put_unaligned_le32(p,out->wrapper+E007Y_WRAPPER_IRQ_OFF+0x10);
  }
 }
 {
  struct e008l_rear_packet_dma saved=arena.packet[1];
  /* Fully consistent descriptors can still alias another DMA arena. */
  arena.packet[1].slab_dma=arena.packet[0].slab_dma;
  CHECK(e008l_rear_packet_bind_layout(&arena.packet[1],1)==0);
  CHECK(e007y_rear_wrapper(1,&arena.packet[1].out)==0);
  CHECK(native_rear_validate_prepared_commands(&arena)==-EADDRINUSE);
  arena.packet[1]=saved;
  CHECK(e008l_rear_packet_bind_layout(&arena.packet[1],1)==0);
  CHECK(e007y_rear_wrapper(1,&arena.packet[1].out)==0);
 }
 CHECK(native_rear_validate_prepared_commands(&arena)==0);
 CHECK(e008o_rear_materialize_commands(&semantic,&arena)==-EINVAL);
 CHECK(materializations==4);
 CHECK(e008l_rear_command_mark_submitted(&arena,0)==0);
 CHECK(native_rear_validate_prepared_commands(&arena)==-ESTALE); /* partial submission */
 CHECK(e008l_rear_command_release(v,&arena,false)==-EBUSY);
 for(p=1;p<4;p++)CHECK(e008l_rear_command_mark_submitted(&arena,p)==0);
 CHECK(native_rear_validate_prepared_commands(&arena)==0);
 CHECK(e008l_rear_command_release(v,&arena,true)==0);
 for(p=0;p<4;p++)free(snapshot[p]);
 CHECK(allocations==0);
}
static void failure_atomicity_tests(struct vfe_device *v){
 unsigned p,j;
 for(p=0;p<4;p++){
  struct e008o_rear_semantic_set semantic;
  struct e008l_rear_command_set arena={0};
  init_semantics(&semantic);fail_packet=(int)p;
  CHECK(e008l_rear_command_alloc(v,&arena)==0);
  CHECK(e008o_rear_materialize_commands(&semantic,&arena)==-EIO);
  CHECK(!arena.prepared && !arena.hardware_exposed);
  for(j=0;j<4;j++){
   CHECK(arena.packet_request_id[j]==0 && arena.packet[j].out.bl_count==0);
   CHECK(all_zero(arena.packet[j].slab_cpu,arena.packet[j].slab_bytes));
  }
  CHECK(e008l_rear_command_release(v,&arena,false)==0);
  CHECK(allocations==0);
 }
 fail_packet=-1;
}
static void semantic_rejection_tests(struct vfe_device *v){
 unsigned p;
 for(p=0;p<4;p++){
  struct e008o_rear_semantic_set s;
  struct e008l_rear_command_set a={0};
  unsigned before=materializations;
  init_semantics(&s);s.packet[p].regs.scalar.startup_phase^=1;
  CHECK(e008l_rear_command_alloc(v,&a)==0);
  CHECK(e008o_rear_materialize_commands(&s,&a)==-EPROTO);
  CHECK(materializations==before && !a.prepared);
  CHECK(e008l_rear_command_release(v,&a,false)==0);
 }
 CHECK(allocations==0);
}
static void once_and_denial_test(struct vfe_device *v,struct v4l2_subdev *sensor){
 struct e008o_rear_semantic_set semantic;
 struct e008n_rear_request req={0};
 struct e008n_rear_result result;
 unsigned before=materializations;
 init_semantics(&semantic);req.sensor=sensor;req.semantics=&semantic;
 req.first_request_generation=1;
 CHECK(e008n_rear_run_once_unreachable(v,&req,&result)==-EOPNOTSUPP);
 CHECK(result.identity_consumed && result.command_arena_allocated && result.preflight_materialized);
 CHECK(result.command_arena_released && !result.reboot_required && allocations==0 && hardware_calls==0);
 CHECK(materializations==before+4);
 CHECK(e008n_rear_run_once_unreachable(v,&req,&result)==-EALREADY);
 CHECK(materializations==before+4 && hardware_calls==0 && allocations==0);
}

static void scalar_binding_test(void)
{
 struct native_rear_startup_scalars capsule={0}, bad;
 struct e008o_rear_semantic_set semantic, saved;
 unsigned p,j;
 static const u64 ids[4]={4,5,6,6};
 #define PUTCAP(off,value,width) do { u64 _v=(value);unsigned _i;for(_i=0;_i<(width);_i++)capsule.data[(off)+_i]=(u8)(_v>>(8*_i)); } while(0)
 PUTCAP(0,NATIVE_REAR_SCALARS_MAGIC,4);PUTCAP(4,NATIVE_REAR_SCALARS_VERSION,2);
 PUTCAP(6,NATIVE_REAR_SCALARS_BYTES,2);PUTCAP(8,4,4);
 init_semantics(&semantic);
 for(p=0;p<4;p++){
  unsigned off=16+48*p;
  semantic.packet[p].ready=false;
  PUTCAP(off,ids[p],8);PUTCAP(off+8,p,4);
  for(j=0;j<4;j++){PUTCAP(off+16+2*j,1024+p*16+j,2);PUTCAP(off+24+4*j,4096+p*32+j,4);}
  PUTCAP(off+40,1024+p,2);PUTCAP(off+42,1536+p,2);
 }
 saved=semantic;
 CHECK(native_rear_bind_startup_scalars(semantic.packet,&capsule)==0);
 for(p=0;p<4;p++){
  CHECK(!semantic.packet[p].ready);
  CHECK(semantic.packet[p].regs.scalar.request_id==ids[p]);
  CHECK(semantic.packet[p].regs.scalar.startup_phase==p);
  CHECK(semantic.packet[p].regs.scalar.demux_q10[2]==1024+p*16+2);
  CHECK(semantic.packet[p].regs.scalar.pdpc_q12[3]==4096+p*32+3);
  CHECK(semantic.packet[p].regs.period.valid_mask==saved.packet[p].regs.period.valid_mask);
  CHECK(semantic.packet[p].dmi.request_id==saved.packet[p].dmi.request_id);
 }
 saved=semantic;
 bad=capsule;bad.data[16+3*48]=99;
 CHECK(native_rear_bind_startup_scalars(semantic.packet,&bad)==-ESTALE);
 CHECK(memcmp(&saved,&semantic,sizeof(saved))==0);
 bad=capsule;bad.data[16+3*48+8]=0;
 CHECK(native_rear_bind_startup_scalars(semantic.packet,&bad)==-EPROTO);
 CHECK(memcmp(&saved,&semantic,sizeof(saved))==0);
 bad=capsule;bad.data[16+3*48+16+1]=0x80;
 CHECK(native_rear_bind_startup_scalars(semantic.packet,&bad)==-ERANGE);
 CHECK(memcmp(&saved,&semantic,sizeof(saved))==0);
 bad=capsule;bad.data[16+3*48+12]=1;
 CHECK(native_rear_bind_startup_scalars(semantic.packet,&bad)==-EPROTO);
 CHECK(memcmp(&saved,&semantic,sizeof(saved))==0);
 semantic.packet[3].ready=true;saved=semantic;
 CHECK(native_rear_bind_startup_scalars(semantic.packet,&capsule)==-EBUSY);
 CHECK(memcmp(&saved,&semantic,sizeof(saved))==0);
 CHECK(native_rear_scalars_validate(capsule.data,sizeof(capsule)-1)==-EINVAL);
 #undef PUTCAP
}

int main(void){
 struct camss c={0};struct vfe_device v={.camss=&c};struct v4l2_subdev sensor={0};
 scalar_binding_test();
 positive_and_corruption_tests(&v,&sensor);
 failure_atomicity_tests(&v);
 semantic_rejection_tests(&v);
 once_and_denial_test(&v,&sensor);
 printf("NATIVE_REAR_PREPARED_HANDOFF_PASS assertions=%u hardware_callbacks=%u\n",tests,hardware_calls);
 return 0;
}
