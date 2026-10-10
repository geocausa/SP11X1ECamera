/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_GAMMA_H
#define NATIVE_FRONT_GAMMA_H
/* Data-only compiler, not a userspace ABI or MMIO/DMA interface.
 * Channels are semantic R,G,B. The eventual kernel adapter must bind them
 * to independently verified SP11 selectors; this code assigns no selector.
 * The native 256-word layout is base12 + signed delta12. Points include
 * the 257th endpoint. No proprietary curve, address or startup profile here.
 */
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
typedef u8 nf_gamma_u8;
typedef u16 nf_gamma_u16;
typedef u32 nf_gamma_u32;
#else
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
typedef uint8_t nf_gamma_u8;
typedef uint16_t nf_gamma_u16;
typedef uint32_t nf_gamma_u32;
#endif
#define NF_GAMMA_CHANNELS 3U
#define NF_GAMMA_POINTS 257U
#define NF_GAMMA_WORDS 256U
#define NF_GAMMA_POINT_COUNT (NF_GAMMA_CHANNELS * NF_GAMMA_POINTS)
#define NF_GAMMA_WORD_COUNT (NF_GAMMA_CHANNELS * NF_GAMMA_WORDS)
#define NF_GAMMA_BYTES (NF_GAMMA_WORD_COUNT * 4U)

static inline int nf_gamma_overlap(const void *a, size_t an,
                                    const void *b, size_t bn)
{
 unsigned long x=(unsigned long)a, y=(unsigned long)b;
 return x <= y ? y-x < an : x-y < bn;
}
static inline void nf_gamma_put32(nf_gamma_u8 *out, nf_gamma_u32 value)
{
 out[0]=value;out[1]=value>>8;out[2]=value>>16;out[3]=value>>24;
}
/* Validate all channels before changing output; never silently clamp a slope. */
static inline int native_front_gamma12_pack(const nf_gamma_u16 *points,
 size_t count, nf_gamma_u8 *out, size_t bytes)
{
 unsigned int c,i;
 if (!points || !out || count!=NF_GAMMA_POINT_COUNT || bytes!=NF_GAMMA_BYTES)
  return -EINVAL;
 if (nf_gamma_overlap(points,count*sizeof(*points),out,bytes))
  return -EINVAL;
 for(c=0;c<NF_GAMMA_CHANNELS;c++)
  for(i=0;i<NF_GAMMA_POINTS;i++) {
   unsigned int at=c*NF_GAMMA_POINTS+i;
   int delta;
   if(points[at]>4095)return -ERANGE;
   if(i==NF_GAMMA_WORDS)continue;
   delta=(int)points[at+1]-(int)points[at];
   if(delta < -2048 || delta > 2047)return -ERANGE;
  }
 for(c=0;c<NF_GAMMA_CHANNELS;c++)
  for(i=0;i<NF_GAMMA_WORDS;i++) {
   unsigned int at=c*NF_GAMMA_POINTS+i;
   int delta=(int)points[at+1]-(int)points[at];
   nf_gamma_u32 word=points[at]|(((nf_gamma_u32)delta&0xfffU)<<12);
   nf_gamma_put32(out+4*(c*NF_GAMMA_WORDS+i),word);
  }
 return 0;
}
static inline unsigned int nf_gamma10_scale12(unsigned int value)
{
 /* Exact 0/1023 -> 0/4095 endpoints, nearest integer everywhere else. */
 return (value*4095U+511U)/1023U;
}
static inline int nf_gamma10_delta(nf_gamma_u32 word)
{
 unsigned int raw=(word>>10)&0x3ffU;
 return raw&0x200U ? (int)raw-1024 : (int)raw;
}
/* Compatibility helper for the proposed upstream 10+10-bit table semantics.
 * This is NOT the UAPI block parser. That parser still needs block/header/flag
 * validation, frame identity, ownership and metadata-queue integration.
 * Require contiguous base/delta semantics, a representable endpoint and
 * native slopes. No assumption that a table is a calibrated tone curve.
 */
static inline int native_front_gamma10_expand(const nf_gamma_u32 *words,
 size_t count, nf_gamma_u8 *out, size_t bytes)
{
 unsigned int c,i;
 if (!words || !out || count!=NF_GAMMA_WORD_COUNT || bytes!=NF_GAMMA_BYTES)
  return -EINVAL;
 if (nf_gamma_overlap(words,count*sizeof(*words),out,bytes))
  return -EINVAL;
 for(c=0;c<NF_GAMMA_CHANNELS;c++)
  for(i=0;i<NF_GAMMA_WORDS;i++) {
   unsigned int at=c*NF_GAMMA_WORDS+i;
   nf_gamma_u32 word=words[at];
   int base=word&0x3ffU, end=base+nf_gamma10_delta(word),delta;
   if(word&~0xfffffU)return -EINVAL;
   if(end<0 || end>1023)return -ERANGE;
   if(i+1<NF_GAMMA_WORDS && (words[at+1]&0x3ffU)!=(unsigned int)end)
    return -EINVAL;
   delta=(int)nf_gamma10_scale12(end)-(int)nf_gamma10_scale12(base);
   if(delta < -2048 || delta > 2047)return -ERANGE;
  }
 for(c=0;c<NF_GAMMA_CHANNELS;c++)
  for(i=0;i<NF_GAMMA_WORDS;i++) {
   unsigned int at=c*NF_GAMMA_WORDS+i;
   int base=words[at]&0x3ffU,end=base+nf_gamma10_delta(words[at]);
   unsigned int start=nf_gamma10_scale12(base);
   int delta=(int)nf_gamma10_scale12(end)-(int)start;
   nf_gamma_put32(out+4*at,start|(((nf_gamma_u32)delta&0xfffU)<<12));
  }
 return 0;
}

static inline nf_gamma_u32 nf_gamma_get32(const nf_gamma_u8 *p)
{
 return (nf_gamma_u32)p[0] | (nf_gamma_u32)p[1] << 8 |
        (nf_gamma_u32)p[2] << 16 | (nf_gamma_u32)p[3] << 24;
}

/* Revalidate prepared data at the kernel backend boundary. This verifies
 * encoding and continuity, not monotonicity, tuning quality or hardware.
 */
static inline int native_front_gamma12_validate(const nf_gamma_u8 *data,
                                                size_t bytes)
{
 unsigned int c, i;

 if (!data || bytes != NF_GAMMA_BYTES)
  return -EINVAL;
 for (c = 0; c < NF_GAMMA_CHANNELS; c++)
  for (i = 0; i < NF_GAMMA_WORDS; i++) {
   const nf_gamma_u8 *p = data + 4 * (c * NF_GAMMA_WORDS + i);
   nf_gamma_u32 word = nf_gamma_get32(p);
   unsigned int raw = (word >> 12) & 0xfffU;
   int delta = raw & 0x800U ? (int)raw - 4096 : (int)raw;
   int end = (int)(word & 0xfffU) + delta;

   if (word & 0xff000000U)
    return -EINVAL;
   if (end < 0 || end > 4095)
    return -ERANGE;
   if (i + 1 < NF_GAMMA_WORDS &&
       (nf_gamma_get32(p + 4) & 0xfffU) != (unsigned int)end)
    return -EINVAL;
  }
 return 0;
}
#endif
