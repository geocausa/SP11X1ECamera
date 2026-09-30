/* SPDX-License-Identifier: MIT */
/* L4/user-space source scalar arithmetic. No camera or Windows dependency. */
#ifndef E011AI_SCALAR_PRODUCER_H
#define E011AI_SCALAR_PRODUCER_H
#include <stdint.h>
#include <math.h>
#include <string.h>

struct e011ai_scalar_inputs {
    float demux_gain, bls[4], channel[4];
    float awb_g, awb_b, awb_r, predictive_gain;
    uint32_t bayer;
};
struct e011ai_scalar_output {
    uint16_t demux_q10[4];
    uint32_t pdpc_q12[4];
    uint16_t wb_b_q10, wb_r_q10;
};

/* The audited rear path uses Bayer enum2 and ordinary WB without optional
 * normalization. Other Bayer/WB policy branches remain outside this domain.
 * Volatile results preserve separate source binary32 operations, no FMA. */
static float e011ai_mul(float a,float b) { volatile float r=a*b;return r; }
static float e011ai_div(float a,float b) { volatile float r=a/b;return r; }
static float e011ai_sub(float a,float b) { volatile float r=a-b;return r; }
static uint32_t e011ai_quant(float value,uint32_t lo,uint32_t hi) {
    float q=roundf(value);
    if(q<=(float)lo)return lo;
    if(q>=(float)hi)return hi;
    return (uint32_t)q;
}
static int e011ai_produce_scalar(const struct e011ai_scalar_inputs *in,
                                struct e011ai_scalar_output *out)
{
    struct e011ai_scalar_output result={0};
    float gain[4],peak=0.0f;
    /* Bound intermediates and C conversions; this is an admitted source slice,
     * not a claim that every original exceptional input is a supported policy. */
    if(!in||!out||in->bayer!=2||!isfinite(in->demux_gain)||
       in->demux_gain<0.0f||in->demux_gain>32.0f||
       !isfinite(in->awb_g)||!isfinite(in->awb_b)||!isfinite(in->awb_r)||
       !isfinite(in->predictive_gain)||in->awb_g<0.0f||in->awb_b<0.0f||
       in->awb_r<0.0f||in->awb_g>32.0f||in->awb_b>32.0f||in->awb_r>32.0f||
       in->predictive_gain<=0.0f||in->predictive_gain>32.0f)
        return -1;
    for(unsigned int i=0;i<4;i++)
        if(!isfinite(in->bls[i])||!isfinite(in->channel[i])||
           in->bls[i]<0.0f||in->bls[i]>16382.0f||
           in->channel[i]<0.0f||in->channel[i]>32.0f)
            return -1;
    /* Common output order for Bayer2, independently checked at Titan680 pack. */
    const unsigned int bls_lane[4]={1,3,2,0},channel_lane[4]={1,0,2,3};
    for(unsigned int i=0;i<4;i++) {
        gain[i]=e011ai_mul(e011ai_mul(e011ai_div(16383.0f,
            e011ai_sub(16383.0f,in->bls[bls_lane[i]])),in->demux_gain),
            in->channel[channel_lane[i]]);
        if(gain[i]>peak)peak=gain[i];
    }
    if(peak>31.999f) {
        float scale=e011ai_div(31.999f,peak);
        for(unsigned int i=0;i<4;i++)gain[i]=e011ai_mul(scale,gain[i]);
    }
    for(unsigned int i=0;i<4;i++)
        result.demux_q10[i]=(uint16_t)e011ai_quant(e011ai_mul(gain[i],1024.0f),0,32767);
    const float num[4]={in->awb_r,in->awb_b,in->awb_g,in->awb_g};
    const float den[4]={in->awb_g,in->awb_g,in->awb_r,in->awb_b};
    for(unsigned int i=0;i<4;i++) {
        float q=(double)fabsf(den[i])<1e-6?128.0f:
            e011ai_mul(e011ai_div(num[i],den[i]),4096.0f);
        result.pdpc_q12[i]=e011ai_quant(q,128,131071);
    }
    result.wb_b_q10=(uint16_t)e011ai_quant(
        e011ai_mul(e011ai_mul(in->awb_b,in->predictive_gain),1024.0f),0,32767);
    result.wb_r_q10=(uint16_t)e011ai_quant(
        e011ai_mul(e011ai_mul(in->awb_r,in->predictive_gain),1024.0f),0,32767);
    memcpy(out,&result,sizeof(result));
    return 0;
}
#endif
