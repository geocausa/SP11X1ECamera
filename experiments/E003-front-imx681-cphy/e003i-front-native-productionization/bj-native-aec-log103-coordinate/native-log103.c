// SPDX-License-Identifier: GPL-2.0-only
#include "native-log103.h"
#include <math.h>
#include <string.h>

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

float e003i_log103_coordinate(uint64_t exposure)
{
    const float base = 37516.0f;
    const float reciprocal_log10_103 = f32bits(0x429bcc0cU);
    float ratio = (float)exposure / base;

    if (ratio == 0.0f)
        return 0.0f;

    return (float)(log10((double)ratio) *
                   (double)reciprocal_log10_103);
}

uint32_t e003i_log103_coordinate_bits(uint64_t exposure)
{
    float f = e003i_log103_coordinate(exposure);
    uint32_t u;
    memcpy(&u, &f, sizeof(u));
    return u;
}
