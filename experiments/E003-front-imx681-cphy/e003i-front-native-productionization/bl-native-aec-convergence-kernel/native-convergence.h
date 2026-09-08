// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_CONVERGENCE_H
#define E003I_NATIVE_CONVERGENCE_H
#include <stdint.h>

#define E003I_CONV_LANES 7
#define E003I_CONV_MAX_STRETCH 16
#define E003I_LANE_SHORT 0
#define E003I_LANE_LONG  1
#define E003I_LANE_SAFE  2
#define E003I_LANE_S1    3

struct e003i_conv_history {
    uint64_t lanes[E003I_CONV_LANES];
    float drc_gain;
    float previous_delta;
};

struct e003i_stretch_record {
    float weight;
    float offset;
    float comp;
    float temp_weight;
    uint32_t negative;
};

struct e003i_conv_input {
    double target_log[E003I_CONV_LANES];
    struct e003i_conv_history history1;
    struct e003i_conv_history history2;
    struct e003i_conv_history delayed_history;

    uint32_t pipeline_delay;
    float base_speed;
    float base_capping;
    float drc_speed;
    int32_t capping_type;
    int32_t tolerance_steps;
    float minimum_step;
    uint32_t intolerance_gate;
    uint32_t small_delta_exemption;

    struct e003i_stretch_record stretch[E003I_CONV_MAX_STRETCH];
    uint32_t stretch_capacity;
    uint32_t stretch_active_count;
    uint32_t stretch_agg_type;
    uint32_t stretch_direction_mode;
    uint32_t stretch_target_negative;

    int32_t state_flag_short;
    int32_t state_flag_long;
    int32_t drc_policy;
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

/* stretch_type 0 converts a positive factor into log1.03; other types are offsets. */
int e003i_stretch_materialize(int stretch_type, float weight, float factor_or_offset,
                              float comp, float temp_weight,
                              struct e003i_stretch_record *out);

int e003i_converge_single_request(const struct e003i_conv_input *in,
                                  struct e003i_conv_output *out);
#endif
