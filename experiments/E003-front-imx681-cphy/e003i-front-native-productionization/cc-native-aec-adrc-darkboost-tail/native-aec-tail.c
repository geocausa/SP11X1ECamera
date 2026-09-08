// SPDX-License-Identifier: GPL-2.0-only
#include "native-aec-tail.h"
#include <math.h>
#include <stdint.h>
#include <string.h>

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

__attribute__((noinline)) static float fadd32(float a, float b)
{
    volatile float r = a + b;
    return r;
}
__attribute__((noinline)) static float fsub32(float a, float b)
{
    volatile float r = a - b;
    return r;
}
__attribute__((noinline)) static float fmul32(float a, float b)
{
    volatile float r = a * b;
    return r;
}
__attribute__((noinline)) static float fdiv32(float a, float b)
{
    volatile float r = a / b;
    return r;
}

/* Windows TwoFloats/OneFloat blend: low*(1-t) + high*t. */
static float lerp_win(float low, float high, float t)
{
    float omt = fsub32(1.0f, t);
    float a = fmul32(low, omt);
    float b = fmul32(high, t);
    return fadd32(a, b);
}

/* Three plateau regions with interpolation only across the two gaps. */
static float cap_from_lux(float lux)
{
    const float v16 = f32bits(UINT32_C(0x3fcccccd));
    const float v15 = 1.5f;
    const float v14 = f32bits(UINT32_C(0x3fb33333));

    if (lux <= 210.0f)
        return v16;
    if (lux < 260.0f)
        return lerp_win(v16, v15,
                        fdiv32(fsub32(lux, 210.0f), 50.0f));
    if (lux <= 300.0f)
        return v15;
    if (lux < 320.0f)
        return lerp_win(v15, v14,
                        fdiv32(fsub32(lux, 300.0f), 20.0f));
    return v14;
}

/* Inner 3748 table: [0,1]=>1 and [1000,1000]=>1000. */
static float short_gain_ramp(float ratio)
{
    if (ratio <= 1.0f)
        return 1.0f;
    if (ratio < 1000.0f)
        return lerp_win(1.0f, 1000.0f,
                        fdiv32(fsub32(ratio, 1.0f), 999.0f));
    return 1000.0f;
}

/* Inner 3830/3831 table: [0,1]=>1 and [2,1000]=>2. */
static float long_primary_child(float ratio)
{
    if (ratio <= 1.0f)
        return 1.0f;
    if (ratio < 2.0f)
        return lerp_win(1.0f, 2.0f, fsub32(ratio, 1.0f));
    return 2.0f;
}

/*
 * Outer 3829 table. Do not collapse the 260..300 gap even though both child
 * programs are numerically identical: Windows executes lerp(g,g,t).
 */
static float long_primary(float lux, float ratio)
{
    float g = long_primary_child(ratio);

    if (lux <= 260.0f)
        return g;
    if (lux < 300.0f)
        return lerp_win(g, g,
                        fdiv32(fsub32(lux, 260.0f), 40.0f));
    if (lux <= 320.0f)
        return g;
    if (lux < 360.0f)
        return lerp_win(g, 1.0f,
                        fdiv32(fsub32(lux, 320.0f), 40.0f));
    return 1.0f;
}

/* Inner 3836 table: [0,1]=>1 and [64,64]=>64. */
static float long_remainder_branch(float remainder)
{
    if (remainder <= 1.0f)
        return 1.0f;
    if (remainder < 64.0f)
        return lerp_win(1.0f, 64.0f,
                        fdiv32(fsub32(remainder, 1.0f), 63.0f));
    return 64.0f;
}

int e003i_aec_default_tail(const struct e003i_aec_tail_input *in,
                           struct e003i_aec_tail_output *out)
{
    float primary, remainder_branch;

    if (in == NULL || out == NULL)
        return -1;
    if (!isfinite(in->lux_index) || !isfinite(in->safe_adj_ratio) ||
        !isfinite(in->short_target) || !isfinite(in->long_target))
        return -2;
    if (!(in->safe_adj_ratio > 0.0f) || !(in->short_target > 0.0f) ||
        !(in->long_target > 0.0f))
        return -3;

    out->adrc_lux_cap = cap_from_lux(in->lux_index);
    out->adj_ratio_short = fdiv32(in->safe_adj_ratio, in->short_target);
    out->adrc_gain = short_gain_ramp(out->adj_ratio_short);
    if (out->adrc_lux_cap < out->adrc_gain)
        out->adrc_gain = out->adrc_lux_cap;
    out->short_adj_ratio = fdiv32(in->safe_adj_ratio, out->adrc_gain);

    out->drc_gain_remainder = fdiv32(8.0f, out->adrc_gain);
    out->adj_ratio_long = fdiv32(in->long_target, in->safe_adj_ratio);
    primary = long_primary(in->lux_index, out->adj_ratio_long);
    remainder_branch = long_remainder_branch(out->drc_gain_remainder);
    out->dark_boost_gain = primary < remainder_branch ? primary : remainder_branch;
    out->long_adj_ratio = fmul32(in->safe_adj_ratio, out->dark_boost_gain);
    return 0;
}
