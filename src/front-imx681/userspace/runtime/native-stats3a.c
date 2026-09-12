// SPDX-License-Identifier: GPL-2.0-only
#include "native-stats3a.h"

#include <math.h>
#include <string.h>

#define E003I_AECBE_REGIONS_X 32u
#define E003I_AECBE_REGIONS_Y 32u
#define E003I_AECBE_REGIONS \
    (E003I_AECBE_REGIONS_X * E003I_AECBE_REGIONS_Y)
#define E003I_AECBE_RAW_STRIDE 0x50u
#define E003I_FRAME_LUMA_OUT_X 16u
#define E003I_FRAME_LUMA_OUT_Y 16u
#define E003I_FRAME_LUMA_OUT_REGIONS \
    (E003I_FRAME_LUMA_OUT_X * E003I_FRAME_LUMA_OUT_Y)
#define E003I_AECBE_PIXELS_PER_CHANNEL 1980u
#define E003I_AECBE_SUM_MASK UINT64_C(0x3ffffffff)

static uint16_t le16(const uint8_t *p)
{
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}

static uint32_t le32(const uint8_t *p)
{
    return (uint32_t)p[0] |
           ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) |
           ((uint32_t)p[3] << 24);
}

static uint64_t le64(const uint8_t *p)
{
    return (uint64_t)le32(p) | ((uint64_t)le32(p + 4) << 32);
}

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

static float fadd(float a, float b)
{
    volatile float r = a + b;
    return r;
}

static float fsub(float a, float b)
{
    volatile float r = a - b;
    return r;
}

static float fmul(float a, float b)
{
    volatile float r = a * b;
    return r;
}

static float fdiv32(float a, float b)
{
    volatile float r = a / b;
    return r;
}

int e003i_stats3a_open(const void *data, size_t bytes,
                       struct e003i_stats3a_view *out)
{
    const uint8_t *p = data;

    if (p == NULL || out == NULL || bytes != E003I_STATS3A_BYTES)
        return -1;
    if (le32(p) != E003I_STATS3A_MAGIC || le16(p + 4) != 1u ||
        le16(p + 6) != E003I_STATS3A_HEADER_BYTES)
        return -2;
    if (le32(p + 24) != 0u ||
        le32(p + 28) != E003I_STATS3A_AEC_BYTES ||
        le32(p + 32) != E003I_STATS3A_AEC_BYTES ||
        le32(p + 36) != E003I_STATS3A_BHIST_BYTES ||
        le32(p + 40) != E003I_STATS3A_AEC_BYTES + E003I_STATS3A_BHIST_BYTES ||
        le32(p + 44) != E003I_STATS3A_AWB_BYTES ||
        !(le32(p + 48) & 1u))
        return -3;

    memset(out, 0, sizeof(*out));
    out->generation = le64(p + 8);
    out->source_seq = le32(p + 16);
    out->slot = le32(p + 20);
    if (out->generation == 0u || out->source_seq == 0u || out->slot >= 2u)
        return -4;

    out->aec_raw = p + E003I_STATS3A_HEADER_BYTES;
    out->bhist_raw = (const uint32_t *)(
        p + E003I_STATS3A_HEADER_BYTES + E003I_STATS3A_AEC_BYTES);
    out->awb_raw = p + E003I_STATS3A_HEADER_BYTES +
                   E003I_STATS3A_AEC_BYTES + E003I_STATS3A_BHIST_BYTES;
    return 0;
}

int e003i_aecbe_frame_luma(
    const uint8_t aec_raw[E003I_STATS3A_AEC_BYTES], float *out_luma)
{
    const float r_coeff = f32bits(UINT32_C(0x3e991687));
    const float g_coeff = f32bits(UINT32_C(0x3f1645a2));
    const float b_coeff = f32bits(UINT32_C(0x3de978d5));
    const float scale = f32bits(UINT32_C(0x3504655e));
    float bins[E003I_FRAME_LUMA_OUT_REGIONS];
    uint8_t counts[E003I_FRAME_LUMA_OUT_REGIONS];
    float weight_sum = 0.0f;
    float weighted_sum = 0.0f;
    unsigned i;

    if (aec_raw == NULL || out_luma == NULL)
        return -1;

    memset(bins, 0, sizeof(bins));
    memset(counts, 0, sizeof(counts));

    for (i = 0; i < E003I_AECBE_REGIONS; ++i) {
        const uint8_t *r = aec_raw + i * E003I_AECBE_RAW_STRIDE;
        uint64_t r_sum = le64(r + 0x00) & E003I_AECBE_SUM_MASK;
        uint64_t gr_sum = le64(r + 0x08) & E003I_AECBE_SUM_MASK;
        uint64_t gb_sum = le64(r + 0x10) & E003I_AECBE_SUM_MASK;
        uint64_t b_sum = le64(r + 0x18) & E003I_AECBE_SUM_MASK;
        unsigned row = i / E003I_AECBE_REGIONS_X;
        unsigned col = i % E003I_AECBE_REGIONS_X;
        unsigned out_index;
        double value;
        float v, old, delta, step;

        if (le16(r + 0x06) != E003I_AECBE_PIXELS_PER_CHANNEL ||
            le16(r + 0x1e) != E003I_AECBE_PIXELS_PER_CHANNEL ||
            le16(r + 0x0e) != E003I_AECBE_PIXELS_PER_CHANNEL ||
            le16(r + 0x16) != E003I_AECBE_PIXELS_PER_CHANNEL)
            return -2;

        /* AB's exact ComputeLuma order: G average, then R, then B, then scale. */
        value = (double)g_coeff * (double)(gr_sum + gb_sum) * 0.5;
        value = value + (double)r_coeff * (double)r_sum;
        value = value + (double)b_coeff * (double)b_sum;
        value = value * (double)scale;
        v = (float)value;

        /* Active normal-front FrameLuma checkerboard: even row+column only. */
        if (((row + col) & 1u) != 0u)
            continue;

        out_index = (row / 2u) * E003I_FRAME_LUMA_OUT_X + (col / 2u);
        counts[out_index]++;
        old = bins[out_index];
        delta = fsub(v, old);
        step = fdiv32(delta, (float)counts[out_index]);
        bins[out_index] = fadd(old, step);
    }

    for (i = 0; i < E003I_FRAME_LUMA_OUT_REGIONS; ++i) {
        float product;
        if (counts[i] != 2u)
            return -3;
        weight_sum = fadd(weight_sum, 1.0f);
        product = fmul(1.0f, bins[i]);
        weighted_sum = fadd(weighted_sum, product);
    }

    *out_luma = fdiv32(weighted_sum, weight_sum);
    return isfinite(*out_luma) ? 0 : -4;
}
