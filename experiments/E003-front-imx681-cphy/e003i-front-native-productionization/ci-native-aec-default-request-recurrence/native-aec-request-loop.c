// SPDX-License-Identifier: GPL-2.0-only
#include "native-aec-request-loop.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

void e003i_request_loop_init(struct e003i_request_loop_state *state)
{
    if (state != NULL)
        memset(state, 0, sizeof(*state));
}

static struct e003i_request_history_entry *history_slot(
    struct e003i_request_loop_state *state, uint64_t frame_id)
{
    return &state->history[frame_id % E003I_REQUEST_HISTORY_SLOTS];
}

static const struct e003i_request_history_entry *history_get(
    const struct e003i_request_loop_state *state, uint64_t frame_id)
{
    const struct e003i_request_history_entry *e =
        &state->history[frame_id % E003I_REQUEST_HISTORY_SLOTS];
    return e->valid && e->frame_id == frame_id ? e : NULL;
}

int e003i_request_loop_seed_history(struct e003i_request_loop_state *state,
                                    uint64_t frame_id,
                                    uint64_t short_exposure,
                                    uint64_t long_exposure,
                                    uint64_t safe_exposure,
                                    float pred_gain)
{
    struct e003i_request_history_entry *e;
    if (state == NULL || short_exposure == 0 || long_exposure == 0 ||
        safe_exposure == 0 || !isfinite(pred_gain) || !(pred_gain > 0.0f))
        return -1;
    e = history_slot(state, frame_id);
    e->frame_id = frame_id;
    e->short_exposure = short_exposure;
    e->long_exposure = long_exposure;
    e->safe_exposure = safe_exposure;
    e->pred_gain = pred_gain;
    e->valid = 1;
    return 0;
}

int e003i_request_loop_process(struct e003i_request_loop_state *state,
                               const struct e003i_request_loop_input *in,
                               struct e003i_request_loop_output *out)
{
    const struct e003i_request_history_entry *h1, *h2, *h3;
    struct e003i_final_exposure_input fi;
    struct e003i_front_preview_unlocked_qword_history_input ci;
    struct e003i_request_history_entry *cur;
    int rc;

    if (state == NULL || in == NULL || out == NULL || in->frame_id < 3)
        return -1;
    h1 = history_get(state, in->frame_id - 1);
    h2 = history_get(state, in->frame_id - 2);
    h3 = history_get(state, in->frame_id - 3);
    if (h1 == NULL || h2 == NULL || h3 == NULL)
        return -2;

    memset(out, 0, sizeof(*out));
    memset(&fi, 0, sizeof(fi));
    fi.source_exposure_s1 = in->source_exposure_s1;
    fi.target_input = in->target_input;
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

    /* AX + BA + PopulateOutput/runEndOfFrame recurrence. */
    cur = history_slot(state, in->frame_id);
    cur->frame_id = in->frame_id;
    cur->short_exposure = out->short_arbitration.retained_exposure;
    cur->long_exposure = out->long_arbitration.retained_exposure;
    cur->safe_exposure = out->safe_arbitration.retained_exposure;
    cur->pred_gain = out->convergence.pred_gain;
    cur->valid = 1;
    return 0;
}
