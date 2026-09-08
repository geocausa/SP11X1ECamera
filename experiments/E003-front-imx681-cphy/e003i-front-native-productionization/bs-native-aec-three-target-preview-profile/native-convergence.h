// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_CONVERGENCE_H
#define E003I_NATIVE_CONVERGENCE_H
#include <stdint.h>

#define E003I_CONV_LANES 7
#define E003I_TARGET_LANES 3
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
 * Ordinary SP11 front-preview current-target projection.
 *
 * BC proves activeExposureCount == 1 forces final S1..S4 to Short. The
 * convergence kernel reads current target state only for Short, Long and Safe;
 * current target S1..S4 therefore are not caller-visible in this scoped API.
 * Full F-1/F-2/F-3 history remains explicit and is not reduced here.
 */
struct e003i_front_preview_unlocked_three_target_input {
    double target_log[E003I_TARGET_LANES];
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

int e003i_converge_front_preview_unlocked_three_target(
    const struct e003i_front_preview_unlocked_three_target_input *in,
    struct e003i_conv_output *out);
#endif
