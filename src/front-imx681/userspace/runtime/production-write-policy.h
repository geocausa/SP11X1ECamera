// SPDX-License-Identifier: GPL-2.0-only
#ifndef SP11_FRONT_PRODUCTION_WRITE_POLICY_H
#define SP11_FRONT_PRODUCTION_WRITE_POLICY_H
#include "native-cap-release-policy.h"

enum sp11_front_post_g3_policy {
    SP11_FRONT_POST_G3_SHADOW = 0,
    SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT = 1,
};

int sp11_front_parse_post_g3_policy(const char *value,
                                    enum sp11_front_post_g3_policy *out);
int sp11_front_post_g3_apply_allowed(enum sp11_front_post_g3_policy policy,
                                     enum e003i_ha_decision decision);
const char *sp11_front_post_g3_policy_name(enum sp11_front_post_g3_policy policy);
#endif
