/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_REAR_VIDEO_DMA_H
#define NATIVE_REAR_VIDEO_DMA_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
#else
#include <stdint.h>
#include <errno.h>
typedef uint32_t u32;
typedef uint64_t u64;
#endif
#include "native-rear-nv12-layout.h"

/* Only mapped device addresses are admitted, never physical SG addresses.
 * This describes an existing VB2 mapping; it allocates/frees nothing and
 * grants no hardware or buffer-completion authority.
 */
struct native_rear_video_dma {
 u32 y_iova;
 u32 uv_iova;
 u64 mapped_bytes;
};
struct native_rear_video_dma_scan {
 u64 base, next, bytes;
 unsigned int segments;
 int error;
};

static inline int
native_rear_video_dma_append(struct native_rear_video_dma_scan *scan,
                            u64 iova, u64 bytes)
{
 if (!scan)
  return -EINVAL;
 if (scan->error)
  return scan->error;
 if (!bytes || !iova || iova >= 0x100000000ULL ||
     bytes > 0x100000000ULL - iova) {
  scan->error = -ERANGE;
  return scan->error;
 }
 if (!scan->segments) {
  if (iova & 4095U) {
   scan->error = -ERANGE;
   return scan->error;
  }
  scan->base = iova;
 } else if (iova != scan->next) {
  scan->error = -ERANGE;
  return scan->error;
 }
 if (scan->segments == (unsigned int)-1) {
  scan->error = -EOVERFLOW;
  return scan->error;
 }
 scan->bytes += bytes; /* Contiguous validated 32-bit aperture bounds the sum. */
 scan->next = iova + bytes;
 scan->segments++;
 return 0;
}

static inline int
native_rear_video_dma_finish(const struct native_rear_video_dma_scan *scan,
                            u64 plane_bytes, struct native_rear_video_dma *out)
{
 struct native_rear_video_dma candidate;
 if (!scan || !out)
  return -EINVAL;
 if (scan->error)
  return scan->error;
 if (!scan->segments || plane_bytes < NATIVE_REAR_NV12_BYTES ||
     scan->bytes < plane_bytes)
  return -ENOSPC;
 candidate.y_iova = (u32)scan->base;
 candidate.uv_iova = (u32)(scan->base + NATIVE_REAR_NV12_UV_OFFSET);
 candidate.mapped_bytes = scan->bytes;
 *out = candidate; /* Publish atomically only after the whole SG mapping passed. */
 return 0;
}
#endif
