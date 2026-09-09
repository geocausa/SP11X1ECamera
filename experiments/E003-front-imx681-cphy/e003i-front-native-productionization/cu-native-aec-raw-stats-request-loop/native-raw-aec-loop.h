// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_RAW_AEC_LOOP_H
#define E003I_NATIVE_RAW_AEC_LOOP_H

#include <stddef.h>
#include <stdint.h>

#include "native-aec-request-loop.h"
#include "native-bhist-bank4.h"
#include "native-effective-analyzers.h"
#include "native-stats3a.h"

struct e003i_raw_request_input {
    uint64_t frame_id;
    const void *stats3a;
    size_t stats3a_bytes;
};

struct e003i_raw_request_output {
    uint64_t stats_generation;
    uint32_t stats_source_seq;
    uint32_t stats_slot;
    float measured_luma;
    struct e003i_bhist_bank4_output bank4;
    struct e003i_final_target_input effective_target;
    struct e003i_request_loop_output request;
};

/*
 * Ordinary uninterrupted cold-start front AEC loop:
 * generation-tagged STATS3A -> FrameSA/BHist -> effective analyzers -> CP.
 * This stops before CQ and therefore performs no sensor-control write.
 */
int e003i_raw_request_loop_process(struct e003i_request_loop_state *state,
                                   const struct e003i_raw_request_input *in,
                                   struct e003i_raw_request_output *out);

#endif
