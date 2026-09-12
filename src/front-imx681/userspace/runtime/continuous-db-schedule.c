// SPDX-License-Identifier: GPL-2.0-only
#include "continuous-db-schedule.h"

#include <limits.h>
#include <math.h>
#include <stddef.h>
#include <string.h>

#define E003I_CONT_IMX681_HEIGHT 2160U
#define E003I_CONT_IMX681_DEFAULT_FLL 3554U
#define E003I_CONT_IMX681_VERT_OFFSET 8U
#define E003I_CONT_IMX681_EXPOSURE_MIN 4U
#define E003I_CONT_IMX681_ANALOGUE_MAX 0x03c0U
#define E003I_CONT_IMX681_DIGITAL_MIN 0x0100U
#define E003I_CONT_IMX681_DIGITAL_MAX 0x0f00U

static uint32_t pending_slot(uint32_t generation)
{
    return (generation - 1U) % E003I_CONT_PENDING_SLOTS;
}

void e003i_cont_schedule_init(struct e003i_cont_schedule_state *state)
{
    if (state != NULL)
        memset(state, 0, sizeof(*state));
}

void e003i_cont_schedule_fail(struct e003i_cont_schedule_state *state)
{
    if (state != NULL)
        state->failed = 1U;
}

int e003i_cont_controls_valid(const struct e003i_imx681_controls *c)
{
    uint32_t expected_fll;

    if (c == NULL)
        return 0;
    if (!isfinite(c->isp_gain) || !(c->isp_gain > 0.0f))
        return 0;
    if (c->frame_length_lines < E003I_CONT_IMX681_HEIGHT ||
        c->vertical_blanking != c->frame_length_lines - E003I_CONT_IMX681_HEIGHT)
        return 0;
    if (c->line_count_before_even < E003I_CONT_IMX681_EXPOSURE_MIN)
        return 0;
    if (c->exposure_lines != (c->line_count_before_even & ~1U) ||
        c->exposure_lines < E003I_CONT_IMX681_EXPOSURE_MIN)
        return 0;

    expected_fll = E003I_CONT_IMX681_DEFAULT_FLL;
    if (c->line_count_before_even >
        E003I_CONT_IMX681_DEFAULT_FLL - E003I_CONT_IMX681_VERT_OFFSET)
        expected_fll = c->line_count_before_even + E003I_CONT_IMX681_VERT_OFFSET;
    if (c->frame_length_lines != expected_fll)
        return 0;
    if (c->exposure_lines > ((c->frame_length_lines - 4U) & ~1U))
        return 0;
    if (c->analogue_gain_code > E003I_CONT_IMX681_ANALOGUE_MAX)
        return 0;
    if (c->digital_gain_code < E003I_CONT_IMX681_DIGITAL_MIN ||
        c->digital_gain_code > E003I_CONT_IMX681_DIGITAL_MAX)
        return 0;
    return 1;
}

int e003i_cont_schedule_queue(struct e003i_cont_schedule_state *state,
                              uint32_t generation,
                              const struct e003i_imx681_controls *controls)
{
    uint32_t slot;

    if (state == NULL || controls == NULL)
        return -1;
    if (state->failed)
        return -2;
    if (generation == 0U || generation > UINT32_MAX - E003I_CONT_STATS_TO_REQUEST_DELAY ||
        generation != state->queued_generation + 1U) {
        state->failed = 1U;
        return -3;
    }
    if (!e003i_cont_controls_valid(controls)) {
        state->failed = 1U;
        return -4;
    }
    slot = pending_slot(generation);
    if (state->pending_valid[slot]) {
        /* A prior source survived long enough to collide: caller missed a release. */
        state->failed = 1U;
        return -5;
    }
    state->pending[slot] = *controls;
    state->pending_generation[slot] = generation;
    state->pending_valid[slot] = 1U;
    state->queued_generation = generation;
    return 0;
}

int e003i_cont_schedule_release(struct e003i_cont_schedule_state *state,
                                uint32_t completed_video_generation,
                                struct e003i_cont_apply_event *event)
{
    uint32_t source, slot;

    if (state == NULL || event == NULL)
        return -1;
    memset(event, 0, sizeof(*event));
    if (state->failed)
        return -2;
    if (completed_video_generation < 2U ||
        completed_video_generation > UINT32_MAX - E003I_CONT_WRITE_TO_EFFECT_DELAY) {
        state->failed = 1U;
        return -3;
    }
    source = completed_video_generation - E003I_CONT_WRITE_AFTER_OFFSET;
    if (source != state->released_source_generation + 1U ||
        source > state->queued_generation) {
        state->failed = 1U;
        return -4;
    }
    slot = pending_slot(source);
    if (!state->pending_valid[slot] || state->pending_generation[slot] != source) {
        state->failed = 1U;
        return -5;
    }

    event->apply = 1U;
    event->source_generation = source;
    event->write_after_generation = completed_video_generation;
    event->logical_request_frame = (uint64_t)source + E003I_CONT_STATS_TO_REQUEST_DELAY;
    event->expected_effect_generation = completed_video_generation + E003I_CONT_WRITE_TO_EFFECT_DELAY;
    event->controls = state->pending[slot];
    if (event->logical_request_frame != event->expected_effect_generation) {
        state->failed = 1U;
        memset(event, 0, sizeof(*event));
        return -6;
    }

    state->pending_valid[slot] = 0U;
    state->pending_generation[slot] = 0U;
    state->released_source_generation = source;
    return 0;
}
