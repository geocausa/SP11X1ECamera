// SPDX-License-Identifier: GPL-2.0-only
#include "native-effective-analyzers.h"

#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct scalar_region {
    float start;
    float end;
    float value;
};

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

static float fdivv(float a, float b)
{
    volatile float r = a / b;
    return r;
}

/* Windows TwoFloats/OneFloat blend order: lo*(1-t) + hi*t. */
static float win_lerp(float lo, float hi, float t)
{
    float omt = fsub(1.0f, t);
    float p0 = fmul(lo, omt);
    float p1 = fmul(hi, t);
    return fadd(p0, p1);
}

static float interp_regions(float x, const struct scalar_region *r, size_t n)
{
    size_t i;

    if (x <= r[0].start)
        return r[0].value;
    for (i = 0; i < n; ++i) {
        if (x <= r[i].end)
            return r[i].value;
        if (i + 1 < n && x < r[i + 1].start) {
            float num = fsub(x, r[i].end);
            float den = fsub(r[i + 1].start, r[i].end);
            float t = fdivv(num, den);
            return win_lerp(r[i].value, r[i + 1].value, t);
        }
    }
    return r[n - 1].value;
}

static float sat_target_high(float lux)
{
    static const struct scalar_region r[] = {
        { 0.0f, 160.0f, 220.0f },
        { 180.0f, 260.0f, 210.0f },
        { 300.0f, 360.0f, 200.0f },
        { 440.0f, 480.0f, 140.0f },
        { 500.0f, 1000.0f, 90.0f },
    };
    return interp_regions(lux, r, sizeof(r) / sizeof(r[0]));
}

static float sat_confidence(float lux)
{
    static const struct scalar_region r[] = {
        { 0.0f, 160.0f, 0.5f },
        { 180.0f, 260.0f, 0.5f },
        { 300.0f, 360.0f, 0.5f },
        { 440.0f, 480.0f, 0.3f },
        { 500.0f, 1000.0f, 0.1f },
    };
    return interp_regions(lux, r, sizeof(r) / sizeof(r[0]));
}

static float sat_inner(float ratio, float floorv)
{
    struct scalar_region r[2] = {
        { 0.0f, floorv, floorv },
        { 256.0f, 256.0f, 256.0f },
    };
    return interp_regions(ratio, r, 2);
}

static float sat_method2(float lux, float ratio)
{
    struct scalar_region r[5];
    r[0] = (struct scalar_region){ 0.0f, 160.0f, sat_inner(ratio, f32bits(UINT32_C(0x3f4ccccd))) };
    r[1] = (struct scalar_region){ 180.0f, 260.0f, sat_inner(ratio, f32bits(UINT32_C(0x3f266666))) };
    r[2] = (struct scalar_region){ 300.0f, 360.0f, sat_inner(ratio, f32bits(UINT32_C(0x3f19999a))) };
    r[3] = (struct scalar_region){ 440.0f, 480.0f, sat_inner(ratio, f32bits(UINT32_C(0x3f0ccccd))) };
    r[4] = (struct scalar_region){ 500.0f, 1000.0f, sat_inner(ratio, f32bits(UINT32_C(0x3ee66666))) };
    return interp_regions(lux, r, 5);
}

static float dark_luma(float raw)
{
    static const struct scalar_region r[] = {
        { 0.0f, 0.25f, 0.25f },
        { 255.0f, 255.0f, 255.0f },
    };
    return interp_regions(raw, r, 2);
}

static float dark_target_high(float lux)
{
    static const struct scalar_region r[] = {
        { 0.0f, 270.0f, 256.0f },
        { 300.0f, 360.0f, 256.0f },
        { 380.0f, 460.0f, 256.0f },
        { 480.0f, 1000.0f, 256.0f },
    };
    return interp_regions(lux, r, 4);
}

static float dark_confidence(float lux)
{
    static const struct scalar_region r[] = {
        { 0.0f, 270.0f, 0.2f },
        { 300.0f, 360.0f, 0.15f },
        { 380.0f, 460.0f, 0.18f },
        { 480.0f, 1000.0f, 0.2f },
    };
    return interp_regions(lux, r, 4);
}

static float identity_0_256(float x)
{
    static const struct scalar_region r[] = {
        { 0.0f, 0.0f, 0.0f },
        { 256.0f, 256.0f, 256.0f },
    };
    return interp_regions(x, r, 2);
}

static float dark_method2(float lux, float ratio)
{
    float v = identity_0_256(ratio);
    struct scalar_region r[] = {
        { 0.0f, 270.0f, v },
        { 300.0f, 360.0f, v },
        { 380.0f, 460.0f, v },
        { 480.0f, 1000.0f, v },
    };
    return interp_regions(lux, r, 4);
}

static float short_target_high(float lux)
{
    static const struct scalar_region r[] = {
        { 0.0f, 190.0f, 165.0f },
        { 240.0f, 290.0f, 175.0f },
        { 340.0f, 1000.0f, 190.0f },
    };
    return interp_regions(lux, r, 3);
}

static float short_confidence(float lux)
{
    static const struct scalar_region r[] = {
        { 0.0f, 190.0f, 1.0f },
        { 240.0f, 290.0f, 1.0f },
        { 340.0f, 1000.0f, 1.0f },
    };
    return interp_regions(lux, r, 3);
}

static float short_method2(float lux, float ratio)
{
    float v = identity_0_256(ratio);
    struct scalar_region r[] = {
        { 0.0f, 190.0f, v },
        { 240.0f, 290.0f, v },
        { 340.0f, 1000.0f, v },
    };
    return interp_regions(lux, r, 3);
}

