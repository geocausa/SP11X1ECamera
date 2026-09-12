// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_CONTINUOUS_DB_SCHEDULE_H
#define E003I_CONTINUOUS_DB_SCHEDULE_H

#include <stdint.h>
#include "native-imx681-control.h"

#define E003I_CONT_PENDING_SLOTS 2U
#define E003I_CONT_STATS_TO_REQUEST_DELAY 3U
#define E003I_CONT_WRITE_AFTER_OFFSET 1U
#define E003I_CONT_WRITE_TO_EFFECT_DELAY 2U

struct e003i_cont_apply_event {
    uint32_t apply;
    uint32_t source_generation;
    uint32_t write_after_generation;
    uint32_t expected_effect_generation;
    uint64_t logical_request_frame;
    struct e003i_imx681_controls controls;
};

struct e003i_cont_schedule_state {
    uint32_t queued_generation;
    uint32_t released_source_generation;
    uint32_t failed;
    struct e003i_imx681_controls pending[E003I_CONT_PENDING_SLOTS];
    uint32_t pending_generation[E003I_CONT_PENDING_SLOTS];
    uint32_t pending_valid[E003I_CONT_PENDING_SLOTS];
};

void e003i_cont_schedule_init(struct e003i_cont_schedule_state *state);
void e003i_cont_schedule_fail(struct e003i_cont_schedule_state *state);
int e003i_cont_controls_valid(const struct e003i_imx681_controls *controls);
int e003i_cont_schedule_queue(struct e003i_cont_schedule_state *state,
                              uint32_t generation,
                              const struct e003i_imx681_controls *controls);
int e003i_cont_schedule_release(struct e003i_cont_schedule_state *state,
                                uint32_t completed_video_generation,
                                struct e003i_cont_apply_event *event);

#endif
