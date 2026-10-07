/* SPDX-License-Identifier: GPL-2.0-only */
/* Experimental platform metadata; no upstream FourCC allocation is claimed. */
#ifndef NATIVE_FRONT_STATS_H
#define NATIVE_FRONT_STATS_H
#include <linux/types.h>
#ifdef __KERNEL__
#include <linux/errno.h>
#else
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#endif

#define NATIVE_FRONT_STATS_MAGIC 0x31535851U /* QXS1 */
#define NATIVE_FRONT_STATS_VERSION 1
#define NATIVE_FRONT_STATS_HEADER_BYTES 64U
#define NATIVE_FRONT_STATS_AEC_BYTES 0x14000U
#define NATIVE_FRONT_STATS_BHIST_BYTES 0x1000U
#define NATIVE_FRONT_STATS_AWB_BYTES 0x3c000U
#define NATIVE_FRONT_STATS_TLBG_BYTES 0xf000U
#define NATIVE_FRONT_STATS_BYTES (NATIVE_FRONT_STATS_HEADER_BYTES + \
 NATIVE_FRONT_STATS_AEC_BYTES + NATIVE_FRONT_STATS_BHIST_BYTES + \
 NATIVE_FRONT_STATS_AWB_BYTES + NATIVE_FRONT_STATS_TLBG_BYTES)
#define NATIVE_FRONT_STATS_F_DISCONTINUITY 1U

/* Little-endian on the wire; layout is identical on 32- and 64-bit hosts.
 * Payload order: AEC_BE, BHist, AWB_BG, TL_BG. Sizes are exact active prefixes.
 * sequence and timestamp match the associated processed video buffer.
 * source_sequence is the hardware completion counter; it is not an app request.
 * stream_id changes at each video start. dropped counts unavailable meta buffers.
 */
struct native_front_stats_header {
 __le32 magic;
 __le16 version;
 __le16 header_bytes;
 __le64 stream_id;
 __le64 timestamp_ns;
 __le32 sequence;
 __le32 source_sequence;
 __le64 dropped;
 __le32 flags;
 __le32 aec_bytes;
 __le32 bhist_bytes;
 __le32 awb_bytes;
 __le32 tlbg_bytes;
 __le32 reserved;
};

#ifndef __KERNEL__
static inline uint32_t native_front_stats_u32(const unsigned char *p)
{
 return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
        (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static inline uint64_t native_front_stats_u64(const unsigned char *p)
{
 return native_front_stats_u32(p) | (uint64_t)native_front_stats_u32(p + 4) << 32;
}
/* The actual consumer uses this validator before reading raw statistic planes.
 * No caller outputs or raw pointers are published on malformed/stale input.
 */
static inline int native_front_stats_validate(const void *data, size_t bytes,
                                              uint64_t stream, uint32_t sequence)
{
 const unsigned char *p = (const unsigned char *)data;
 if (!p || !stream || bytes != NATIVE_FRONT_STATS_BYTES)
  return -EINVAL;
 if (native_front_stats_u32(p) != NATIVE_FRONT_STATS_MAGIC ||
     native_front_stats_u32(p + 4) !=
       (NATIVE_FRONT_STATS_HEADER_BYTES << 16 | NATIVE_FRONT_STATS_VERSION) ||
     !native_front_stats_u64(p + 16) || !native_front_stats_u32(p + 28) ||
     native_front_stats_u32(p + 44) != NATIVE_FRONT_STATS_AEC_BYTES ||
     native_front_stats_u32(p + 48) != NATIVE_FRONT_STATS_BHIST_BYTES ||
     native_front_stats_u32(p + 52) != NATIVE_FRONT_STATS_AWB_BYTES ||
     native_front_stats_u32(p + 56) != NATIVE_FRONT_STATS_TLBG_BYTES ||
     native_front_stats_u32(p + 60) ||
     (native_front_stats_u32(p + 40) & ~NATIVE_FRONT_STATS_F_DISCONTINUITY))
  return -EINVAL;
 if (native_front_stats_u64(p + 8) != stream ||
     native_front_stats_u32(p + 24) != sequence)
  return -ESTALE;
 if (native_front_stats_u64(p + 32) || native_front_stats_u32(p + 40))
  return -EPIPE;
 return 0;
}
#endif
#endif
