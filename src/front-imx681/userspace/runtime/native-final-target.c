// SPDX-License-Identifier: GPL-2.0-only
#include "native-final-target.h"
#include "native-target-aggregate.h"
#include <math.h>
#include <stdint.h>
#include <string.h>

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

static int candidate_finite(const struct e003i_aec_candidate *c)
{
    return isfinite(c->low) && isfinite(c->high) &&
           c->low <= c->high && isfinite(c->confidence);
}

int e003i_aec_default_final_targets(const struct e003i_final_target_input *in,
                                    struct e003i_final_target_output *out)
{
    const struct e003i_aec_candidate *safe_src[E003I_SAFE_ACTIVE_CANDIDATES];
    struct e003i_weighted_range safe[E003I_SAFE_ACTIVE_CANDIDATES];
    struct e003i_weighted_range short_ranges[2];
    struct e003i_weighted_range long_ranges[2];
    struct e003i_aec_tail_input tail_in;
    const float shared_safe_weight = f32bits(UINT32_C(0x3a83126f));
    size_t i;
    int rc;

    if (in == NULL || out == NULL)
        return -1;
    if (!isfinite(in->lux_index))
        return -2;

    safe_src[0] = &in->frame;
    safe_src[1] = &in->sat_prev;
    safe_src[2] = &in->dark_prev;
    safe_src[3] = &in->brighten;
    safe_src[4] = &in->extreme_color;
    safe_src[5] = &in->illuminance;
    for (i = 0; i < E003I_SAFE_ACTIVE_CANDIDATES; ++i) {
        if (!candidate_finite(safe_src[i]))
            return -3;
        safe[i].low = safe_src[i]->low;
        safe[i].high = safe_src[i]->high;
        safe[i].weight = safe_src[i]->confidence;
    }
    if (!candidate_finite(&in->short_sat_prev) ||
        !candidate_finite(&in->long_dark_prev))
        return -3;

    rc = e003i_method11_range_aggregate(safe, E003I_SAFE_ACTIVE_CANDIDATES,
                                        &out->safe_target);
    if (rc != 0)
        return -10;
    if (!(out->safe_target > 0.0f) || !isfinite(out->safe_target))
        return -11;
    out->safe_adj_ratio = out->safe_target;

    short_ranges[0].low = short_ranges[0].high = out->safe_adj_ratio;
    short_ranges[0].weight = shared_safe_weight;
    short_ranges[1].low = in->short_sat_prev.low;
    short_ranges[1].high = in->short_sat_prev.high;
    short_ranges[1].weight = in->short_sat_prev.confidence;
    rc = e003i_method11_range_aggregate(short_ranges, 2, &out->short_target);
    if (rc != 0 || !(out->short_target > 0.0f) || !isfinite(out->short_target))
        return -12;

    long_ranges[0].low = long_ranges[0].high = out->safe_adj_ratio;
    long_ranges[0].weight = shared_safe_weight;
    long_ranges[1].low = in->long_dark_prev.low;
    long_ranges[1].high = in->long_dark_prev.high;
    long_ranges[1].weight = in->long_dark_prev.confidence;
    rc = e003i_method11_range_aggregate(long_ranges, 2, &out->long_target);
    if (rc != 0 || !(out->long_target > 0.0f) || !isfinite(out->long_target))
        return -13;

    tail_in.lux_index = in->lux_index;
    tail_in.safe_adj_ratio = out->safe_adj_ratio;
    tail_in.short_target = out->short_target;
    tail_in.long_target = out->long_target;
    rc = e003i_aec_default_tail(&tail_in, &out->tail);
    if (rc != 0)
        return -14;
    return 0;
}
