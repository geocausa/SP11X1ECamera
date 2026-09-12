// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_FINAL_EXPOSURE_H
#define E003I_NATIVE_FINAL_EXPOSURE_H

#include <stdint.h>
#include "native-final-target.h"

struct e003i_final_exposure_input {
    uint64_t source_exposure_s1;
    struct e003i_final_target_input target_input;
};

struct e003i_final_exposure_output {
    struct e003i_final_target_output targets;
    uint64_t short_exposure;
    uint64_t long_exposure;
    uint64_t safe_exposure;
};

/* Ordinary DefaultSequence final target qwords: Short/Long/Safe all source S1. */
int e003i_aec_default_final_exposures(
    const struct e003i_final_exposure_input *in,
    struct e003i_final_exposure_output *out);

#endif
