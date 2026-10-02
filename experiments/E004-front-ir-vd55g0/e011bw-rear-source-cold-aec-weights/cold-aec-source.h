/* SPDX-License-Identifier: MIT */
#ifndef E011BW_COLD_AEC_SOURCE_H
#define E011BW_COLD_AEC_SOURCE_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
typedef u8 e011bw_u8;
typedef u32 e011bw_u32;
#else
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
typedef uint8_t e011bw_u8;
typedef uint32_t e011bw_u32;
#endif
static inline e011bw_u32 e011bw_le32(const e011bw_u8 *p)
{
    return (e011bw_u32)p[0] | ((e011bw_u32)p[1] << 8) |
        ((e011bw_u32)p[2] << 16) | ((e011bw_u32)p[3] << 24);
}
/* Caller qualifies aecxhwstatsconfig v10.0 Default, count4, and its
 * gridStatsConfig v0.0 packed child. This decoder covers only invariant
 * weights in four 101-byte records; it does not select a filename/profile,
 * resolve child symbols, construct the manager or authorize hardware.
 * Differing grid weights are unsupported. Rejection never changes out.
 */
static inline int e011bw_decode_invariant_cold_weights(
    const e011bw_u8 *wire, size_t bytes, unsigned int major,
    unsigned int minor, unsigned int count, e011bw_u32 out[3])
{
    e011bw_u32 values[3];
    unsigned int lane, grid;
    if (!wire || !out || bytes != 404 || major != 0 || minor != 0 || count != 4)
        return -EINVAL;
    for (lane = 0; lane < 3; lane++) {
        values[lane] = e011bw_le32(wire + 20 + 4 * lane);
        /* IEEE754 unit interval, with negative zero admitted as zero. */
        if (values[lane] != 0x80000000U && values[lane] > 0x3f800000U)
            return -ERANGE;
        for (grid = 1; grid < 4; grid++)
            if (e011bw_le32(wire + grid * 101 + 20 + 4 * lane) != values[lane])
                return -EOPNOTSUPP;
    }
    for (lane = 0; lane < 3; lane++)
        out[lane] = values[lane];
    return 0;
}
#endif
