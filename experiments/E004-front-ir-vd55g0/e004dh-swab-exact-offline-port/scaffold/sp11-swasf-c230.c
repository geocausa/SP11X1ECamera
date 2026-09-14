/* SPDX-License-Identifier: MIT */
/* Scalar transcription of Windows QcISPTrustlet8380.dll FUN_18001c230. */
#include "sp11-swasf-c230.h"

static const int16_t k_hp[7][7] = {
    { -7, -23, -41, -49, -41, -23,  -7 },
    {-23, -73, -74, -53, -74, -73, -23 },
    {-41, -74,  89, 242,  89, -74, -41 },
    {-49, -53, 242,   0, 242, -53, -49 },
    {-41, -74,  89, 242,  89, -74, -41 },
    {-23, -73, -74, -53, -74, -73, -23 },
    { -7, -23, -41, -49, -41, -23,  -7 },
};

static const int16_t k_lp[7][7] = {
    {0,  0,  0,  0,  0,  0, 0},
    {0,  9, 23, 31, 23,  9, 0},
    {0, 23, 60, 82, 60, 23, 0},
    {0, 31, 82,  0, 82, 31, 0},
    {0, 23, 60, 82, 60, 23, 0},
    {0,  9, 23, 31, 23,  9, 0},
    {0,  0,  0,  0,  0,  0, 0},
};

static int32_t srshr64(int64_t v, unsigned shift)
{
    return (int32_t)((v + ((int64_t)1 << (shift - 1))) >> shift);
}

void sp11_swasf_c230(const int16_t rows[7][8], const int16_t tail[2],
                     int32_t out4[2], uint8_t out2[2])
{
    int lane, r, c;

    for (lane = 0; lane < 2; ++lane) {
        int64_t hp = (int64_t)508 * tail[lane];
        int64_t lp = (int64_t)112 * tail[lane];

        for (r = 0; r < 7; ++r) {
            for (c = 0; c < 7; ++c) {
                int32_t px = rows[r][c + lane];
                hp += (int64_t)k_hp[r][c] * px;
                lp += (int64_t)k_lp[r][c] * px;
            }
        }

        out4[lane] = srshr64(hp, 8);
        out2[lane] = (uint8_t)srshr64(lp, 12);
    }
}
