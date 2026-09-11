// SPDX-License-Identifier: GPL-2.0-only
#include "redundant-write-policy.h"
#include <string.h>

#define E003I_REDUNDANT_FIRST_SOURCE 4U
#define E003I_REDUNDANT_LAST_SOURCE 6U

int e003i_sensor_controls_equal(const struct e003i_imx681_controls *a,
                                const struct e003i_imx681_controls *b)
{
    uint32_t af, bf;
    if (a == NULL || b == NULL)
        return 0;
    memcpy(&af, &a->isp_gain, sizeof(af));
    memcpy(&bf, &b->isp_gain, sizeof(bf));
    return a->line_count_before_even == b->line_count_before_even &&
           a->frame_length_lines == b->frame_length_lines &&
           a->vertical_blanking == b->vertical_blanking &&
           a->exposure_lines == b->exposure_lines &&
           a->analogue_gain_code == b->analogue_gain_code &&
           a->digital_gain_code == b->digital_gain_code && af == bf;
}

enum e003i_redundant_write_decision
e003i_redundant_write_decide(uint32_t source_generation,
                             const struct e003i_imx681_controls *last_applied,
                             const struct e003i_imx681_controls *candidate)
{
    if (candidate == NULL)
        return E003I_WRITE_SHADOW_CHANGED;
    if (source_generation >= 1U && source_generation <= 3U)
        return E003I_WRITE_PROVEN_STARTUP;
    if (source_generation >= E003I_REDUNDANT_FIRST_SOURCE &&
        source_generation <= E003I_REDUNDANT_LAST_SOURCE) {
        if (e003i_sensor_controls_equal(last_applied, candidate))
            return E003I_WRITE_REDUNDANT_ALLOWED;
        return E003I_WRITE_SHADOW_CHANGED;
    }
    return E003I_WRITE_SHADOW_BOUND;
}
