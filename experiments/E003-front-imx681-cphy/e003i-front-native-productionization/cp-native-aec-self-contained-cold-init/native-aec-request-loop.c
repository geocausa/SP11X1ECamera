// SPDX-License-Identifier: GPL-2.0-only
#include "native-aec-request-loop.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

/* Separately verified BK/BJ primitives. */
float e003i_framesa_target_low(float lux_trigger);
float e003i_algorithm001_lux(float measured_luma,
                             float history_reference_log103,
                             float previous_lux,
                             float alpha);
float e003i_log103_coordinate(uint64_t exposure);

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

__attribute__((noinline)) static float fdiv32(float a, float b)
{
    volatile float r = a / b;
    return r;
}

int e003i_request_loop_init(struct e003i_request_loop_state *state)
{
    struct e003i_request_history_entry *start;
    if (state == NULL)
        return -1;
    memset(state, 0, sizeof(*state));
    /* CP: exact ordinary cold-preview Windows initialization. */
    state->lux_trigger = f32bits(E003I_WINDOWS_INITIAL_LUX_BITS);
    state->algorithm001_alpha = f32bits(E003I_WINDOWS_ALGORITHM001_ALPHA_BITS);
    state->next_frame_id = 0;

    /* CN: exact ordinary Windows synthetic start-history exposure record. */
    start = &state->start_history;
    start->frame_id = 0;
    start->short_exposure = E003I_WINDOWS_START_EXPOSURE;
    start->long_exposure = E003I_WINDOWS_START_EXPOSURE;
    start->safe_exposure = E003I_WINDOWS_START_EXPOSURE;
    start->s1_exposure = E003I_WINDOWS_START_EXPOSURE;
    /* Windows start record's DRC state is the identity/zero case. */
    start->pred_gain = 0.0f;
    start->valid = 1;
    return 0;
}

static struct e003i_request_history_entry *history_slot(
    struct e003i_request_loop_state *state, uint64_t frame_id)
{
    return &state->history[frame_id % E003I_REQUEST_HISTORY_SLOTS];
}

static const struct e003i_request_history_entry *history_exact(
    const struct e003i_request_loop_state *state, uint64_t frame_id)
{
    const struct e003i_request_history_entry *e =
        &state->history[frame_id % E003I_REQUEST_HISTORY_SLOTS];
    return e->valid && e->frame_id == frame_id ? e : NULL;
}

/*
 * CN / GetInternalFrameHistory ordinary rule.  Begin with the synthetic start
 * record.  Walk real history newest -> oldest, selecting each visited record;
 * stop at the first whose saved frame is old enough for the requested offset.
 * If none is old enough, the oldest available real record remains selected.
 * Windows retains ten ordinary real records.
 */
static const struct e003i_request_history_entry *history_get_offset(
    const struct e003i_request_loop_state *state,
    uint64_t current_frame,
    unsigned offset)
{
    const struct e003i_request_history_entry *selected = &state->start_history;
    uint64_t depth, max_depth;

    if (offset == 0 || !selected->valid)
        return NULL;
    max_depth = current_frame < E003I_WINDOWS_HISTORY_CAPACITY ?
        current_frame : E003I_WINDOWS_HISTORY_CAPACITY;
    for (depth = 1; depth <= max_depth; ++depth) {
        uint64_t saved_frame = current_frame - depth;
        const struct e003i_request_history_entry *e =
            history_exact(state, saved_frame);
        if (e == NULL)
            return NULL; /* sequential ordinary stream must not have holes */
        selected = e;
        if (saved_frame + (uint64_t)offset <= current_frame)
            break;
    }
    return selected;
}

int e003i_request_loop_process(struct e003i_request_loop_state *state,
                               const struct e003i_request_loop_input *in,
                               struct e003i_request_loop_output *out)
{
    const struct e003i_request_history_entry *h1, *h2, *h3;
    struct e003i_final_exposure_input fi;
    struct e003i_front_preview_unlocked_qword_history_input ci;
    struct e003i_request_history_entry *cur;
    float lux_in, frame_target, frame_adj, frame_conf, href, next_lux;
    int rc;

    if (state == NULL || in == NULL || out == NULL)
        return -1;
    if (in->frame_id != state->next_frame_id)
        return -2;
    if (!isfinite(in->measured_luma) || !(in->measured_luma > 0.0f))
        return -3;

    h1 = history_get_offset(state, in->frame_id, 1);
    h2 = history_get_offset(state, in->frame_id, 2);
    h3 = history_get_offset(state, in->frame_id, 3);
    if (h1 == NULL || h2 == NULL || h3 == NULL)
        return -4;

