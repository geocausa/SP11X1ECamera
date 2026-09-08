// SPDX-License-Identifier: GPL-2.0-only
#include "native-t681.h"
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct knee {
    uint32_t priority;
    float gain;
    uint64_t time;
};

static const struct knee k681[] = {
    { 1, 1.0f, 37516ULL },
    { 1, 67.0f, 33333333ULL },
    { 1, 67.0f, 66666666ULL },
    { 0, 92.0f, 66666666ULL },
};

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

__attribute__((noinline)) static float fdiv32(float a, float b)
{
    volatile float r = a / b;
    return r;
}
__attribute__((noinline)) static float fmul32(float a, float b)
{
    volatile float r = a * b;
    return r;
}

static uint64_t trunc_double_u64(double x)
{
    return (uint64_t)x;
}

static uint64_t trunc_float_u64(float x)
{
    return (uint64_t)x;
}

static uint64_t product_trunc(float gain, uint64_t time, float correction)
{
    volatile double p = (double)gain * (double)time;
    volatile double q = p * (double)correction;
    return trunc_double_u64(q);
}

static uint64_t product_frinta(float gain, uint64_t time, float correction)
{
    volatile double p = (double)gain * (double)time;
    volatile double q = p * (double)correction;
    /* Positive finite FRINTA: nearest integral, halfway away from zero. */
    return (uint64_t)floor(q + 0.5);
}

int e003i_t681_preview_arbitrate(uint64_t target,
                                struct e003i_t681_result *out)
{
    const float one_next = f32bits(UINT32_C(0x3f800001));
    const float fit_warn_eps = f32bits(UINT32_C(0x33d6bf95));
    const float min_gain = 1.0f;
    const float max_gain = 92.0f;
    const uint64_t min_time = 37516ULL;
    const uint64_t max_time = 33333332ULL;
    const float correction = 1.0f;
    uint64_t products[4];
    uint32_t upper;
    float gain;
    uint64_t time;
    uint64_t desired;
    double exact_gain_eps;
    unsigned i;

    if (out == NULL)
        return -1;

    /* Exact GAIN_EPS bytes: 00 00 00 e0 e2 36 1a 3f. */
    {
        const unsigned char b[8] = {0x00,0x00,0x00,0xe0,0xe2,0x36,0x1a,0x3f};
        memcpy(&exact_gain_eps, b, sizeof(exact_gain_eps));
    }

    for (i = 0; i < 4; ++i)
        products[i] = product_trunc(k681[i].gain, k681[i].time, correction);
    if (target < products[0] || target > products[3])
        return -2;

    upper = 1;
    while (upper < 4 && target > products[upper])
        ++upper;
    if (upper >= 4)
        upper = 3;

    gain = k681[upper - 1].gain;
    time = k681[upper - 1].time;
    {
        float ratio = fdiv32((float)target, (float)products[upper - 1]);
        if (one_next < ratio) {
            if (k681[upper].priority == 0) {
                float gr = fdiv32(k681[upper].gain, k681[upper - 1].gain);
                float leftover, used;
                if (ratio <= gr) {
                    leftover = 1.0f;
                    used = ratio;
                } else {
                    leftover = fdiv32(ratio, gr);
                    used = gr;
                }
                gain = fmul32(used, k681[upper - 1].gain);
                if (one_next < leftover) {
                    float tr = fdiv32((float)k681[upper].time,
                                      (float)k681[upper - 1].time);
                    float used_t = leftover <= tr ? leftover : tr;
                    time = trunc_float_u64(
                        fmul32(used_t, (float)k681[upper - 1].time));
                }
            } else {
                float tr = fdiv32((float)k681[upper].time,
                                  (float)k681[upper - 1].time);
                float leftover, used;
                if (ratio <= tr) {
                    leftover = 1.0f;
                    used = ratio;
                } else {
                    leftover = fdiv32(ratio, tr);
                    used = tr;
                }
                time = trunc_float_u64(
                    fmul32(used, (float)k681[upper - 1].time));
                if (1.0f < leftover) {
                    float gr = fdiv32(k681[upper].gain,
                                      k681[upper - 1].gain);
                    float used_g = leftover <= gr ? leftover : gr;
                    gain = fmul32(used_g, k681[upper - 1].gain);
                }
            }
        }
    }

    desired = product_trunc(gain, time, correction);

    /* UtilMakeTableExposureFit, pinned positive normal-preview path. */
    {
        float old_gain = gain;
        if (min_gain <= old_gain) {
            if (max_gain < old_gain) {
                gain = max_gain;
                if ((double)max_gain + exact_gain_eps <= (double)old_gain) {
                    time = trunc_double_u64(
                        ((double)desired / (double)max_gain) /
                        (double)correction);
                    if (max_time < time && time <= max_time + 1)
                        time = max_time;
                }
            }
        } else {
            gain = min_gain;
            if ((double)old_gain <= (double)min_gain - exact_gain_eps) {
                time = trunc_double_u64(
                    ((double)desired / (double)min_gain) /
                    (double)correction);
                if (time < min_time && min_time - 1 <= time)
                    time = min_time;
            }
        }

        if (time < min_time) {
            uint64_t old_time = time;
            time = min_time;
            if (!(min_time - 1 <= old_time)) {
                gain = (float)(((double)desired / (double)min_time) /
                               (double)correction);
                if (!(min_gain <= gain ||
                      (double)gain < (double)min_gain - exact_gain_eps))
                    gain = min_gain;
            }
        } else if (time > max_time) {
            uint64_t old_time = time;
            time = max_time;
            if (!(old_time <= max_time + 1)) {
                gain = (float)(((double)desired / (double)max_time) /
                               (double)correction);
                if (!(gain <= max_gain ||
                      (double)max_gain + exact_gain_eps < (double)gain))
                    gain = max_gain;
            }
        }
    }

    if (time < min_time || time > max_time ||
        gain < (float)(min_gain - fit_warn_eps) || !isfinite(gain))
        return -3;

    out->gain = gain;
    out->exposure_time_ns = time;
    out->correction = correction;
    out->retained_exposure = product_frinta(gain, time, correction);
    out->upper_knee = upper;
    return 0;
}
