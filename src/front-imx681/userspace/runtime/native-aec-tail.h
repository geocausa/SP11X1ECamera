// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_AEC_TAIL_H
#define E003I_NATIVE_AEC_TAIL_H

struct e003i_aec_tail_input {
    float lux_index;
    float safe_adj_ratio; /* SceneAnalyzer 3:9 */
    float short_target;   /* SceneAnalyzer 3:10 */
    float long_target;    /* SceneAnalyzer 3:12 */
};

struct e003i_aec_tail_output {
    float adrc_lux_cap;       /* Triggers 9:54 */
    float adj_ratio_short;    /* SceneAnalyzer 3:66 */
    float adrc_gain;          /* SceneAnalyzer 3:67 */
    float short_adj_ratio;    /* SceneAnalyzer 3:11 */
    float drc_gain_remainder; /* SceneAnalyzer 3:157 */
    float adj_ratio_long;     /* SceneAnalyzer 3:68 */
    float dark_boost_gain;    /* SceneAnalyzer 3:69 */
    float long_adj_ratio;     /* SceneAnalyzer 3:13 */
};

/*
 * Native transcription of the Windows ordinary/default AEC arithmetic tail
 * closed by CB. Inputs are finite positive target/ratio scalars and finite Lux.
 * The implementation deliberately preserves Windows float32 interpolation
 * order, including equal-endpoint interpolation in outer trigger gaps.
 */
int e003i_aec_default_tail(const struct e003i_aec_tail_input *in,
                           struct e003i_aec_tail_output *out);

#endif
