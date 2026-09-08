// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_AEC_STATE_H
#define E003I_NATIVE_AEC_STATE_H
#include <stdint.h>

#define E003I_AEC_LANES 7
#define E003I_AEC_HISTORY_SLOTS 32
#define E003I_AEC_PUBLICATION_SLOTS 8
#define E003I_AEC_S1_LANE 3

struct e003i_aec_history_entry {
    uint64_t frame_id;
    uint64_t lanes[E003I_AEC_LANES];
    uint8_t valid;
};

struct e003i_aec_publication_entry {
    uint64_t frame_id;
    float lux;
    uint8_t valid;
};

struct e003i_aec_state {
    float lux_trigger;
    float algorithm001_alpha;
    struct e003i_aec_history_entry history[E003I_AEC_HISTORY_SLOTS];
    struct e003i_aec_publication_entry publication[E003I_AEC_PUBLICATION_SLOTS];
};

struct e003i_aec_request_result {
    uint64_t frame_id;
    float lux_trigger_in;
    float target_low;
    float measured_luma;
    uint64_t frame_sa_safe_si;
    uint64_t history_reference_frame;
    uint64_t history_reference_s1_exposure;
    float history_reference_log103;
    float next_lux_trigger;
    uint8_t external_lux_valid;
    float external_lux;
    uint8_t previous_exposure_valid;
    uint64_t previous_exposure_frame;
    uint64_t previous_exposure_lanes[E003I_AEC_LANES];
};

void e003i_aec_state_init(struct e003i_aec_state *state,
                          float initial_lux_trigger,
                          float algorithm001_alpha);
int e003i_aec_state_commit_exposure(struct e003i_aec_state *state,
                                    uint64_t frame_id,
                                    const uint64_t lanes[E003I_AEC_LANES]);
float e003i_framesa_target_low(float lux_trigger);
float e003i_algorithm001_lux(float measured_luma,
                             float history_reference_log103,
                             float previous_lux,
                             float alpha);
int e003i_aec_state_process(struct e003i_aec_state *state,
                            uint64_t frame_id,
                            float measured_luma,
                            uint64_t source_exposure_s1,
                            struct e003i_aec_request_result *out);
#endif
