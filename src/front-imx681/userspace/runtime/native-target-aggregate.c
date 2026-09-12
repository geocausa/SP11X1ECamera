// SPDX-License-Identifier: GPL-2.0-only
#include "native-target-aggregate.h"
#include <math.h>
#include <stdint.h>

static float bits_to_float(uint32_t bits)
{
    union { uint32_t u; float f; } v = { .u = bits };
    return v.f;
}

static void sort_float_ascending(float *v, size_t n)
{
    size_t i;
    for (i = 1; i < n; ++i) {
        float x = v[i];
        size_t j = i;
        while (j > 0 && x < v[j - 1]) {
            v[j] = v[j - 1];
            --j;
        }
        v[j] = x;
    }
}

int e003i_method11_point_aggregate(
    const struct e003i_weighted_point *points,
    size_t count,
    float *out_value)
{
    const float epsilon = bits_to_float(UINT32_C(0x33d6bf95));
    float boundaries[2 * E003I_METHOD11_MAX_POINTS + 2];
    float best_value = -1.0f;
    float best_metric = 100000.0f;
    size_t nb = 0, i, k;

    if (points == NULL || out_value == NULL)
        return -1;
    if (count > E003I_METHOD11_MAX_POINTS)
        return -2;
    for (i = 0; i < count; ++i) {
        if (!isfinite(points[i].value) || !isfinite(points[i].weight))
            return -3;
        if (points[i].weight > 0.0f) {
            boundaries[nb++] = points[i].value;
            boundaries[nb++] = points[i].value;
        }
    }

    boundaries[nb++] = 0.0f;
    boundaries[nb++] = 256.0f;
    sort_float_ascending(boundaries, nb);

    for (k = 0; k + 1 < nb; ++k) {
        const float lower = boundaries[k];
        const float upper = boundaries[k + 1];
        float sum_weight = 0.0f;
        float sum_weighted = 0.0f;
        float avg, candidate, metric;

        if (fabsf(lower - upper) < epsilon)
            continue;

        for (i = 0; i < count; ++i) {
            const float weight = points[i].weight;
            const float value = points[i].value;
            if (fabsf(weight) < epsilon)
                continue;
            if (upper <= value) {
                volatile float product = weight * value;
                sum_weight = sum_weight + weight;
                sum_weighted = sum_weighted + product;
            }
            if (lower >= value) {
                volatile float product = weight * value;
                sum_weight = sum_weight + weight;
                sum_weighted = sum_weighted + product;
            }
        }

        avg = sum_weighted / sum_weight;
        candidate = avg;
        if (candidate < lower)
            candidate = lower;
        if (upper < candidate)
            candidate = upper;
        {
            volatile float product = candidate * sum_weight;
            metric = fabsf(product - sum_weighted);
        }
        if (metric < best_metric) {
            best_value = candidate;
            best_metric = metric;
        }
    }

    *out_value = best_value;
    return 0;
}
