/* SPDX-License-Identifier: MIT */
#ifndef SP11_E012K_REAR_NEUTRAL_SCALAR_H
#define SP11_E012K_REAR_NEUTRAL_SCALAR_H
#include <stdint.h>

struct e012k_rear_scalar_input {
    float demux_gain;
    float bls[4];
    float channel[4];
    float awb_g;
    float awb_b;
    float awb_r;
    float predictive_gain;
    uint8_t bayer;
};

struct e012k_rear_scalar_output {
    uint16_t demux_q10[4];
    uint32_t pdpc_q12[4];
    uint16_t wb_b_q10;
    uint16_t wb_r_q10;
};

int e012k_rear_scalar_calculate(const struct e012k_rear_scalar_input *in,
                                struct e012k_rear_scalar_output *out);
#endif
