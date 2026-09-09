// SPDX-License-Identifier: GPL-2.0-only
#include "native-raw-aec-loop.h"

#include <math.h>
#include <string.h>

#include "native-aec-state.h"

int e003i_raw_request_loop_process(struct e003i_request_loop_state *state,
                                   const struct e003i_raw_request_input *in,
                                   struct e003i_raw_request_output *out)
{
    struct e003i_stats3a_view stats;
    struct e003i_request_history_entry delayed;
    struct e003i_bhist_history_input bhist_history;
    struct e003i_effective_analyzer_input analyzer_in;
    struct e003i_request_loop_input request_in;
    uint64_t expected_generation;
    float frame_target;
    int rc;

    if (state == NULL || in == NULL || out == NULL || in->stats3a == NULL)
        return -1;
    memset(out, 0, sizeof(*out));

    if (in->frame_id != state->next_frame_id)
        return -2;
    if (in->frame_id >= UINT32_MAX)
        return -3;

    rc = e003i_stats3a_open(in->stats3a, in->stats3a_bytes, &stats);
    if (rc != 0)
        return -10 + rc;

    /* Cold-owned producer generations and source sequence numbers begin at 1. */
    expected_generation = in->frame_id + 1u;
    if (stats.generation != expected_generation ||
        stats.source_seq != (uint32_t)expected_generation)
        return -14;

    rc = e003i_request_loop_get_history_offset(state, in->frame_id, 3,
                                                &delayed);
    if (rc != 0)
        return -15;

    out->stats_generation = stats.generation;
    out->stats_source_seq = stats.source_seq;
    out->stats_slot = stats.slot;

    rc = e003i_aecbe_frame_luma(stats.aec_raw, &out->measured_luma);
    if (rc != 0)
        return -20 + rc;

    bhist_history.safe_exposure = delayed.safe_exposure;
    bhist_history.s1_exposure = delayed.s1_exposure;
    bhist_history.pred_gain = delayed.pred_gain;
    rc = e003i_bhist_replay_bank4(stats.bhist_raw, state->lux_trigger,
                                  &bhist_history, &out->bank4);
    if (rc != 0)
        return -30 + rc;

    frame_target = e003i_framesa_target_low(state->lux_trigger);
    if (!isfinite(frame_target) || !(frame_target > 0.0f))
        return -40;

    memset(&analyzer_in, 0, sizeof(analyzer_in));
    analyzer_in.lux_index = state->lux_trigger;
    analyzer_in.frame_luma = out->measured_luma;
    analyzer_in.frame_target = frame_target;
    analyzer_in.delayed_short_exposure = delayed.short_exposure;
    analyzer_in.saturate_stats_ratio = out->bank4.saturate_stats_ratio;
    analyzer_in.sat_prev_high_pctl_luma = out->bank4.sat_prev_high_pctl_luma;
    analyzer_in.dark_prev_low_pctl_luma = out->bank4.dark_prev_low_pctl_luma;
    analyzer_in.short_sat_prev_high_pctl_luma =
        out->bank4.short_sat_prev_high_pctl_luma;
    rc = e003i_aec_default_effective_analyzers(&analyzer_in,
                                                &out->effective_target);
    if (rc != 0)
        return -50 + rc;

    memset(&request_in, 0, sizeof(request_in));
    request_in.frame_id = in->frame_id;
    request_in.measured_luma = out->measured_luma;
    request_in.analyzers.sat_prev = out->effective_target.sat_prev;
    request_in.analyzers.dark_prev = out->effective_target.dark_prev;
    request_in.analyzers.brighten = out->effective_target.brighten;
    request_in.analyzers.extreme_color = out->effective_target.extreme_color;
    request_in.analyzers.illuminance = out->effective_target.illuminance;
    request_in.analyzers.short_sat_prev = out->effective_target.short_sat_prev;
    request_in.analyzers.long_dark_prev = out->effective_target.long_dark_prev;

    rc = e003i_request_loop_process(state, &request_in, &out->request);
    if (rc != 0)
        return -100 + rc;
    return 0;
}
