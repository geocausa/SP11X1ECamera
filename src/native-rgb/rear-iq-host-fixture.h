/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual BF/CST/BPC packers and seed. Unrelated fields omitted in host only. */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int8_t s8;
typedef int16_t s16;
typedef int32_t s32;
#define __used __attribute__((used))
#define __maybe_unused __attribute__((unused))
#define GFP_KERNEL 0
#define E007Y_STARTUP_PACKETS 4
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define BIT(n) (1U<<(n))
#undef static_assert
#define static_assert(x) _Static_assert(x, #x)
typedef int (*e006m_scalar_fn)(void *, u16, u32 *);
static unsigned iq_allocations;
static size_t iq_last_allocation_size;
static bool iq_fail_allocation, iq_freed_uncleared;
static void *kzalloc(size_t n, int flags) {
 void *p; (void)flags; if(iq_fail_allocation)return NULL;
 p=calloc(1,n);if(p){iq_allocations++;iq_last_allocation_size=n;}return p;
}
static void memzero_explicit(void *p, size_t n) { memset(p,0,n); }
static void kfree(void *p) {
 if(p){const u8 *b=p;size_t i;
 for(i=0;i<iq_last_allocation_size;i++)if(b[i])iq_freed_uncleared=true;
 iq_allocations--;free(p);}
}
static void put_unaligned_le32(u32 v,void *p){
 u8 *b=p;b[0]=v;b[1]=v>>8;b[2]=v>>16;b[3]=v>>24;
}
#include "camss-e006z-clean-scalar-bank.inc"
#include "camss-e006q-mnds23.inc"
#include "camss-e006r-cst12.inc"
#include "camss-e007a-bpcabf411.inc"
#include "camss-e007b-bfstats25.inc"
#include "camss-e007e-bfstats25-dmi.inc"
struct iq_f {struct e007e_bf_dmi_state bfstats25; u8 unrelated[64];};
struct iq_i {struct iq_f dmi;};
struct iq_q {struct iq_i dmi;};
struct iq_s {struct iq_q dmi;};
struct iq_t {struct iq_s dmi;};
struct iq_u {struct iq_t dmi;};
struct e007v_rear_dmi_state {struct iq_u dmi;};
struct e008o_rear_packet_semantics {
 struct {
  struct e006z_rear_scalar_state scalar;
  struct e006q_mnds23_state mnds;
  struct e006r_cst12_state cst;
  struct e007a_bpcabf411_calc_state bpcabf;
  struct e007b_bfstats25_calc_state bfstats;
  u8 unrelated[64];
 } regs;
 struct e007v_rear_dmi_state dmi;
 u64 request_id;bool ready;
};
struct e008o_rear_semantic_set {struct e008o_rear_packet_semantics packet[4];bool sealed;};
#include "camss-vfe-e008t-rear-bf-semantic.inc"
#include "camss-e011as-cold-gamma-policy.inc"
#include "native-rear-startup-iq.inc"
static int native_rear_iq_test_initialize(struct e008o_rear_packet_semantics base[4],
 struct native_rear_startup_iq_input *input){
 static const u64 ids[4]={4,5,6,6};unsigned p;
 memset(base,0x5a,sizeof(*base)*4);memset(input,0,sizeof(*input));
 for(p=0;p<4;p++){
  struct native_rear_packet_iq_input *i=&input->packet[p];
  base[p].ready=false;base[p].request_id=i->request_id=ids[p];
  base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STARTUP;
  base[p].regs.scalar.startup_phase=i->phase=p;
  base[p].regs.scalar.request_id=ids[p];
  base[p].regs.mnds.input_width=i->active_width=4064;
  base[p].regs.mnds.input_height=i->active_height=2286;
  if(p)i->af=(struct native_rear_af_rect){1524,858,1016,571};
  i->controls_valid=true;
  i->cst.enabled=true;i->cst.c01=i->cst.c11=i->cst.c21=4095;
  i->cst.m00=1024;i->cst.m11=1024;i->cst.m22=1024;
  i->bpcabf.signed10[0]=-100-p;i->bpcabf.signed10[1]=100+p;
  i->bpcabf.unsigned9[0]=200+p;i->bpcabf.unsigned9[1]=210+p;
  i->bpcabf.nibble4[0]=p;i->bpcabf.nibble4[1]=p+1;
  memset(i->bpcabf.byte_group0,10+p,sizeof(i->bpcabf.byte_group0));
  memset(i->bpcabf.byte_group1,20+p,sizeof(i->bpcabf.byte_group1));
  memset(i->bpcabf.nibble_group,5+p,sizeof(i->bpcabf.nibble_group));
 }
 return 0;
}
