// SPDX-License-Identifier: GPL-2.0-only
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "production-write-policy.h"

static void exact(struct e003i_raw_control_output *o)
{
    uint32_t isp = UINT32_C(0x3f801646);
    memset(o,0,sizeof(*o));
    o->stats_owned_request_frame=UINT64_C(7);
    o->sensor_pipeline_delay_frames=2;
    o->camx_history_realign_frames=0;
    o->raw.request.capped.linear[E003I_LANE_SHORT]=UINT64_C(6133333088);
    o->raw.request.short_arbitration.retained_exposure=UINT64_C(6133332579);
    o->controls.line_count_before_even=7108;
    o->controls.frame_length_lines=7116;
    o->controls.vertical_blanking=4956;
    o->controls.exposure_lines=7108;
    o->controls.analogue_gain_code=960;
    o->controls.digital_gain_code=1471;
    memcpy(&o->controls.isp_gain,&isp,4);
}
#define REJECT(tag,stmt) do{struct e003i_raw_control_output x;exact(&x);stmt;if(sp11_front_g4_startup_fill_exact(SP11_FRONT_POST_G3_G4_STARTUP_FILL_SHADOW,4,&x)){fprintf(stderr,"accepted mutation: %s\n",tag);return 20;}}while(0)
int main(void)
{
    struct e003i_raw_control_output o; enum sp11_front_post_g3_policy p;
    exact(&o);
    if(sp11_front_parse_post_g3_policy("shadow",&p)||p!=SP11_FRONT_POST_G3_SHADOW)return 1;
    if(sp11_front_post_g3_apply_allowed(p,E003I_HA_APPLY_ONE_NATIVE))return 2;
    if(sp11_front_parse_post_g3_policy("cap-release-one-shot",&p)||p!=SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT)return 3;
    if(!sp11_front_post_g3_apply_allowed(p,E003I_HA_APPLY_ONE_NATIVE))return 4;
    if(sp11_front_post_g3_apply_allowed(p,E003I_HA_SHADOW_CAP_ACTIVE))return 5;
    if(sp11_front_parse_post_g3_policy("g4-startup-fill-shadow",&p)||p!=SP11_FRONT_POST_G3_G4_STARTUP_FILL_SHADOW)return 6;
    if(strcmp(sp11_front_post_g3_policy_name(p),"g4-startup-fill-shadow"))return 2;
    if(!sp11_front_g4_startup_fill_exact(p,4,&o))return 3;
    if(sp11_front_g4_startup_fill_exact(SP11_FRONT_POST_G3_SHADOW,4,&o))return 4;
    if(sp11_front_g4_startup_fill_exact(SP11_FRONT_POST_G3_CAP_RELEASE_ONE_SHOT,4,&o))return 5;
    if(sp11_front_g4_startup_fill_exact(p,5,&o))return 6;
    if(sp11_front_post_g3_apply_allowed(p,E003I_HA_APPLY_ONE_NATIVE))return 7;
    REJECT("request",x.stats_owned_request_frame++);
    REJECT("pipeline",x.sensor_pipeline_delay_frames++);
    REJECT("realign",x.camx_history_realign_frames++);
    REJECT("cap",x.raw.request.capped.linear[E003I_LANE_SHORT]--);
    REJECT("retained",x.raw.request.short_arbitration.retained_exposure--);
    REJECT("line_count",x.controls.line_count_before_even--);
    REJECT("fll",x.controls.frame_length_lines--);
    REJECT("vb",x.controls.vertical_blanking--);
    REJECT("exp",x.controls.exposure_lines--);
    REJECT("again",x.controls.analogue_gain_code--);
    REJECT("dgain",x.controls.digital_gain_code--);
    REJECT("isp",{uint32_t u=UINT32_C(0x3f801647);memcpy(&x.controls.isp_gain,&u,4);});
    puts("E004EK_POLICY_UNIT=PASS EXACT_G4_ONLY=YES LATER_APPLY_ALLOWED=NO");
    return 0;
}
