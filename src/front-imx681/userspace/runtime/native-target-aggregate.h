// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_TARGET_AGGREGATE_H
#define E003I_NATIVE_TARGET_AGGREGATE_H
#include <stddef.h>

#define E003I_METHOD11_MAX_POINTS 11
#define E003I_METHOD11_MAX_RANGES 11

struct e003i_weighted_point {
    float value;
    float weight;
};

struct e003i_weighted_range {
    float low;
    float high;
    float weight;
};

/*
 * Exact finite-input point specialization of Windows target-component method
 * 11. Keep this helper for point-only proofs/regressions; production final
 * aggregation uses the generic low/high range form below.
 */
int e003i_method11_point_aggregate(
    const struct e003i_weighted_point *points,
    size_t count,
    float *out_value);

/* Exact generic Windows method-11 semantics for [low, high] candidates. */
int e003i_method11_range_aggregate(
    const struct e003i_weighted_range *ranges,
    size_t count,
    float *out_value);

#endif
