/* SPDX-License-Identifier: MIT */
/*
 * Scalar transcriptions of shipping Windows QcISPTrustlet8380.dll helpers:
 *   FUN_18001b848 -> local 5x5 extrema, gain 0x99/256 with rounding
 *   FUN_18001c078 -> symmetric 5x5 curvature/activity metric
 *
 * Windows helper-oracle output is normative. Static NEON reverse engineering
 * is used only to express the same arithmetic in portable scalar C.
 */
#include "sp11-swasf-helpers.h"

static int32_t iabs32(int32_t v) { return v < 0 ? -v : v; }
static int32_t cap32(int32_t v, int32_t cap) { return v > cap ? cap : v; }

void sp11_swasf_local_extrema_5x5(const int16_t rows[5][8], int16_t pos[4], int16_t neg[4])
{
    int i, r, c;
    for (i = 0; i < 4; ++i) {
        int32_t center = rows[2][i + 2];
        int32_t max_pos = 0, max_neg = 0;
        for (r = 0; r < 5; ++r) {
            for (c = i; c < i + 5; ++c) {
                int32_t d = (int32_t)rows[r][c] - center;
                if (d > max_pos) max_pos = d;
                if (-d > max_neg) max_neg = -d;
            }
        }
        pos[i] = (int16_t)((max_pos * 0x99 + 0x80) >> 8);
        neg[i] = (int16_t)((max_neg * 0x99 + 0x80) >> 8);
    }
}

uint8_t sp11_swasf_c078_activity(const int16_t rows[5][8], int16_t center, int16_t scale)
{
    static const int32_t h[5] = { 1, 4, 6, 4, 1 };
    int32_t twice_center = (int32_t)center * 2;
    int32_t cap = (((uint16_t)scale << 3) & 0x7f8);
    int32_t sum = 0;
    int c;

    for (c = 0; c < 5; ++c) {
        int32_t d0 = iabs32((int32_t)rows[0][c] + rows[4][4 - c] - twice_center);
        int32_t d1 = iabs32((int32_t)rows[1][c] + rows[3][4 - c] - twice_center);
        int32_t d2 = iabs32((int32_t)rows[2][c] + rows[2][4 - c] - twice_center);
        d0 = cap32(d0, cap);
        d1 = cap32(d1, cap);
        d2 = cap32(d2, cap);
        sum += h[c] * (2 * d0 + 8 * d1 + 6 * d2);
    }
    sum = (sum + 0x40) >> 7;
    if (sum > 0xff) sum = 0xff;
    return (uint8_t)sum;
}
