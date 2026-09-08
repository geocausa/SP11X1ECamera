// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_AEC_REQUEST_LOOP_CL_H
#define E003I_NATIVE_AEC_REQUEST_LOOP_CL_H
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
    uint64_t s1_exposure;
    float pred_gain;
    uint8_t valid;
};

struct e003i_request_loop_state {
    struct e003i_request_history_entry history[E003I_REQUEST_HISTORY_SLOTS];
};

struct e003i_request_loop_input {
    uint64_t frame_id;
    struct e003i_final_target_input target_input;
};

struct e003i_request_loop_output {
    struct e003i_final_exposure_output target_publication;
    struct e003i_conv_output convergence;
    struct e003i_t681_result short_arbitration;
    struct e003i_t681_result long_arbitration;
    struct e003i_t681_result safe_arbitration;
    struct e003i_t681_result s1_arbitration;
};

void e003i_request_loop_init(struct e003i_request_loop_state *state);

/* Explicit warm-up seam. CK requires F-3 retained S1 as well as CI history. */
int e003i_request_loop_seed_history(struct e003i_request_loop_state *state,
                                    uint64_t frame_id,
                                    uint64_t short_exposure,
                                    uint64_t long_exposure,
                                    uint64_t safe_exposure,
                                    uint64_t s1_exposure,
                                    float pred_gain);

/* Warmed-up ordinary DefaultSequence request; source S1 is self-fed from F-3. */
int e003i_request_loop_process(struct e003i_request_loop_state *state,
                               const struct e003i_request_loop_input *in,
                               struct e003i_request_loop_output *out);

#endif
