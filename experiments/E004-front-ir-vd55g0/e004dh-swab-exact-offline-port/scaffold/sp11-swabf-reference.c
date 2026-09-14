/* SPDX-License-Identifier: MIT */
/*
 * Scalar transcription of the shipping Windows SecureISP SWABF pixel rule.
 * Windows live-oracle tuning is normative; the static trustlet decompile is
 * used only to recover the arithmetic and boundary traversal.
 */
#include "sp11-swabf-reference.h"

const struct sp11_swabf_tuning sp11_swabf_windows_oracle_tuning = {
    .weight = { 2000, 1990, 1960, 1911, 1846, 1670, 1452, 1213,
                 973,  750,  556,  395,  270,  177,  142,  112 },
    .threshold = 128,
};

static int32_t sp11_asr14(int32_t v)
{
    if (v >= 0)
        return v >> 14;
    return -(int32_t)(((uint32_t)(-v) + 0x3fffU) >> 14);
}

static uint32_t sp11_wrap(int32_t p, uint32_t n)
{
    if (p < 0)
        return n - 1;
    if ((uint32_t)p >= n)
        return 0;
    return (uint32_t)p;
}

int sp11_swabf_reference(uint8_t *dst, size_t dst_len,
                         const uint8_t *src, size_t src_len,
                         uint32_t width, uint32_t height,
                         const struct sp11_swabf_tuning *tuning)
{
    static const int8_t dx[8] = { 1, -1, 0, 1, -1, 0, 1, -1 };
    static const int8_t dy[8] = { 1,  1, 1,-1, -1,-1, 0,  0 };
    size_t pixels;
    uint32_t y, x, k;

    if (!dst || !src || !tuning || !width || !height)
        return -1;
    if ((size_t)width > (size_t)-1 / (size_t)height)
        return -2;
    pixels = (size_t)width * (size_t)height;
    if (dst_len < pixels || src_len < pixels)
        return -2;

    for (y = 0; y < height; y++) {
        for (x = 0; x < width; x++) {
            size_t pos = (size_t)y * width + x;
            int32_t center = src[pos];
            int32_t acc = 0;

            for (k = 0; k < 8; k++) {
                uint32_t nx = sp11_wrap((int32_t)x + dx[k], width);
                uint32_t ny = sp11_wrap((int32_t)y + dy[k], height);
                int32_t diff = (int32_t)src[(size_t)ny * width + nx] - center;
                int32_t mag = diff < 0 ? -diff : diff;

                if (mag < tuning->threshold) {
                    uint32_t wi = (uint32_t)mag >> 1;
                    if (wi > 15)
                        wi = 15;
                    acc += (int32_t)tuning->weight[wi] * diff;
                }
            }
            dst[pos] = (uint8_t)(center + sp11_asr14(acc));
        }
    }
    return 0;
}
