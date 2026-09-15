// SPDX-License-Identifier: GPL-2.0-only
#include "production-write-policy.h"
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

int sp11_front_parse_post_g3_policy(const char *value,
                                    enum sp11_front_post_g3_policy *out)
{
    if (out == NULL)
        return -EINVAL;
    if (value == NULL || value[0] == '\0' || strcmp(value, "shadow") == 0) {
        *out = SP11_FRONT_POST_G3_SHADOW;
        return 0;
    }
    if (strcmp(value, "cap-release-one-shot") == 0) {
        *out = SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT;
        return 0;
    }
    if (strcmp(value, "g4-startup-fill-shadow") == 0) {
        *out = SP11_FRONT_POST_G3_G4_STARTUP_FILL_SHADOW;
        return 0;
    }
    return -EINVAL;
}

int sp11_front_post_g3_apply_allowed(enum sp11_front_post_g3_policy policy,
                                     enum e003i_ha_decision decision)
{
    return policy == SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT &&
           decision == E003I_HA_APPLY_ONE_NATIVE;
}

int sp11_front_g4_startup_fill_exact(
    enum sp11_front_post_g3_policy policy,
    uint32_t source_generation,
    const struct e003i_raw_control_output *native_output)
{
    uint32_t isp_bits;

    if (policy != SP11_FRONT_POST_G3_G4_STARTUP_FILL_SHADOW ||
        source_generation != 4U || native_output == NULL)
        return 0;

    memcpy(&isp_bits, &native_output->controls.isp_gain, sizeof(isp_bits));
    return native_output->stats_owned_request_frame == UINT64_C(7) &&
           native_output->sensor_pipeline_delay_frames == 2U &&
           native_output->camx_history_realign_frames == 0U &&
           native_output->raw.request.capped.linear[E003I_LANE_SHORT] ==
               UINT64_C(6133333088) &&
           native_output->raw.request.short_arbitration.retained_exposure ==
               UINT64_C(6133332579) &&
           native_output->controls.line_count_before_even == 7108U &&
           native_output->controls.frame_length_lines == 7116U &&
           native_output->controls.vertical_blanking == 4956U &&
           native_output->controls.exposure_lines == 7108U &&
           native_output->controls.analogue_gain_code == 960U &&
           native_output->controls.digital_gain_code == 1471U &&
           isp_bits == UINT32_C(0x3f801646);
}

const char *sp11_front_post_g3_policy_name(enum sp11_front_post_g3_policy policy)
{
    switch (policy) {
    case SP11_FRONT_POST_G3_SHADOW:
        return "shadow";
    case SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT:
        return "cap-release-one-shot";
    case SP11_FRONT_POST_G3_G4_STARTUP_FILL_SHADOW:
        return "g4-startup-fill-shadow";
    default:
        return "invalid";
    }
}
