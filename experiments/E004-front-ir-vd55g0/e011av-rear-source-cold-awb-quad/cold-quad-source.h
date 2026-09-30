/* SPDX-License-Identifier: MIT */
#ifndef E011AV_COLD_QUAD_SOURCE_H
#define E011AV_COLD_QUAD_SOURCE_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
typedef u8 e011av_u8;
typedef u32 e011av_u32;
#else
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
typedef uint8_t e011av_u8;
typedef uint32_t e011av_u32;
#endif
/* Qualified bgStatsConfigV1 v1.0 Default root, serialized size 93.
 * Caller must independently validate symbol identity and selector ancestry.
 * Only the boolean at wire+24 is decoded; no aggregate payload claim.
 * Output is untouched on every rejected input.
 */
static inline int e011av_decode_cold_quad(const e011av_u8 *wire,
    size_t bytes, unsigned int major, unsigned int minor,
    e011av_u32 *out)
{
    e011av_u32 value;
    if (!wire || !out || bytes != 93 || major != 1 || minor != 0)
        return -EINVAL;
    value = (e011av_u32)wire[24] | ((e011av_u32)wire[25] << 8) |
        ((e011av_u32)wire[26] << 16) | ((e011av_u32)wire[27] << 24);
    if (value > 1)
        return -ERANGE;
    *out = value;
    return 0;
}
#endif
