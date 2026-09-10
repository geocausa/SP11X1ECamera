// SPDX-License-Identifier: GPL-2.0-only
#include "native-internal-cap.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
static uint64_t lo(uint64_t a,uint64_t b){return a<b?a:b;}
static uint64_t hi(uint64_t a,uint64_t b){return a>b?a:b;}
__attribute__((noinline)) static float div32(float a,float b){volatile float r=a/b;return r;}
__attribute__((noinline)) static float mul32(float a,float b){volatile float r=a*b;return r;}
static float frombits(uint32_t u){float f;memcpy(&f,&u,4);return f;}
static uint64_t trunc32(float f){
    if(!(f>0.0f))return 0;
    if((double)f>=18446744073709551616.0)return UINT64_MAX;
    return (uint64_t)f;
}
int e003i_internal_cap(const struct e003i_cap_input *in,struct e003i_cap_output *out){
    struct e003i_cap_output r;
    unsigned i;
    if(!in || !out || !isfinite(in->pred_gain) || in->pred_gain<0.0f ||
       !isfinite(in->compact_98) || !isfinite(in->snap_steps) ||
       in->snap_steps<0.0f || in->rescale_disabled>1 || in->history1_valid>1 ||
       (in->history1_valid && !in->history1_short))return -1;
    for(i=0;i<7;i++)
        if(!in->linear[i] || !in->minimum[i] || in->minimum[i]>in->maximum[i])return -1;
    memset(&r,0,sizeof(r));
    memcpy(r.linear,in->linear,sizeof(r.linear));
    r.pred_gain=in->pred_gain;
    if(r.linear[2]>in->maximum[2] && r.linear[0]<in->maximum[0] &&
       r.linear[0]<r.linear[2] && !in->rescale_disabled){
        float old_short=(float)r.linear[0];
        float ratio=div32((float)r.linear[2],old_short);
        r.linear[0]=trunc32(div32((float)in->maximum[2],ratio));
        r.rescaled=1;
        if(in->history1_valid){
            float a=(float)in->history1_short,b=(float)r.linear[0];
            float distance=mul32(log10f(in->history1_short>r.linear[0] ?
                                      div32(a,b):div32(b,a)),frombits(0x429bcc0cU));
            if(distance<in->snap_steps){
                r.linear[0]=lo(in->history1_short,r.linear[2]);
                r.history_snapped=1;
            }
        }
        r.linear[3]=r.linear[0];
        ratio=div32((float)r.linear[0],old_short);
        for(i=4;i<7;i++)r.linear[i]=trunc32(mul32((float)r.linear[i],ratio));
    }
    for(i=0;i<7;i++)r.linear[i]=lo(hi(r.linear[i],in->minimum[i]),in->maximum[i]);
    r.linear[0]=lo(lo(r.linear[0],r.linear[2]),r.linear[1]);
    if(in->compact_98<frombits(0x3f800001U))r.linear[1]=hi(r.linear[1],r.linear[2]);
    r.linear[3]=r.linear[0];
    for(i=4;i<7;i++)r.linear[i]=hi(r.linear[i],r.linear[i-1]);
    {
        float ratio=div32((float)r.linear[2],(float)r.linear[0]);
        r.pred_gain=r.pred_gain<ratio?r.pred_gain:ratio;
    }
    *out=r;
    return 0;
}
int e003i_internal_cap_preview_observed(const uint64_t linear[7],float pred_gain,
                                      struct e003i_cap_output *out){
    struct e003i_cap_input in;
    unsigned i;
    if(!linear || !out)return -1;
    /* Do not invent the missing bank9:data10 branch input. All 18 DM samples
     * and DB G1..G4 bypass this prelude independently of that value. */
    if(linear[2]>E003I_PREVIEW_CAP_MAX && linear[0]<E003I_PREVIEW_CAP_MAX &&
       linear[0]<linear[2])return -2;
    memset(&in,0,sizeof(in));
    memcpy(in.linear,linear,sizeof(in.linear));
    for(i=0;i<7;i++){in.minimum[i]=E003I_PREVIEW_CAP_MIN;in.maximum[i]=E003I_PREVIEW_CAP_MAX;}
    in.pred_gain=pred_gain;
    in.compact_98=0.0f; /* DM ordinary compact field, all 18 observations. */
    in.snap_steps=0.5f; /* BO global aecxconvergence +0x2c. */
    return e003i_internal_cap(&in,out);
}
