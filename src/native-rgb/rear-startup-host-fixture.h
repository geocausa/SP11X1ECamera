/* SPDX-License-Identifier: MIT */
/* Host-only integration harness; allocators use malloc and synthetic IOVAs. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
typedef uint8_t u8; typedef int8_t s8;
typedef uint16_t u16; typedef int16_t s16;
typedef uint32_t u32; typedef int32_t s32;
typedef uint64_t u64; typedef int64_t s64;
typedef uint64_t dma_addr_t;
#define BIT(n) (1U << (n))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define static_assert(expr) _Static_assert((expr), #expr)
#define __used __attribute__((used))
#define __maybe_unused __attribute__((unused))
#define ALIGN(x,a) (((x)+(a)-1)&~((a)-1))
#define IS_ALIGNED(x,a) (!((x)&((a)-1)))
#define GFP_KERNEL 0
#define U32_MAX UINT32_MAX
#define min_t(t,a,b) ((t)(a) < (t)(b) ? (t)(a) : (t)(b))
#define max_t(t,a,b) ((t)(a) > (t)(b) ? (t)(a) : (t)(b))
static void memzero_explicit(void *p,size_t n) { volatile u8 *b=p;while(n--)*b++=0; }
static u32 get_unaligned_le32(const void *p) { const u8 *b=p;return (u32)b[0]|((u32)b[1]<<8)|((u32)b[2]<<16)|((u32)b[3]<<24); }
static void put_unaligned_le32(u32 v,void *p) { u8 *b=p;for(unsigned int i=0;i<4;i++)b[i]=(u8)(v>>(8*i)); }
struct device { int fixture; }; struct camss { struct device *dev; };
struct vfe_device { struct camss *camss; };
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *v) { return v&&v->camss&&v->camss->dev&&v->camss->dev->fixture==1; }
static bool vfe680_x1e_dma_span_32bit(dma_addr_t a,size_t n) { return n&&a<=UINT32_MAX&&n-1<=UINT32_MAX-a; }
static unsigned full_allocations;
static int full_fail_after=-1;
static void *kzalloc(size_t n,int flag) {
 (void)flag;
 if(full_fail_after==0)return NULL;
 if(full_fail_after>0)full_fail_after--;
 void *p=calloc(1,n);if(p)full_allocations++;return p;
}
static void *kcalloc(size_t n,size_t size,int flag) {return kzalloc(n*size,flag);}
static void kfree(void *p) {if(p){full_allocations--;free(p);}}
static void *dma_alloc_coherent(struct device *d,size_t n,dma_addr_t *a,int flag) {
    static dma_addr_t next=0x10000000;
    (void)d;(void)flag;*a=next;next+=ALIGN(n,0x1000);return kzalloc(n,flag);
}
static void dma_free_coherent(struct device *d,size_t n,void *p,dma_addr_t a) { (void)d;(void)n;(void)a;kfree(p); }
#include "camss-e006g-rear-materializer.inc"
#include "camss-e006j-rear-register-bindings.inc"
#include "camss-e006m-rear-startup-bindings.inc"
#include "camss-e006o-rear-steady-singletons.inc"
#include "camss-e006p-crop-roundclamp.inc"
#include "camss-e006q-mnds23.inc"
#include "camss-e006r-cst12.inc"
#include "camss-e006s-bc101.inc"
#include "camss-e006t-small-iq.inc"
#include "camss-e006u-bhist16.inc"
#include "camss-e006v-rsstats14.inc"
#include "camss-e006w-aecbe17.inc"
#include "camss-e006x-tintlessbg17.inc"
#include "camss-e006y-awbbg17.inc"
#include "camss-e006z-clean-scalar-bank.inc"
#include "camss-e007a-bpcabf411.inc"
#include "camss-e007b-bfstats25.inc"
#include "camss-e007c-period-cfg.inc"
#include "camss-e007d-register-integration.inc"
#include "camss-e007e-bfstats25-dmi.inc"
#include "camss-e007f-dmi-integration.inc"
#include "camss-e007i-rear-lsc-handoff.inc"
#include "camss-e007q-rear-gtm-handoff.inc"
#include "camss-e007s-zero-stable.inc"
#include "camss-e007t-gamma151.inc"
#include "camss-e007u-bpcabf411.inc"
#include "camss-e007v-dsx101.inc"
#include "camss-e007w-period-cfg.inc"
#include "camss-e007x-bhist16-startup-dmi.inc"
#include "camss-e007y-rear-startup.inc"
#include "camss-vfe-e008l-rear-command-dma.inc"
#include "native-rear-prepared-commands.inc"
#include "camss-vfe-e008o-rear-semantic-state.inc"
#include "camss-vfe-e008t-rear-bf-semantic.inc"
#include "camss-e011as-cold-gamma-policy.inc"
#include "native-rear-scalar-binding.inc"
#include "native-rear-startup-geometry.inc"
#include "native-rear-startup-statistics.inc"
#include "native-rear-startup-iq.inc"
#include "native-rear-startup-compose.inc"
