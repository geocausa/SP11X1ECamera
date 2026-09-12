// SPDX-License-Identifier: GPL-2.0-only
#include "native-cap-release-policy.h"
#include <string.h>

#define E003I_HA_PREVIEW_CAP_MAX UINT64_C(6133333088)

static int controls_equal(const struct e003i_imx681_controls *a,
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

enum e003i_ha_decision
e003i_ha_decide(uint32_t source_generation,
                uint32_t later_native_write_already_applied,
                const struct e003i_imx681_controls *last_applied,
                const struct e003i_raw_control_output *native_output)
{
    uint64_t conv, cap;
    if (source_generation <= 3U)
        return E003I_HA_STARTUP_OWNED;
    if (last_applied == NULL || native_output == NULL)
        return E003I_HA_SHADOW_INVALID;
    if (later_native_write_already_applied)
        return E003I_HA_SHADOW_ALREADY_APPLIED;

    conv = native_output->raw.request.convergence.linear[E003I_LANE_SHORT];
    cap = native_output->raw.request.capped.linear[E003I_LANE_SHORT];

    /* Fail closed unless Short is demonstrably below, and untouched by, cap. */
    if (conv >= E003I_HA_PREVIEW_CAP_MAX || cap != conv)
        return E003I_HA_SHADOW_CAP_ACTIVE;
    if (controls_equal(last_applied, &native_output->controls))
        return E003I_HA_SHADOW_UNCHANGED;
    return E003I_HA_APPLY_ONE_NATIVE;
}
