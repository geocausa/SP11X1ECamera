// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_DB_SCHEDULE_H
#define E003I_NATIVE_DB_SCHEDULE_H

#include <stdint.h>
#include "native-imx681-control.h"

#define E003I_DB_FRAME_COUNT 6U
#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U
#define E003I_DB_STATS_TO_REQUEST_DELAY 3U
#define E003I_DB_WRITE_AFTER_OFFSET 1U
#define E003I_DB_WRITE_TO_EFFECT_DELAY 2U

struct e003i_db_apply_event {
    uint32_t apply;
    uint32_t source_generation;
    uint32_t write_after_generation;
    uint32_t expected_effect_generation;
    uint64_t logical_request_frame;
    struct e003i_imx681_controls controls;
};

struct e003i_db_schedule_state {
    uint32_t queued_generation;
    uint32_t released_writes;
    uint32_t failed;
    struct e003i_imx681_controls pending[E003I_DB_WRITTEN_SOURCE_GENERATIONS];
    uint32_t pending_valid[E003I_DB_WRITTEN_SOURCE_GENERATIONS];
};

void e003i_db_schedule_init(struct e003i_db_schedule_state *state);
void e003i_db_schedule_fail(struct e003i_db_schedule_state *state);
int e003i_db_controls_valid(const struct e003i_imx681_controls *controls);

/* Queue one native-AEC result in exact generation order. G1..G3 are retained. */
int e003i_db_schedule_queue(struct e003i_db_schedule_state *state,
                            uint32_t generation,
                            const struct e003i_imx681_controls *controls);

/*
 * Release the already-computed G tuple only on completed video generation G+1.
 * The caller owns the actual DQBUF timing gate; this pure helper proves the
 * request/effect algebra and exactly-once ordering.
 */
int e003i_db_schedule_release(struct e003i_db_schedule_state *state,
                              uint32_t completed_video_generation,
                              struct e003i_db_apply_event *event);

#endif
