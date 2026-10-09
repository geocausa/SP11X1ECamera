/* SPDX-License-Identifier: GPL-2.0-only */
/* Experimental QXA2 compact fixed-mode AEC transport, version2.
 * Exactly81920 valid WM11 bytes; other WM payloads are absent, never fabricated.
 * Source DMA capacity/lifetime checks still cover all six statistic allocations.
 * Driver completion time is not SOF or an optical-exposure association.
 * Raw/spatial payloads remain SAME SP11 only. Not an accepted upstream UAPI.
 */
#ifndef NATIVE_REAR_STATS_H
#define NATIVE_REAR_STATS_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
#include <linux/string.h>
typedef u8 nr_s8;
typedef u32 nr_s32;
typedef u64 nr_s64;
#else
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <string.h>
typedef uint8_t nr_s8;
typedef uint32_t nr_s32;
typedef uint64_t nr_s64;
#endif
#define NATIVE_REAR_STATS_MAGIC 0x32415851U /* QXA2; experimental, not upstream */
#define NATIVE_REAR_STATS_VERSION 2U
#define NATIVE_REAR_STATS_HEADER_BYTES 96U
#define NATIVE_REAR_STATS_PLANES 1U
#define NATIVE_REAR_STATS_PAYLOAD_BYTES (32U*32U*80U)
#define NATIVE_REAR_STATS_BYTES (NATIVE_REAR_STATS_HEADER_BYTES+NATIVE_REAR_STATS_PAYLOAD_BYTES)
#define NATIVE_REAR_STATS_F_NORMAL_AEC_GRID 4U
#define NATIVE_REAR_STATS_F_DISCONTINUITY 2U
#define NATIVE_REAR_STATS_WM_MASK (1U<<11)
static const nr_s32 native_rear_stats_capacity[6] = {0xa0000,0x1800,0x48000,0x151800,0x2d00,0x10000};
/* Wire lengths are valid active spans, not source DMA capacities. */
static const nr_s32 native_rear_stats_payload_length[6] = {NATIVE_REAR_STATS_PAYLOAD_BYTES,0,0,0,0,0};
static inline nr_s8 native_rear_stats_wm(unsigned int i)
{ const nr_s8 wm[6]={11,12,13,14,16,18}; return wm[i]; }
struct native_rear_stats_identity {
 nr_s64 stream, timestamp, owner, generation, dropped;
 nr_s32 sequence, cursor;
};
static inline nr_s32 native_rear_stats_u32(const nr_s8 *p)
{ return (nr_s32)p[0]|(nr_s32)p[1]<<8|(nr_s32)p[2]<<16|(nr_s32)p[3]<<24; }
static inline nr_s64 native_rear_stats_u64(const nr_s8 *p)
{ return native_rear_stats_u32(p)|(nr_s64)native_rear_stats_u32(p+4)<<32; }
static inline void native_rear_stats_put(nr_s8 *p,nr_s64 v,unsigned int n)
{ unsigned int i; for(i=0;i<n;i++)p[i]=(nr_s8)(v>>(8*i)); }
/* Validate all source spans and identity before writing any destination byte.
 * The transport producer runs only AFTER complete exact-owner/replacement DMA
 * proof. This helper validates the envelope; it grants no DMA lifetime right.
 */
static inline int native_rear_stats_pack(void *output,size_t bytes,
 const struct native_rear_stats_identity *id,
 const void *const planes[6],const size_t lengths[6])
{
 nr_s8 *out=(nr_s8 *)output;
 unsigned int i;
 if(!out||bytes!=NATIVE_REAR_STATS_BYTES||!id||!planes||!lengths||
    !id->stream||!id->timestamp||!id->owner||!id->generation||!id->cursor||
    id->sequence==0xffffffffU||id->generation!=(nr_s64)id->sequence+1)
  return -EINVAL;
 for(i=0;i<6;i++)
  if(!planes[i]||lengths[i]!=native_rear_stats_capacity[i])
   return -EINVAL;
 memset(out,0,NATIVE_REAR_STATS_HEADER_BYTES);
 native_rear_stats_put(out,NATIVE_REAR_STATS_MAGIC,4);
 native_rear_stats_put(out+4,NATIVE_REAR_STATS_VERSION,2);
 native_rear_stats_put(out+6,NATIVE_REAR_STATS_HEADER_BYTES,2);
 native_rear_stats_put(out+8,id->stream,8);
 native_rear_stats_put(out+16,id->timestamp,8);
 native_rear_stats_put(out+24,id->owner,8);
 native_rear_stats_put(out+32,id->generation,8);
 native_rear_stats_put(out+40,id->sequence,4);
 native_rear_stats_put(out+44,id->cursor,4);
 native_rear_stats_put(out+48,id->dropped,8);
 native_rear_stats_put(out+56,NATIVE_REAR_STATS_F_NORMAL_AEC_GRID|
                      (id->dropped?NATIVE_REAR_STATS_F_DISCONTINUITY:0),4);
 for(i=0;i<6;i++)
  native_rear_stats_put(out+60+4*i,native_rear_stats_payload_length[i],4);
 memcpy(out+NATIVE_REAR_STATS_HEADER_BYTES,planes[0],NATIVE_REAR_STATS_PAYLOAD_BYTES);
 native_rear_stats_put(out+84,NATIVE_REAR_STATS_WM_MASK,4);
 return 0;
}
/* Timestamp is driver completion time, not SOF/exposure. V4L2's timeval
 * carries microseconds; compare that precision, preserving the exact ns in
 * the envelope. Validate header identity before handing payload to IPA.
 */
static inline int native_rear_stats_validate(const void *data,size_t bytes,
 nr_s64 stream,nr_s32 sequence,nr_s64 timestamp)
{
 const nr_s8 *p=(const nr_s8 *)data;
 unsigned int i;
 if(!p||bytes!=NATIVE_REAR_STATS_BYTES||!stream||!timestamp||sequence==0xffffffffU)
  return -EINVAL;
 if(native_rear_stats_u32(p)!=NATIVE_REAR_STATS_MAGIC||
    native_rear_stats_u32(p+4)!=(NATIVE_REAR_STATS_HEADER_BYTES<<16|NATIVE_REAR_STATS_VERSION)||
    !native_rear_stats_u64(p+16)||!native_rear_stats_u64(p+24)||
    !native_rear_stats_u32(p+44)||native_rear_stats_u32(p+84)!=NATIVE_REAR_STATS_WM_MASK||
    native_rear_stats_u64(p+88))
  return -EINVAL;
 for(i=0;i<6;i++)
  if(native_rear_stats_u32(p+60+4*i)!=native_rear_stats_payload_length[i])return -EINVAL;
 if(native_rear_stats_u64(p+8)!=stream||native_rear_stats_u32(p+40)!=sequence||
    native_rear_stats_u64(p+32)!=(nr_s64)sequence+1||
    native_rear_stats_u64(p+16)/1000!=timestamp/1000)
  return -ESTALE;
 if(native_rear_stats_u64(p+48)||
    native_rear_stats_u32(p+56)!=NATIVE_REAR_STATS_F_NORMAL_AEC_GRID)
  return -EPIPE;
 return 0;
}
#endif
