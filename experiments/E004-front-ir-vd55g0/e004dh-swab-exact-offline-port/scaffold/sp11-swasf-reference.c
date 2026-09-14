/* SPDX-License-Identifier: MIT */
/*
 * Windows-authoritative full SWASF scalar composition.
 *
 * This composes the independently byte-exact helper, C3E8 and CD90 stages
 * using the root-worker glue recovered from QcISPTrustlet8380.dll.  Windows
 * remains normative; the decompile is explanatory only.
 */
#include "sp11-swasf-reference.h"
#include "sp11-swasf-helpers.h"
#include "sp11-swasf-c3e8.h"
#include "sp11-swasf-cd90.h"

static int clampi(int v, int lo, int hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static int16_t sample16(const int16_t *src, uint32_t width, uint32_t height,
                        int x, int y)
{
    x = clampi(x, 0, (int)width - 1);
    y = clampi(y, 0, (int)height - 1);
    return src[(size_t)y * width + (uint32_t)x];
}

static int16_t smooth5_at(const int16_t *src, uint32_t width, uint32_t height,
                          int x, int y)
{
    static const int16_t h[5] = { 1, 4, 6, 4, 1 };
    int32_t acc = 0;
    int r, c;

    for (r = 0; r < 5; ++r)
        for (c = 0; c < 5; ++c)
            acc += (int32_t)h[r] * h[c] *
                   sample16(src, width, height, x + c - 2, y + r - 2);
    return (int16_t)((acc + 0x80) >> 8);
}

static void extrema4(const int16_t *src, uint32_t width, uint32_t height,
                     int center_x, int center_y, int16_t pos[4], int16_t neg[4])
{
    int16_t rows[5][8];
    int r, c;

    for (r = 0; r < 5; ++r)
        for (c = 0; c < 8; ++c)
            rows[r][c] = sample16(src, width, height,
                                  center_x + c - 2, center_y + r - 2);
    sp11_swasf_local_extrema_5x5(rows, pos, neg);
}

static uint8_t activity_at(const int16_t *raw, const int16_t *smooth,
                           uint32_t width, uint32_t height,
                           int x, int y, int16_t scale)
{
    int16_t rows[5][8];
    int r, c;

    for (r = 0; r < 5; ++r) {
        for (c = 0; c < 5; ++c)
            rows[r][c] = sample16(raw, width, height,
                                  x + c - 2, y + r - 2);
        for (; c < 8; ++c)
            rows[r][c] = rows[r][4];
    }
    return sp11_swasf_c078_activity(rows,
            smooth[(size_t)y * width + (uint32_t)x], scale);
}

static void process_tile(uint8_t *dst, const int16_t *raw, const int16_t *smooth,
                         uint32_t width, uint32_t height,
                         uint32_t x0, uint32_t y,
                         const uint32_t tune[SP11_SWASF_TUNING_WORDS],
                         int16_t activity_scale)
{
    int16_t raw_pos[8], raw_neg[8], sm_pos[8], sm_neg[8];
    int16_t p4[8], p5[8], p6[8], p7[8], p10[8], p11[8], p12[8];
    int32_t p8[8];
    uint8_t p3[8], p9[8];
    int16_t a[4], b[4];
    unsigned i;

    extrema4(raw, width, height, (int)x0, (int)y, a, b);
    for (i = 0; i < 4; ++i) { raw_pos[i] = a[i]; raw_neg[i] = b[i]; }
    extrema4(raw, width, height, (int)x0 + 4, (int)y, a, b);
    for (i = 0; i < 4; ++i) { raw_pos[i + 4] = a[i]; raw_neg[i + 4] = b[i]; }

    extrema4(smooth, width, height, (int)x0, (int)y, a, b);
    for (i = 0; i < 4; ++i) { sm_pos[i] = a[i]; sm_neg[i] = b[i]; }
    extrema4(smooth, width, height, (int)x0 + 4, (int)y, a, b);
    for (i = 0; i < 4; ++i) { sm_pos[i + 4] = a[i]; sm_neg[i + 4] = b[i]; }

    for (i = 0; i < 8; ++i) {
        p4[i] = raw_pos[i] > sm_pos[i] ? raw_pos[i] : sm_pos[i];
        p5[i] = raw_neg[i] < sm_neg[i] ? raw_neg[i] : sm_neg[i];
        p6[i] = sm_pos[i];
        p7[i] = sm_neg[i];
        p3[i] = activity_at(raw, smooth, width, height,
                            (int)x0 + (int)i, (int)y, activity_scale);
        p11[i] = 0x100;
        p12[i] = 0x100;
    }

    sp11_swasf_c3e8_tile(raw, (int)width,
                         (int)x0, (int)x0 + 8, (int)y, (int)y + 1,
                         (int)width, (int)height, p8, p9, p10);
    sp11_swasf_cd90(raw + (size_t)y * width + x0,
                    dst + (size_t)y * width + x0,
                    p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, tune);
}

int sp11_swasf_reference(uint8_t *dst, size_t dst_len,
                         const uint8_t *src, size_t src_len,
                         uint32_t width, uint32_t height,
                         int16_t *raw16, size_t raw_count,
                         int16_t *smooth16, size_t smooth_count,
                         const uint32_t tune[SP11_SWASF_TUNING_WORDS],
                         int16_t activity_scale)
{
    size_t pixels;
    uint32_t x, y, tile_count, tile;

    if (!dst || !src || !raw16 || !smooth16 || !tune ||
        width < 8 || !height || activity_scale < 0)
        return -1;
    if ((size_t)width > (size_t)-1 / (size_t)height)
        return -2;
    pixels = (size_t)width * height;
    if (dst_len < pixels || src_len < pixels ||
        raw_count < pixels || smooth_count < pixels)
        return -2;

    for (y = 0; y < height; ++y)
        for (x = 0; x < width; ++x)
            raw16[(size_t)y * width + x] =
                (int16_t)((uint16_t)src[(size_t)y * width + x] << 2);

    for (y = 0; y < height; ++y)
        for (x = 0; x < width; ++x)
            smooth16[(size_t)y * width + x] =
                smooth5_at(raw16, width, height, (int)x, (int)y);

    tile_count = (width + 7u) >> 3;
    for (y = 0; y < height; ++y) {
        for (tile = 0; tile < tile_count; ++tile) {
            uint32_t x0 = tile << 3;
            if (x0 + 8u > width)
                x0 = width - 8u;
            process_tile(dst, raw16, smooth16, width, height,
                         x0, y, tune, activity_scale);
        }
    }
    return 0;
}
