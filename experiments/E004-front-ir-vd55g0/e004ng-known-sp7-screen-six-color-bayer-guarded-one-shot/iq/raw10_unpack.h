/* SPDX-License-Identifier: MIT
 * CAMERA-FREE exact MIPI RAW10 10-bit pixel unpacker. Does not touch devices.
 * Supported candidate geometries use 4-pixel/5-byte groups with per-row
 * padding. The live RGB publishers still use upper-8-bit approximation.
 */
#ifndef SP11_RGB_RAW10_UNPACK_H
#define SP11_RGB_RAW10_UNPACK_H
#include <stddef.h>
#include <stdint.h>

/* Returns 0 on success and -1 on invalid geometry/input. Caller provides
 * one complete row with accessible row_bytes, never a stale device pointer.
 * Reject partial groups rather than infer a packed tail representation.
 */
static inline int sp11_raw10_pixel(const uint8_t *row, size_t row_bytes,
                                   size_t width, size_t x, uint16_t *value)
{
    if (!row || !value || !width || (width & 3u) || x >= width ||
        width > SIZE_MAX / 5u * 4u || row_bytes < (width / 4u) * 5u)
        return -1;
    const size_t group = (x / 4u) * 5u;
    const size_t shift = (x & 3u) * 2u;
    /* The guard above ensures group+4 is in the row's packed area. */
    *value = (uint16_t)(((uint16_t)row[group + (x & 3u)] << 2u) |
                        ((row[group + 4u] >> shift) & 3u));
    return 0;
}
#endif