static float illuminance_conf_a(float frame_adj)
{
    static const struct scalar_region r[] = {
        { 0.0f, 0.5f, 2.0f },
        { 0.5f, 100.0f, 0.0f },
    };
    return interp_regions(frame_adj, r, 2);
}

static float illuminance_conf_b(float sat_ratio)
{
    static const struct scalar_region r[] = {
        { 0.0f, 0.5f, 0.0f },
        { 0.8f, 1.0f, 5.0f },
    };
    return interp_regions(sat_ratio, r, 2);
}

static float illuminance_correction(float ratio)
{
    static const struct scalar_region r[] = {
        { 0.0f, 0.25f, 1.4f },
        { 0.5f, 1.0f, 1.2f },
    };
    return interp_regions(ratio, r, 2);
}

static int valid_input(const struct e003i_effective_analyzer_input *in)
{
    if (in == NULL)
        return 0;
    if (!isfinite(in->lux_index) || !isfinite(in->frame_luma) ||
        !isfinite(in->frame_target) || !isfinite(in->saturate_stats_ratio) ||
        !isfinite(in->sat_prev_high_pctl_luma) ||
        !isfinite(in->dark_prev_low_pctl_luma) ||
        !isfinite(in->short_sat_prev_high_pctl_luma))
        return 0;
    if (!(in->frame_luma > 0.0f) || !(in->frame_target > 0.0f) ||
        !(in->sat_prev_high_pctl_luma > 0.0f) ||
        !(in->dark_prev_low_pctl_luma > 0.0f) ||
        !(in->short_sat_prev_high_pctl_luma > 0.0f) ||
        in->delayed_short_exposure == 0)
        return 0;
    return 1;
}

int e003i_aec_default_effective_analyzers(
    const struct e003i_effective_analyzer_input *in,
    struct e003i_final_target_input *out)
{
    float frame_adj, t, l, ratio, mapped;
    float short_f, illuminance_luma, illuminance_ratio, corr;
    const float frame_conf = f32bits(UINT32_C(0x3a83126f));
    const float illuminance_factor = f32bits(UINT32_C(0x3d0eb463));

    if (!valid_input(in) || out == NULL)
        return -1;

    memset(out, 0, sizeof(*out));
    out->lux_index = in->lux_index;

    frame_adj = fdivv(in->frame_target, in->frame_luma);
    if (!(frame_adj > 0.0f) || !isfinite(frame_adj))
        return -2;
    out->frame.value = frame_adj;
    out->frame.confidence = frame_conf;

    /* SatPrevSA: high target selector -> normalized ratio -> method2 -> denormalize. */
    t = sat_target_high(in->lux_index);
    l = in->sat_prev_high_pctl_luma;
    ratio = fdivv(fmul(t, in->frame_luma), fmul(l, in->frame_target));
    mapped = sat_method2(in->lux_index, ratio);
    out->sat_prev.value = fdivv(fmul(mapped, in->frame_target), in->frame_luma);
    out->sat_prev.confidence = sat_confidence(in->lux_index);

    /* DarkPrevSA phase-2 AdjRatioEnd (the final data24 publication). */
    t = dark_target_high(in->lux_index);
    l = dark_luma(in->dark_prev_low_pctl_luma);
    ratio = fdivv(fmul(t, in->frame_luma), fmul(l, in->frame_target));
    mapped = dark_method2(in->lux_index, ratio);
    out->dark_prev.value = fdivv(fmul(mapped, in->frame_target), in->frame_luma);
    out->dark_prev.confidence = dark_confidence(in->lux_index);

    /* Proven exact-zero confidence candidates are CE-equivalent canonical zeros. */
    out->brighten.value = 0.0f;
    out->brighten.confidence = 0.0f;
    out->extreme_color.value = 0.0f;
    out->extreme_color.confidence = 0.0f;

    /*
     * IlluminanceSA.  Ordinary trigger 9:63 is exact +0.0f; method2 ref6480
     * therefore selects its first duplicated leaf, 0x3d0eb463.  9:28 is the
     * delayed retained-history Short qword converted uint64 -> float32.
     */
    short_f = (float)in->delayed_short_exposure;
    illuminance_luma = fdivv(fmul(short_f, illuminance_factor), 1000000.0f);
    illuminance_ratio = fdivv(in->frame_target,
                              fmul(illuminance_luma, frame_adj));
    corr = illuminance_correction(illuminance_ratio);
    out->illuminance.value = fmul(fmul(illuminance_ratio, corr), frame_adj);
    out->illuminance.confidence = fminf(illuminance_conf_a(frame_adj),
                                        illuminance_conf_b(in->saturate_stats_ratio));

    /* ShortSatPrevSA phase-2 final data59 publication. */
    t = short_target_high(in->lux_index);
    l = in->short_sat_prev_high_pctl_luma;
    ratio = fdivv(fmul(t, in->frame_luma), fmul(l, in->frame_target));
    mapped = short_method2(in->lux_index, ratio);
    out->short_sat_prev.value = fdivv(fmul(mapped, in->frame_target),
                                      in->frame_luma);
    out->short_sat_prev.confidence = short_confidence(in->lux_index);

    out->long_dark_prev.value = 0.0f;
    out->long_dark_prev.confidence = 0.0f;

    if (!isfinite(out->sat_prev.value) || !isfinite(out->sat_prev.confidence) ||
        !isfinite(out->dark_prev.value) || !isfinite(out->dark_prev.confidence) ||
        !isfinite(out->illuminance.value) || !isfinite(out->illuminance.confidence) ||
        !isfinite(out->short_sat_prev.value) ||
        !isfinite(out->short_sat_prev.confidence))
        return -3;
    return 0;
}
