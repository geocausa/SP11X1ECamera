// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_BHIST_BANK4_H
#define E003I_NATIVE_BHIST_BANK4_H

#include <stdint.h>

#define E003I_BHIST_BINS 1024u
#define E003I_BHIST_RAW_MASK UINT32_C(0x01ffffff)

struct e003i_bhist_history_input {
    uint64_t safe_exposure; /* retained ordinary F-3 Safe lane */
    uint64_t s1_exposure;   /* retained ordinary F-3 S1 lane */
    float pred_gain;        /* retained ordinary F-3 predictive/DRC gain */
};

struct e003i_bhist_bank4_output {
    float saturate_stats_ratio;          /* Bank4:6 */
    float sat_prev_high_pctl_luma;       /* Bank4:7 */
    float dark_prev_low_pctl_luma;       /* Bank4:8 */
    float short_sat_prev_high_pctl_luma; /* Bank4:19 */
};

/* Build the exact 1024-entry BhistY value axis proven by CT. */
int e003i_bhist_build_value_axis(float axis[E003I_BHIST_BINS]);

/*
 * Offline replay of the four ordinary DefaultSequence BhistY-derived values
 * required by the native effective-analyzer path. raw_words are the Titan680
 * 1024 x u32 BHist words; the Windows parser's 0x01ffffff mask is applied here.
 * history is the same retained ordinary F-3 state already carried by the
 * native request loop. Windows uses it to normalize the BhistY luma cap for
 * Bank4:7/:8. Bank4:6 is a CDF-mass lane and Bank4:19 uses the fixed cap.
 */
int e003i_bhist_replay_bank4(const uint32_t raw_words[E003I_BHIST_BINS],
                             float lux_index,
                             const struct e003i_bhist_history_input *history,
                             struct e003i_bhist_bank4_output *out);

#endif
