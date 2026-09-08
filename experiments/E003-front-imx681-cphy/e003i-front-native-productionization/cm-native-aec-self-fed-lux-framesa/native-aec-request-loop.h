// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_AEC_REQUEST_LOOP_CM_H
#define E003I_NATIVE_AEC_REQUEST_LOOP_CM_H
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
    float lux_trigger;
    float algorithm001_alpha;
    struct e003i_request_history_entry history[E003I_REQUEST_HISTORY_SLOTS];
};

struct e003i_remaining_analyzer_input {
    struct e003i_aec_candidate sat_prev;
    struct e003i_aec_candidate dark_prev;
    struct e003i_aec_candidate brighten;
    struct e003i_aec_candidate extreme_color;
    struct e003i_aec_candidate illuminance;
    struct e003i_aec_candidate short_sat_prev;
    struct e003i_aec_candidate long_dark_prev;
};

struct e003i_request_loop_input {
    uint64_t frame_id;
    float measured_luma;
    struct e003i_remaining_analyzer_input analyzers;
};

struct e003i_request_loop_output {
    float lux_trigger_in;
    float frame_target;
    struct e003i_aec_candidate frame_candidate;
    float history_reference_log103;
    float next_lux_trigger;
    struct e003i_final_exposure_output target_publication;
    struct e003i_conv_output convergence;
    struct e003i_t681_result short_arbitration;
    struct e003i_t681_result long_arbitration;
    struct e003i_t681_result safe_arbitration;
    struct e003i_t681_result s1_arbitration;
};

/* Initialization remains the explicit startup seam; alpha is not globally fixed. */
int e003i_request_loop_init(struct e003i_request_loop_state *state,
                            float initial_lux_trigger,
                            float algorithm001_alpha);

int e003i_request_loop_seed_history(struct e003i_request_loop_state *state,
                                    uint64_t frame_id,
                                    uint64_t short_exposure,
                                    uint64_t long_exposure,
                                    uint64_t safe_exposure,
                                    uint64_t s1_exposure,
                                    float pred_gain);

/* Warmed-up ordinary DefaultSequence request. */
int e003i_request_loop_process(struct e003i_request_loop_state *state,
                               const struct e003i_request_loop_input *in,
                               struct e003i_request_loop_output *out);

#endif
