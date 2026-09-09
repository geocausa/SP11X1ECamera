// SPDX-License-Identifier: GPL-2.0-only
#include "native-bhist-bank4.h"

#include <arm_neon.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct pair_region {
    float start;
    float end;
    float low;
    float high;
};

struct boundary {
    uint32_t index;
    float fraction;
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

static float win_lerp(float lo, float hi, float t)
{
    float omt = fsub(1.0f, t);
    float p0 = fmul(lo, omt);
    float p1 = fmul(hi, t);
    return fadd(p0, p1);
}

static void interp_pair(float x, const struct pair_region *r, size_t n,
                        float *low, float *high)
{
    size_t i;

    if (x <= r[0].start) {
        *low = r[0].low;
        *high = r[0].high;
        return;
    }
    for (i = 0; i < n; ++i) {
        if (x <= r[i].end) {
            *low = r[i].low;
            *high = r[i].high;
            return;
        }
        if (i + 1 < n && x < r[i + 1].start) {
            float num = fsub(x, r[i].end);
            float den = fsub(r[i + 1].start, r[i].end);
            float t = fdivv(num, den);
            *low = win_lerp(r[i].low, r[i + 1].low, t);
            *high = win_lerp(r[i].high, r[i + 1].high, t);
            return;
        }
    }
    *low = r[n - 1].low;
    *high = r[n - 1].high;
}

static unsigned axis_width_units(uint32_t i)
{
    if (i < 128u) return 1u;
    if (i < 256u) return 2u;
    if (i < 400u) return 8u;
    if (i < 480u) return 32u;
    if (i < 576u) return 128u;
    if (i < 768u) return 256u;
    if (i < 896u) return 512u;
    return 1024u;
}

int e003i_bhist_build_value_axis(float axis[E003I_BHIST_BINS])
{
    uint32_t i;
    double center = 1.0 / 1024.0;

    if (axis == NULL)
        return -1;

    for (i = 0; i < E003I_BHIST_BINS; ++i) {
        double rounded;
        if (i != 0u) {
            unsigned prev = axis_width_units(i - 1u);
            unsigned cur = axis_width_units(i);
            if (prev == cur)
                center += (double)cur / 1024.0;
            else
                center += (double)(prev + cur) / 2048.0;
        }
        /* The retained producer axis is decimal-quantized to 5 places. */
        rounded = nearbyint(center * 100000.0) / 100000.0;
        if (rounded > 255.5)
            rounded = 255.5;
        axis[i] = (float)rounded;
    }
    return 0;
}

static void build_cdf(const uint32_t raw[E003I_BHIST_BINS],
                      uint32_t counts[E003I_BHIST_BINS],
                      float cdf[E003I_BHIST_BINS])
{
    uint32_t i;
    float running;
    float den;
    float32x4_t dv, recip;

    counts[0] = raw[0] & E003I_BHIST_RAW_MASK;
    running = (float)counts[0];
    cdf[0] = running;
    for (i = 1; i < E003I_BHIST_BINS; ++i) {
        float v;
        counts[i] = raw[i] & E003I_BHIST_RAW_MASK;
        v = (float)counts[i];
        running = fadd(running, v);
        cdf[i] = running;
    }

    den = running < 1.0f ? 1.0f : running;

    /*
     * Match 0x1803f9908..0x1803f9958 exactly: one FRECPE estimate and two
     * FRECPS/Newton refinements, then vector multiply. 1024 bins have no tail.
     */
    dv = vdupq_n_f32(den);
    recip = vrecpeq_f32(dv);
    recip = vmulq_f32(vrecpsq_f32(dv, recip), recip);
    recip = vmulq_f32(vrecpsq_f32(dv, recip), recip);
    for (i = 0; i < E003I_BHIST_BINS; i += 4u) {
        float32x4_t v = vld1q_f32(&cdf[i]);
        vst1q_f32(&cdf[i], vmulq_f32(v, recip));
    }
}

static struct boundary find_boundary(const float *domain, uint32_t begin,
                                     float target)
{
    const float eps = f32bits(UINT32_C(0x33d6bf95));
    struct boundary b = { E003I_BHIST_BINS, 1.0f };
    uint32_t i;

    for (i = begin; i < E003I_BHIST_BINS; ++i) {
        float v = domain[i];
        float delta = fsub(v, target);
        if (fabsf(delta) < eps) {
            b.index = i;
            b.fraction = 0.0f;
            return b;
        }
        if (v > target) {
            float prev = i == 0u ? 0.0f : domain[i - 1u];
            float den = fsub(v, prev);
            b.index = i;
            b.fraction = fdivv(delta, den);
            return b;
        }
    }
    return b;
}

static float clampf(float x, float lo, float hi)
{
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

static float capped_axis(float x, float cap)
{
    return cap < x ? cap : x;
}

static int history_axis_scale(const struct e003i_bhist_history_input *history,
                              float *scale)
{
    const float base = f32bits(UINT32_C(0x3f7ae148)); /* exact Windows 0.98f */
    float safe;
    float s1;
    float ratio;

    if (history == NULL || scale == NULL || history->safe_exposure == 0u ||
        history->s1_exposure == 0u || !isfinite(history->pred_gain))
        return -1;

    /* Mirror 0x1803eacd4..0x1803ead18 for ordinary BhistY source tag S1=3. */
    safe = (float)history->safe_exposure;
    s1 = (float)history->s1_exposure;
    ratio = fdivv(safe, s1);
    /* Windows intentionally permits startup PredGain=+0.0f here: the IEEE
     * division produces +inf and the following 0.98f/ratio yields +0.0f. */
    ratio = fdivv(ratio, history->pred_gain);
    *scale = ratio > 1.0f ? fdivv(base, ratio) : base;
    return 0;
}

static void histogram_range(const uint32_t counts[E003I_BHIST_BINS],
                            const float axis[E003I_BHIST_BINS],
                            const float cdf[E003I_BHIST_BINS],
                            float low, float high, int percentile_mode,
                            float axis_scale,
                            float *avg, float *cdf_mass)
{
    const float eps = f32bits(UINT32_C(0x33d6bf95));
    const float axis_cap = fmul(255.0f, axis_scale); /* captured BhistY bit depth=8 */
    const float *domain = percentile_mode ? cdf : axis;
    float lo = clampf(low, 0.0f, percentile_mode ? 1.0f : 256.0f);
    float hi = clampf(high, 0.0f, percentile_mode ? 1.0f : 256.0f);
    struct boundary lb = find_boundary(domain, 0u, lo);
    struct boundary hb = find_boundary(domain, lb.index, hi);
    uint32_t li = lb.index < E003I_BHIST_BINS ? lb.index : E003I_BHIST_BINS - 1u;
    uint32_t hi_i = hb.index < E003I_BHIST_BINS ? hb.index : E003I_BHIST_BINS - 1u;
    uint32_t end = li > hi_i ? li : hi_i;
    uint32_t i;
    float low_count = fmul((float)counts[li], lb.fraction);
    float count_mass = low_count;
    float weighted = fmul(capped_axis(axis[li], axis_cap), low_count);
    float high_include;
    float high_count;
    float den;

    for (i = li + 1u; i < end; ++i) {
        float c = (float)counts[i];
        float w = fmul(capped_axis(axis[i], axis_cap), c);
        count_mass = fadd(count_mass, c);
        weighted = fadd(weighted, w);
    }

    high_include = fsub(1.0f, hb.fraction);
    high_count = fmul((float)counts[hi_i], high_include);
    weighted = fadd(fmul(capped_axis(axis[hi_i], axis_cap), high_count), weighted);
    count_mass = fadd(high_count, count_mass);
    den = count_mass < eps ? eps : count_mass;
    *avg = fdivv(weighted, den);

    if (li == 0u) {
        *cdf_mass = cdf[hi_i];
    } else if (li == hi_i) {
        *cdf_mass = fsub(cdf[hi_i], cdf[li - 1u]);
    } else {
        *cdf_mass = fsub(cdf[hi_i], cdf[li]);
    }
}

int e003i_bhist_replay_bank4(const uint32_t raw_words[E003I_BHIST_BINS],
                             float lux_index,
                             const struct e003i_bhist_history_input *history,
                             struct e003i_bhist_bank4_output *out)
{
    static const struct pair_region sat_prev[] = {
        {   0.0f,  160.0f, 0.85f, 1.00f },
        { 180.0f,  260.0f, 0.95f, 0.99f },
        { 300.0f,  360.0f, 0.95f, 0.99f },
        { 440.0f,  480.0f, 0.96f, 0.99f },
        { 500.0f, 1000.0f, 0.98f, 1.00f },
    };
    static const struct pair_region dark_prev[] = {
        {   0.0f,  270.0f, 0.00f, 0.11f },
        { 300.0f,  360.0f, 0.00f, 0.12f },
        { 380.0f,  460.0f, 0.00f, 0.12f },
        { 480.0f, 1000.0f, 0.00f, 0.15f },
    };
    static const struct pair_region short_sat_prev[] = {
        {   0.0f,  190.0f, 0.99f, 1.00f },
        { 240.0f,  290.0f, 0.98f, 1.00f },
        { 340.0f, 1000.0f, 0.98f, 1.00f },
    };
    uint32_t counts[E003I_BHIST_BINS];
    float axis[E003I_BHIST_BINS];
    float cdf[E003I_BHIST_BINS];
    const float fixed_scale = f32bits(UINT32_C(0x3f7ae148));
    float history_scale;
    float lo, hi, ignored;

    if (raw_words == NULL || out == NULL || !isfinite(lux_index))
        return -1;
    if (history_axis_scale(history, &history_scale) != 0)
        return -1;
    if (e003i_bhist_build_value_axis(axis) != 0)
        return -1;

    build_cdf(raw_words, counts, cdf);
    memset(out, 0, sizeof(*out));

    histogram_range(counts, axis, cdf, 255.0f, 256.0f, 0, history_scale,
                    &ignored, &out->saturate_stats_ratio);

    interp_pair(lux_index, sat_prev, sizeof(sat_prev) / sizeof(sat_prev[0]), &lo, &hi);
    histogram_range(counts, axis, cdf, lo, hi, 1, history_scale,
                    &out->sat_prev_high_pctl_luma, &ignored);

    interp_pair(lux_index, dark_prev, sizeof(dark_prev) / sizeof(dark_prev[0]), &lo, &hi);
    histogram_range(counts, axis, cdf, lo, hi, 1, history_scale,
                    &out->dark_prev_low_pctl_luma, &ignored);

    interp_pair(lux_index, short_sat_prev,
                sizeof(short_sat_prev) / sizeof(short_sat_prev[0]), &lo, &hi);
    histogram_range(counts, axis, cdf, lo, hi, 1, fixed_scale,
                    &out->short_sat_prev_high_pctl_luma, &ignored);

    return 0;
}
