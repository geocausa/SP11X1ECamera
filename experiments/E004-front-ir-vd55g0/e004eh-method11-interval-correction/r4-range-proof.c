// SPDX-License-Identifier: GPL-2.0-only
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "native-target-aggregate.h"
static float f32(uint32_t u){ float v; memcpy(&v,&u,4); return v; }
static uint32_t bits(float v){ uint32_t u; memcpy(&u,&v,4); return u; }
int main(void)
{
    struct e003i_weighted_range r[3] = {0};
    struct e003i_weighted_point p[3] = {0};
    float range_out=-1.0f, point_out=-1.0f;
    r[0]=(struct e003i_weighted_range){f32(0x42809ffb),f32(0x42809ffb),f32(0x3a83126f)};
    r[1]=(struct e003i_weighted_range){f32(0x00000000),f32(0x430d7247),f32(0x3ee8d8f3)};
    r[2]=(struct e003i_weighted_range){f32(0x4203f081),f32(0x446a8f1d),f32(0x3e356210)};
    for (int i=0;i<3;i++) { p[i].value=r[i].high; p[i].weight=r[i].weight; }
    if (e003i_method11_range_aggregate(r,3,&range_out) || e003i_method11_point_aggregate(p,3,&point_out)) return 2;
    printf("FRAME=0x42809ffb %.9g\n",r[0].low);
    printf("WINDOWS_RANGE=0x%08x %.9g\n",bits(range_out),range_out);
    printf("OLD_POINT=0x%08x %.9g\n",bits(point_out),point_out);
    return bits(range_out)==0x42809ffbU && bits(point_out)==0x43b62909U ? 0 : 3;
}
