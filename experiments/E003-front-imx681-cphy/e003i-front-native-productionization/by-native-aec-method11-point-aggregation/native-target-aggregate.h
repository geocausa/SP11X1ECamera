// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_TARGET_AGGREGATE_H
#define E003I_NATIVE_TARGET_AGGREGATE_H
#include <stddef.h>

#define E003I_METHOD11_MAX_POINTS 11

struct e003i_weighted_point {
    float value;
    float weight;
};

/*
 * Exact finite-input point specialization of the Windows target-component
 * aggregation method 11. Arithmetic SceneAnalyzer publications duplicate a
 * scalar as [value,value], so callers need only provide the scalar and weight.
 */
int e003i_method11_point_aggregate(
    const struct e003i_weighted_point *points,
    size_t count,
    float *out_value);

#endif
