// SPDX-License-Identifier: GPL-2.0-only
#include "minimal-dgain-sentinel.h"
#include <string.h>

#define E003I_GW_SENTINEL_SOURCE 4U
#define E003I_GW_DIGITAL_GAIN_MAX 0x0f00U

static int exact_controls_equal(const struct e003i_imx681_controls *a,
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

enum e003i_gw_decision
e003i_gw_make_sentinel(uint32_t source_generation,
                       const struct e003i_imx681_controls *last_applied,
                       const struct e003i_imx681_controls *native_candidate,
                       struct e003i_imx681_controls *sentinel)
{
    if (sentinel != NULL)
        memset(sentinel, 0, sizeof(*sentinel));
    if (source_generation != E003I_GW_SENTINEL_SOURCE)
        return E003I_GW_SHADOW_NOT_SOURCE;
    if (last_applied == NULL || native_candidate == NULL || sentinel == NULL ||
        !exact_controls_equal(last_applied, native_candidate))
        return E003I_GW_SHADOW_BASE_CHANGED;
    if (native_candidate->digital_gain_code >= E003I_GW_DIGITAL_GAIN_MAX)
        return E003I_GW_SHADOW_RANGE;

    *sentinel = *native_candidate;
    sentinel->digital_gain_code++;
    return E003I_GW_APPLY_SENTINEL;
}
