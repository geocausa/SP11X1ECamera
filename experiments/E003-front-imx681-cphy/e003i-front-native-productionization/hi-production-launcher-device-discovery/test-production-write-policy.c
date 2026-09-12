#include <assert.h>
#include <stdio.h>
#include "production-write-policy.h"

int main(void)
{
    enum sp11_front_post_g3_policy p = SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT;
    assert(sp11_front_parse_post_g3_policy(NULL, &p) == 0 && p == SP11_FRONT_POST_G3_SHADOW);
    assert(sp11_front_parse_post_g3_policy("", &p) == 0 && p == SP11_FRONT_POST_G3_SHADOW);
    assert(sp11_front_parse_post_g3_policy("shadow", &p) == 0 && p == SP11_FRONT_POST_G3_SHADOW);
    assert(sp11_front_parse_post_g3_policy("cap-release-one-shot", &p) == 0 && p == SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT);
    assert(sp11_front_parse_post_g3_policy("unsafe", &p) != 0);
    assert(sp11_front_parse_post_g3_policy("cap-release-one-shot", NULL) != 0);
    assert(!sp11_front_post_g3_apply_allowed(SP11_FRONT_POST_G3_SHADOW, E003I_HA_APPLY_ONE_NATIVE));
    assert(!sp11_front_post_g3_apply_allowed(SP11_FRONT_POST_G3_SHADOW, E003I_HA_SHADOW_CAP_ACTIVE));
    assert(sp11_front_post_g3_apply_allowed(SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT, E003I_HA_APPLY_ONE_NATIVE));
    assert(!sp11_front_post_g3_apply_allowed(SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT, E003I_HA_SHADOW_CAP_ACTIVE));
    assert(!sp11_front_post_g3_apply_allowed(SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT, E003I_HA_SHADOW_ALREADY_APPLIED));
    assert(sp11_front_post_g3_policy_name(SP11_FRONT_POST_G3_SHADOW)[0] == 's');
    puts("HI_PRODUCTION_WRITE_POLICY=PASS DEFAULT=shadow");
    return 0;
}
