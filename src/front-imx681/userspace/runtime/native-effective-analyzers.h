// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_EFFECTIVE_ANALYZERS_H
#define E003I_NATIVE_EFFECTIVE_ANALYZERS_H

#include <stdint.h>
#include "native-final-target.h"

struct e003i_effective_analyzer_input {
    float lux_index;                    /* Triggers 9:8 */
    float frame_luma;                   /* SceneAnalyzer 3:4 */
    float frame_target;                 /* SceneAnalyzer 3:5 */
    uint64_t delayed_short_exposure;    /* Triggers 9:28, selected retained history Short */
    float saturate_stats_ratio;         /* StatsCalculator 4:6 */
    float sat_prev_high_pctl_luma;      /* StatsCalculator 4:7 */
    float dark_prev_low_pctl_luma;      /* StatsCalculator 4:8 */
    float short_sat_prev_high_pctl_luma;/* StatsCalculator 4:19 */
};

/*
 * Produce CE's complete ordinary/uninterrupted DefaultSequence analyzer input.
 * The implementation preserves Windows float32 interpolation/arithmetic order.
 * BrightenImgSA, ExtremeColorSA and LongDarkPrevSA are canonicalized to zero
 * because their ordinary default confidence is proven exact +0.0f.
 */
int e003i_aec_default_effective_analyzers(
    const struct e003i_effective_analyzer_input *in,
    struct e003i_final_target_input *out);

#endif
