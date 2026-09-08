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
 * The Windows tuning/profile constants are intentionally absent from this
 * public input. BP injects the mechanically proven BM/BN/BO profile inside
 * e003i_converge_front_preview(). The remaining flags are runtime state, not
 * tuning selection, and stay explicit until their producer semantics close.
 */
struct e003i_front_preview_conv_input {
    double target_log[E003I_CONV_LANES];
    struct e003i_conv_history history1;
    struct e003i_conv_history history2;
    struct e003i_conv_history delayed_history;
    uint32_t intolerance_gate;
    uint32_t small_delta_exemption;
    int32_t state_flag_short;
    int32_t state_flag_long;
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

int e003i_converge_front_preview(const struct e003i_front_preview_conv_input *in,
                                 struct e003i_conv_output *out);
#endif
