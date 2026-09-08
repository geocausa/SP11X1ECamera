// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_CONVERGENCE_H
#define E003I_NATIVE_CONVERGENCE_H
#include <stdint.h>

#define E003I_CONV_LANES 7
#define E003I_LANE_SHORT 0
#define E003I_LANE_LONG  1
#define E003I_LANE_SAFE  2
#define E003I_LANE_S1    3

struct e003i_conv_history {
    uint64_t lanes[E003I_CONV_LANES];
    float drc_gain;
    float previous_delta;
};

/*
 * Normal SP11 front-preview request state only.
 *
 * Ordinary SP11 front preview, normal streaming, AEC unlocked and temporary
 * metering-lock context inactive. BM/BN/BO fix tuning; BQ proves the four
 * residual convergence runtime scalars are all zero in this scoped profile.
 * Only request target/history state remains public.
 */
struct e003i_front_preview_unlocked_input {
    double target_log[E003I_CONV_LANES];
    struct e003i_conv_history history1;
    struct e003i_conv_history history2;
    struct e003i_conv_history delayed_history;
};

struct e003i_conv_output {
    double basic_safe_log;
    double post_stretch_log[E003I_CONV_LANES];
    double final_log[E003I_CONV_LANES];
    uint64_t linear[E003I_CONV_LANES];
    float pred_gain;
    float short_stretch;
    float safe_stretch;
    float stretch_ratio;
    float drc_ratio;
    uint32_t basic_direction_ok;
    uint32_t drc_branch;
};

int e003i_converge_front_preview_unlocked(
    const struct e003i_front_preview_unlocked_input *in,
    struct e003i_conv_output *out);
#endif
