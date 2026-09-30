/* SPDX-License-Identifier: MIT */
#ifndef E011AL_BG_WEIGHT_QUAD_PRODUCER_H
#define E011AL_BG_WEIGHT_QUAD_PRODUCER_H
#include <stdint.h>
#include <errno.h>
/* L4 nonnegative IEEE754 binary32 weights in [0,1], and boolean AWB quad.
 * Decode float bits with integer arithmetic. Scaling by16 is exact, then
 * nearest ties away (ARM64 FRINTA) gives Q4. No register input or FPU needed.
 * Other weight domains and quad policies are deliberately unsupported. */
struct e011al_weight_quad_input { uint32_t weight_bits[3],awb_quad; };
struct e011al_weight_quad_output { uint8_t aec_weight_q4[3],awb_quad; };
static int e011al_produce_weight_quad(
    const struct e011al_weight_quad_input *in,
    struct e011al_weight_quad_output *out)
{
    struct e011al_weight_quad_output v={0};
    if(!in||!out) return -EINVAL;
    if(in->awb_quad>1) return -ERANGE;
    for(unsigned int i=0;i<3;i++) {
        uint32_t b=in->weight_bits[i],mag=b&0x7fffffffU;
        uint32_t exponent=(mag>>23)&255U,significand,shift;
        if(((b>>31)&&mag)||mag>0x3f800000U) return -ERANGE;
        if(exponent<122) continue; /* <1/32: scaled value <0.5 */
        shift=146-exponent; /* validated finite domain gives shift19..24 */
        significand=(mag&0x7fffffU)|0x800000U;
        v.aec_weight_q4[i]=(uint8_t)((significand+(1U<<(shift-1)))>>shift);
    }
    v.awb_quad=(uint8_t)in->awb_quad;
    *out=v;return 0;
}
#endif
