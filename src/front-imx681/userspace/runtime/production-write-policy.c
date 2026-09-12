// SPDX-License-Identifier: GPL-2.0-only
#include "production-write-policy.h"
#include <errno.h>
#include <stddef.h>
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
    return -EINVAL;
}

int sp11_front_post_g3_apply_allowed(enum sp11_front_post_g3_policy policy,
                                     enum e003i_ha_decision decision)
{
    return policy == SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT &&
           decision == E003I_HA_APPLY_ONE_NATIVE;
}

const char *sp11_front_post_g3_policy_name(enum sp11_front_post_g3_policy policy)
{
    switch (policy) {
    case SP11_FRONT_POST_G3_SHADOW:
        return "shadow";
    case SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT:
        return "cap-release-one-shot";
    default:
        return "invalid";
    }
}
