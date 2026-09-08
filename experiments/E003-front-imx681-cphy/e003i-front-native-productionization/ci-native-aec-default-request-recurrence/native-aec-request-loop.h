// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_AEC_REQUEST_LOOP_H
#define E003I_NATIVE_AEC_REQUEST_LOOP_H
#include <stdint.h>
#include "native-final-exposure.h"
#include "native-convergence.h"
#include "native-t681.h"

#define E003I_REQUEST_HISTORY_SLOTS 16

struct e003i_request_history_entry {
    uint64_t frame_id;
    uint64_t short_exposure;
    uint64_t long_exposure;
    uint64_t safe_exposure;
    float pred_gain;
    uint8_t valid;
};

struct e003i_request_loop_state {
    struct e003i_request_history_entry history[E003I_REQUEST_HISTORY_SLOTS];
};

struct e003i_request_loop_input {
    uint64_t frame_id;
    uint64_t source_exposure_s1;
    struct e003i_final_target_input target_input;
};

struct e003i_request_loop_output {
    struct e003i_final_exposure_output target_publication;
    struct e003i_conv_output convergence;
    struct e003i_t681_result short_arbitration;
    struct e003i_t681_result long_arbitration;
    struct e003i_t681_result safe_arbitration;
};

void e003i_request_loop_init(struct e003i_request_loop_state *state);

/* Explicit warm-up/bootstrapping seam. */
int e003i_request_loop_seed_history(struct e003i_request_loop_state *state,
                                    uint64_t frame_id,
                                    uint64_t short_exposure,
                                    uint64_t long_exposure,
                                    uint64_t safe_exposure,
                                    float pred_gain);

/* Warmed-up ordinary DefaultSequence request: requires F-1/F-2/F-3 history. */
int e003i_request_loop_process(struct e003i_request_loop_state *state,
                               const struct e003i_request_loop_input *in,
                               struct e003i_request_loop_output *out);

#endif
