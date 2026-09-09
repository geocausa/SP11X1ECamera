// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_IMX681_CONTROL_H
#define E003I_NATIVE_IMX681_CONTROL_H

#include <stdint.h>
#include "native-t681.h"

struct e003i_imx681_controls {
    uint32_t line_count_before_even;
    uint32_t frame_length_lines;
    uint32_t vertical_blanking;
    uint32_t exposure_lines;
    uint32_t analogue_gain_code;
    uint32_t digital_gain_code;
    float isp_gain;
};

/*
 * Ordinary unlocked single-exposure SP11 front-preview adapter.
 * The caller supplies CP/CH's T681 result for the canonical Short lane.
 * BC proves activeExposureCount==1 replicates Short into S1..S4.
 */
int e003i_imx681_controls_from_t681(const struct e003i_t681_result *in,
                                    struct e003i_imx681_controls *out);

#endif
