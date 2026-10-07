/* SPDX-License-Identifier: MIT */
#include "rear-neutral-scalar.h"
#include <math.h>
#include <stddef.h>

static int qpos(float v, float scale, uint32_t maxv, uint32_t *out)
{
    float x;
    if (!out || !isfinite(v) || v < 0.0f)
        return -1;
    x = floorf(v * scale + 0.5f);
    if (!isfinite(x) || x < 0.0f || x > (float)maxv)
        return -1;
    *out = (uint32_t)x;
    return 0;
}

int e012k_rear_scalar_calculate(const struct e012k_rear_scalar_input *in,
                                struct e012k_rear_scalar_output *out)
{
    const float full = 16383.0f;
    float d[4];
    uint32_t q;
    unsigned i;

    if (!in || !out || in->bayer != 2 ||
        !isfinite(in->demux_gain) || in->demux_gain <= 0.0f ||
        !isfinite(in->awb_g) || !isfinite(in->awb_b) || !isfinite(in->awb_r) ||
        !isfinite(in->predictive_gain) || in->awb_g <= 0.0f ||
        in->awb_b <= 0.0f || in->awb_r <= 0.0f || in->predictive_gain <= 0.0f)
        return -1;
    for (i = 0; i < 4; i++)
        if (!isfinite(in->bls[i]) || in->bls[i] < 0.0f || in->bls[i] >= full ||
            !isfinite(in->channel[i]) || in->channel[i] <= 0.0f)
            return -1;

    /* Source-locked Demux/BLS141 Bayer=2 ordering. */
    d[0] = full / (full - in->bls[1]) * in->demux_gain * in->channel[1];
    d[1] = full / (full - in->bls[3]) * in->demux_gain * in->channel[0];
    d[2] = full / (full - in->bls[2]) * in->demux_gain * in->channel[2];
    d[3] = full / (full - in->bls[0]) * in->demux_gain * in->channel[3];
    for (i = 0; i < 4; i++) {
        if (qpos(d[i], 1024.0f, 0x7fff, &q))
            return -1;
        out->demux_q10[i] = (uint16_t)q;
    }

    if (qpos(in->awb_r / in->awb_g, 4096.0f, 0x3ffff, &out->pdpc_q12[0]) ||
        qpos(in->awb_b / in->awb_g, 4096.0f, 0x3ffff, &out->pdpc_q12[1]) ||
        qpos(in->awb_g / in->awb_r, 4096.0f, 0x3ffff, &out->pdpc_q12[2]) ||
        qpos(in->awb_g / in->awb_b, 4096.0f, 0x3ffff, &out->pdpc_q12[3]))
        return -1;

    if (qpos(in->awb_b * in->predictive_gain, 1024.0f, 0x7fff, &q))
        return -1;
    out->wb_b_q10 = (uint16_t)q;
    if (qpos(in->awb_r * in->predictive_gain, 1024.0f, 0x7fff, &q))
        return -1;
    out->wb_r_q10 = (uint16_t)q;
    return 0;
}