    lux_in = state->lux_trigger;
    if (!isfinite(lux_in))
        return -4;
    frame_target = e003i_framesa_target_low(lux_in);
    frame_adj = fdiv32(frame_target, in->measured_luma);
    frame_conf = f32bits(0x3a83126fU); /* BG FrameSA_Confidence = 0.001f. */
    if (!isfinite(frame_target) || !isfinite(frame_adj) || !(frame_adj > 0.0f))
        return -5;

    memset(out, 0, sizeof(*out));
    memset(&fi, 0, sizeof(fi));
    fi.source_exposure_s1 = h3->s1_exposure;
    fi.target_input.lux_index = lux_in;
    fi.target_input.frame.value = frame_adj;
    fi.target_input.frame.confidence = frame_conf;
    fi.target_input.sat_prev = in->analyzers.sat_prev;
    fi.target_input.dark_prev = in->analyzers.dark_prev;
    fi.target_input.brighten = in->analyzers.brighten;
    fi.target_input.extreme_color = in->analyzers.extreme_color;
    fi.target_input.illuminance = in->analyzers.illuminance;
    fi.target_input.short_sat_prev = in->analyzers.short_sat_prev;
    fi.target_input.long_dark_prev = in->analyzers.long_dark_prev;

    rc = e003i_aec_default_final_exposures(&fi, &out->target_publication);
    if (rc != 0)
        return -10 + rc;

    memset(&ci, 0, sizeof(ci));
    ci.target_exposure[E003I_LANE_SHORT] = out->target_publication.short_exposure;
    ci.target_exposure[E003I_LANE_LONG] = out->target_publication.long_exposure;
    ci.target_exposure[E003I_LANE_SAFE] = out->target_publication.safe_exposure;
    ci.history1.short_exposure = h1->short_exposure;
    ci.history1.long_exposure = h1->long_exposure;
    ci.history1.safe_exposure = h1->safe_exposure;
    ci.history1.drc_gain = h1->pred_gain;
    ci.history2.short_exposure = h2->short_exposure;
    ci.history2.long_exposure = h2->long_exposure;
    ci.history2.safe_exposure = h2->safe_exposure;
    ci.history2.drc_gain = h2->pred_gain;
    ci.delayed_history.safe_exposure = h3->safe_exposure;

    rc = e003i_converge_front_preview_unlocked_qword_history(&ci,
                                                             &out->convergence);
    if (rc != 0)
        return -20 + rc;

    rc = e003i_t681_preview_arbitrate(out->convergence.linear[E003I_LANE_SHORT],
                                      &out->short_arbitration);
    if (rc != 0)
        return -30 + rc;
    rc = e003i_t681_preview_arbitrate(out->convergence.linear[E003I_LANE_LONG],
                                      &out->long_arbitration);
    if (rc != 0)
        return -40 + rc;
    rc = e003i_t681_preview_arbitrate(out->convergence.linear[E003I_LANE_SAFE],
                                      &out->safe_arbitration);
    if (rc != 0)
        return -50 + rc;
    rc = e003i_t681_preview_arbitrate(out->convergence.linear[E003I_LANE_S1],
                                      &out->s1_arbitration);
    if (rc != 0)
        return -60 + rc;

    href = e003i_log103_coordinate(h3->s1_exposure);
    next_lux = e003i_algorithm001_lux(in->measured_luma, href, lux_in,
                                      state->algorithm001_alpha);
    if (!isfinite(href) || !isfinite(next_lux))
        return -70;

    out->lux_trigger_in = lux_in;
    out->frame_target = frame_target;
    out->frame_candidate.value = frame_adj;
    out->frame_candidate.confidence = frame_conf;
    out->history_reference_log103 = href;
    out->next_lux_trigger = next_lux;

    /* Commit only after all current-request arithmetic has succeeded. */
    cur = history_slot(state, in->frame_id);
    cur->frame_id = in->frame_id;
    cur->short_exposure = out->short_arbitration.retained_exposure;
    cur->long_exposure = out->long_arbitration.retained_exposure;
    cur->safe_exposure = out->safe_arbitration.retained_exposure;
    cur->s1_exposure = out->s1_arbitration.retained_exposure;
    cur->pred_gain = out->convergence.pred_gain;
    cur->valid = 1;
    state->lux_trigger = next_lux;
    state->next_frame_id++;
    return 0;
}
