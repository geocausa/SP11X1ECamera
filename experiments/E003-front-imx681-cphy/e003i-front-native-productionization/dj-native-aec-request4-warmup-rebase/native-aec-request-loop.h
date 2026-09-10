// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_AEC_REQUEST_LOOP_DJ_H
#define E003I_NATIVE_AEC_REQUEST_LOOP_DJ_H
#include <stdint.h>
#include "native-final-exposure.h"
#include "native-convergence.h"
#include "native-t681.h"

#define E003I_REQUEST_HISTORY_SLOTS 16
#define E003I_WINDOWS_HISTORY_CAPACITY 10
#define E003I_WINDOWS_START_EXPOSURE UINT64_C(33333332)
#define E003I_WINDOWS_REQUEST1_ENTRY_LUX_BITS UINT32_C(0x4365b24a)
#define E003I_WINDOWS_REQUEST4_ENTRY_LUX_BITS UINT32_C(0x4365acdd)
#define E003I_WINDOWS_WARMUP_REQUESTS UINT64_C(3)
#define E003I_WINDOWS_WARMUP_EXPOSURE UINT64_C(33312452)
#define E003I_WINDOWS_WARMUP_PRED_GAIN_BITS UINT32_C(0x3f800000)
#define E003I_WINDOWS_ALGORITHM001_ALPHA_BITS UINT32_C(0x00000000)

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
    uint64_t next_frame_id;
    struct e003i_request_history_entry start_history;
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

/*
 * Initialize at the first statistics-owned ordinary request.  The public
 * frame_id remains generation-local (G1 == frame_id 0), while internal history
 * is rebased by the Windows G->request +3 law.  The exact synthetic start record
 * remains installed, and three Windows-proven real warm-up records are seeded
 * for requests 1..3 before local G1/request4 processing begins.
 */
int e003i_request_loop_init(struct e003i_request_loop_state *state);

/*
 * Read one Windows-selected retained-history record for the current request
 * without mutating recurrence state.  CU uses offset 3 to feed raw-stat
 * history-dependent BhistY calculations from the same selector CP owns.
 */
int e003i_request_loop_get_history_offset(
    const struct e003i_request_loop_state *state,
    uint64_t current_frame, unsigned offset,
    struct e003i_request_history_entry *out);

/* Sequential ordinary DefaultSequence request, valid starting at frame 0. */
int e003i_request_loop_process(struct e003i_request_loop_state *state,
                               const struct e003i_request_loop_input *in,
                               struct e003i_request_loop_output *out);

#endif
