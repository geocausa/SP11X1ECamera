// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_CONVERGENCE_QWORD_H
#define E003I_NATIVE_CONVERGENCE_QWORD_H
#include <stdint.h>

#define E003I_CONV_LANES 7
#define E003I_TARGET_LANES 3
#define E003I_LANE_SHORT 0
#define E003I_LANE_LONG  1
#define E003I_LANE_SAFE  2
#define E003I_LANE_S1    3

struct e003i_history_f1 {
    uint64_t short_exposure;
    uint64_t long_exposure;
    uint64_t safe_exposure;
    float drc_gain;
};

struct e003i_history_f2 {
    uint64_t short_exposure;
    uint64_t long_exposure;
    uint64_t safe_exposure;
    float drc_gain;
};

struct e003i_history_f3 {
    uint64_t safe_exposure;
};

/*
 * Ordinary SP11 front-preview qword convergence request state.
 * Current Short/Long/Safe targets stay in the Windows linear qword domain at
 * the public boundary and are converted internally with Windows float32 order.
 *
 * BS reduces current target state to Short/Long/Safe and BT minimizes the
 * temporal snapshots. BU additionally removes F-1 previous_delta because the
 * pinned Windows normal-preview recurrence proves it remains +0.0f forever.
 */
struct e003i_front_preview_unlocked_qword_history_input {
    uint64_t target_exposure[E003I_TARGET_LANES];
    struct e003i_history_f1 history1;
    struct e003i_history_f2 history2;
    struct e003i_history_f3 delayed_history;
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

/* Exact Windows absolute log1.03 input coordinate for a positive qword exposure. */
float e003i_convergence_log103_u64(uint64_t exposure);

int e003i_converge_front_preview_unlocked_qword_history(
    const struct e003i_front_preview_unlocked_qword_history_input *in,
    struct e003i_conv_output *out);
#endif
