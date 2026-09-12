// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_FINAL_TARGET_H
#define E003I_NATIVE_FINAL_TARGET_H

#include "native-aec-tail.h"

#define E003I_SAFE_ACTIVE_CANDIDATES 6

struct e003i_aec_candidate {
    float value;
    float confidence;
};

struct e003i_final_target_input {
    float lux_index;
    struct e003i_aec_candidate frame;
    struct e003i_aec_candidate sat_prev;
    struct e003i_aec_candidate dark_prev;
    struct e003i_aec_candidate brighten;
    struct e003i_aec_candidate extreme_color;
    struct e003i_aec_candidate illuminance;
    struct e003i_aec_candidate short_sat_prev;
    struct e003i_aec_candidate long_dark_prev;
};

struct e003i_final_target_output {
    float safe_target;       /* SceneAnalyzer 3:8 */
    float safe_adj_ratio;    /* SceneAnalyzer 3:9, exact identity of 3:8 */
    float short_target;      /* SceneAnalyzer 3:10 */
    float long_target;       /* SceneAnalyzer 3:12 */
    struct e003i_aec_tail_output tail;
};

/*
 * Ordinary uninterrupted DefaultSequence final target producer.
 * Optional SafeAgg candidates are absent/zero by BX and are not public inputs.
 * The shared Safe candidate weight in Short/Long is the CD-proven constant
 * 0.001f, not Frame confidence.
 */
int e003i_aec_default_final_targets(const struct e003i_final_target_input *in,
                                    struct e003i_final_target_output *out);

#endif
