// SPDX-License-Identifier: GPL-2.0-only
#include "native-convergence.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
#include <float.h>


#define E003I_CONV_MAX_STRETCH 16

struct e003i_conv_history {
    uint64_t lanes[E003I_CONV_LANES];
    float drc_gain;
    float previous_delta;
};

/* Generic Windows-stage carrier is private in BP. Callers cannot select or
 * override these tuning fields; e003i_converge_front_preview_unlocked_zero_delta_history() fills them from
 * the BM/BN/BO normal-preview proof. */
struct e003i_stretch_record {
    float weight;
    float offset;
    float comp;
    float temp_weight;
    uint32_t negative;
};

struct e003i_conv_input {
    double target_log[E003I_CONV_LANES];
    struct e003i_conv_history history1;
    struct e003i_conv_history history2;
    struct e003i_conv_history delayed_history;

    uint32_t pipeline_delay;
    float base_speed;
    float base_capping;
    float drc_speed;
    int32_t capping_type;
    int32_t tolerance_steps;
    float minimum_step;
    uint32_t intolerance_gate;
    uint32_t small_delta_exemption;

    struct e003i_stretch_record stretch[E003I_CONV_MAX_STRETCH];
    uint32_t stretch_capacity;
    uint32_t stretch_active_count;
    uint32_t stretch_agg_type;
    uint32_t stretch_direction_mode;
    uint32_t stretch_target_negative;

    int32_t state_flag_short;
    int32_t state_flag_long;
    int32_t drc_policy;
};

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}
__attribute__((noinline)) static float fadd32(float a,float b){ volatile float r=a+b; return r; }
__attribute__((noinline)) static float fsub32(float a,float b){ volatile float r=a-b; return r; }
__attribute__((noinline)) static float fmul32(float a,float b){ volatile float r=a*b; return r; }
__attribute__((noinline)) static float fdiv32(float a,float b){ volatile float r=a/b; return r; }

static const float k_one03 = 1.0299999713897705078125f;
static const double k_pow_base = 1.0299999713897705078125;

/* BJ recovered this exact Windows shared log10 scale. */
static float log103_float(float x)
{
    const float scale=f32bits(0x429bcc0cU);
    if (!(x > 0.0f))
        return 0.0f;
    return (float)(log10((double)x) * (double)scale);
}
static double log103_linear_u64(uint64_t exposure)
{
    /* Convergence history is absolute log1.03(linear exposure), not the
     * T681-relative coordinate used by Algorithm001/BJ. Windows first
     * rounds the uint64 exposure to float32, then applies the shared log scale. */
    float x=(float)exposure;
    if (!(x > 0.0f)) return 0.0;
    return (double)log103_float(x);
}
static float pow103_float(float x)
{
    return (float)pow((double)k_one03,(double)x);
}
static float frinta32(float x)
{
    x=(float)x;
    return x >= 0.0f ? (float)floor((double)x+0.5) : (float)ceil((double)x-0.5);
}

int e003i_stretch_materialize(int stretch_type, float weight, float raw,
                              float comp, float temp_weight,
                              struct e003i_stretch_record *out)
{
    const float eps=f32bits(0x33d6bf95U);
    float off;
    if (!out) return -1;
    if (stretch_type==0) {
        if (fabsf(raw) < eps) off=0.0f;
        else {
            if (!(raw > 0.0f)) return -2;
            off=log103_float(raw);
        }
    } else off=raw;
    out->weight=weight; out->offset=off; out->comp=comp; out->temp_weight=temp_weight;
    out->negative=off < 0.0f;
    return 0;
}

static uint32_t slot(uint32_t head,uint32_t rel,uint32_t cap)
{
    return (uint32_t)(head+rel)%cap;
}
static int aggregate_stretch(const struct e003i_conv_input *in,
                             struct e003i_stretch_record *o)
{
    struct e003i_stretch_record ring[E003I_CONV_MAX_STRETCH];
    uint32_t cap=in->stretch_capacity, n=in->stretch_active_count, mode=in->stretch_agg_type;
    uint32_t i,j, selected=UINT32_MAX;
    if (!cap || cap>E003I_CONV_MAX_STRETCH || n>cap || mode>=5) return -1;
    memcpy(ring,in->stretch,sizeof(ring));
    memset(o,0,sizeof(*o));

    if (mode==0) {
        float tw=0,so=0,comp=0,temp=0;
        for(i=0;i<n;i++) {
            const struct e003i_stretch_record *r=&ring[slot(0,i,cap)];
            int accept=in->stretch_direction_mode==0 ||
                (in->stretch_direction_mode==1 && r->negative==(in->stretch_target_negative?1U:0U));
            if(!accept) continue;
            tw=fadd32(tw,r->weight); so=fadd32(so,fmul32(r->offset,r->weight));
            comp=fadd32(comp,fmul32(r->comp,r->weight)); temp=fadd32(temp,fmul32(r->temp_weight,r->weight));
        }
        if(tw>0){so=fdiv32(so,tw);comp=fdiv32(comp,tw);temp=fdiv32(temp,tw);} else so=comp=temp=0;
        o->offset=so;o->comp=comp;o->temp_weight=temp;return 0;
    }

    for(i=0;i+1<n;i++) for(j=0;j+1<n-i;j++) {
        struct e003i_stretch_record *a=&ring[j],*b=&ring[j+1];
        float ka=(mode==3||mode==4)?a->weight:a->offset;
        float kb=(mode==3||mode==4)?b->weight:b->offset;
        if(ka>kb){struct e003i_stretch_record t=*a;*a=*b;*b=t;}
    }
    if(mode==3 && n) {
        if(in->stretch_direction_mode==0 || ring[0].negative==(in->stretch_target_negative?1U:0U)) selected=0;
    } else if(mode==4 && n) {
        uint32_t r=n-1;
        if(in->stretch_direction_mode==0 || ring[r].negative==(in->stretch_target_negative?1U:0U)) selected=r;
    } else {
        uint32_t firstpos=UINT32_MAX;
        for(i=0;i<n;i++) if(ring[i].offset>0){firstpos=i;break;}
        if(mode==1) {
            if(!in->stretch_target_negative) selected=firstpos;
            else if(n && ring[0].offset<0 && firstpos!=UINT32_MAX && firstpos>0) selected=firstpos-1;
        } else if(mode==2) {
            if(!in->stretch_target_negative) {
                if(n && ring[n-1].offset>0) selected=n-1;
            } else if(n && ring[0].offset<=0) selected=0;
        }
    }
    if(selected==UINT32_MAX){o->comp=1.0f;o->temp_weight=0.5f;return 0;}
    *o=ring[selected]; return 0;
}

static int basic_safe(const struct e003i_conv_input *in,double *out,uint32_t *direction_ok)
{
    const float eps=f32bits(0x33d6bf95U), tolguard=f32bits(0x3f800001U);
    double target=in->target_log[E003I_LANE_SAFE];
    double prev=log103_linear_u64(in->history1.lanes[E003I_LANE_SAFE]);
    double prev2=log103_linear_u64(in->history2.lanes[E003I_LANE_SAFE]);
    double delayed=log103_linear_u64(in->delayed_history.lanes[E003I_LANE_SAFE]);
    double T=target-prev, D=target-delayed, M=prev-prev2;
    double candidate=(double)in->base_speed*T, cap, step, applied;
    float pd=in->history1.previous_delta;
    if(!in->pipeline_delay) return -1;
    *direction_ok=(M*T)>=0.0;
    if(fabs(T)<(double)in->tolerance_steps && in->intolerance_gate && fabsf(pd)<=0.0f){*out=prev;return 0;}
    if(in->capping_type==0) cap=(double)in->base_capping*D;
    else if(in->capping_type==1) cap=(T<0?-1.0:1.0)*(double)in->base_capping;
    else cap=D/(double)in->pipeline_delay;
    step=fabs(candidate)>fabs(cap)?cap:candidate;
    {
        float diff=fabsf((float)((float)step-(float)pd));
        if(diff>=eps && (float)in->tolerance_steps<tolguard &&
           fabs(target-(step+prev))<(double)in->tolerance_steps) step=T;
    }
    if(fabs(step)<(double)in->minimum_step && fabs(T)>(double)in->minimum_step) {
        float diff=fabsf((float)((float)step-(float)pd));
        int match=diff<eps;
        if(!(in->small_delta_exemption && match)) step=step>0?(double)in->minimum_step:-(double)in->minimum_step;
    }
    applied=*direction_ok?step:0.0;
    *out=prev+applied; return 0;
}

static int stretch_apply(const struct e003i_conv_input *in,double basic,
                         double lanes[7],float *pred,float *shorts,float *safes)
{
    struct e003i_stretch_record a;
    float filtered,q,sh,pg,lg,ss,one_step;
    unsigned i;
    if(aggregate_stretch(in,&a)) return -1;
    filtered=fadd32(fmul32(fsub32(1.0f,a.temp_weight),in->history1.previous_delta),
                    fmul32(a.temp_weight,a.offset));
    one_step=log103_float(k_one03);
    if(fabsf(filtered)<one_step) sh=0.0f;
    else {
        q=in->minimum_step;
        if(!(q>0.0f && q<=1.0f)) q=0.5f;
        sh=fmul32(frinta32(fdiv32(filtered,q)),q);
    }
    pg=1.0f;
    if(sh<0.0f) pg=pow103_float(fmul32(fabsf(sh),a.comp));
    lg=log103_float(pg); ss=fadd32(sh,lg);
    for(i=0;i<7;i++) lanes[i]=basic;
    lanes[E003I_LANE_SHORT]=basic+(double)sh;
    lanes[E003I_LANE_SAFE]=basic+(double)ss;
    lanes[E003I_LANE_LONG]=basic;
    *pred=pg;*shorts=sh;*safes=ss;return 0;
}

static double adjusted_history_lane(const struct e003i_conv_history *h,int t)
{
    double x=log103_linear_u64(h->lanes[t]);
    if(t==0 && h->drc_gain>1.0f) x+=(double)log103_float(h->drc_gain);
    return x;
}
static double get_exposure_info(const struct e003i_conv_input *in,int t,double drc_safe)
{
    const double rel_eps=*(const double *)(const unsigned char[]){0x00,0x00,0x00,0xa0,0xf2,0xd7,0x7a,0x3e};
    const float tolguard=f32bits(0x3f800001U);
    double h1lane=adjusted_history_lane(&in->history1,t), h2lane=adjusted_history_lane(&in->history2,t);
    double h1safe=log103_linear_u64(in->history1.lanes[E003I_LANE_SAFE]);
    double targetlane=in->target_log[t], targetsafe=in->target_log[E003I_LANE_SAFE];
    double targetrel=targetsafe-targetlane, histrel=h1safe-h1lane, relerr=targetrel-histrel;
    double hm=h1lane-h2lane, tm=targetlane-h1lane, candidate=drc_safe-histrel;
    int state=t==0?in->state_flag_short:in->state_flag_long;
    int force=fabs(targetlane-h1lane)<(double)in->tolerance_steps && state==1;
    if(!force && hm*tm>=0.0 && fabs(relerr)>=rel_eps) {
        double step=(double)in->drc_speed*relerr;
        if(fabs(step)<(double)in->minimum_step) step=step>0?(double)in->minimum_step:-(double)in->minimum_step;
        candidate=drc_safe-(histrel+step);
    }
    if(fabs(candidate-targetlane)<(double)in->tolerance_steps && (float)in->tolerance_steps<tolguard) candidate=targetlane;
    if((candidate-h1lane)*(targetlane-h1lane)<0.0) candidate=h1lane;
    if(targetlane-h1lane>0) candidate=fmin(candidate,targetlane); else candidate=fmax(candidate,targetlane);
    {
        double lim=fmax(fabs(targetrel),fabs(histrel));
        if(fabs(drc_safe-candidate)>lim) candidate=drc_safe+(candidate>drc_safe?lim:-lim);
    }
    return candidate;
}

enum { DRC_NORMAL_PRED=1, DRC_USE_DRC=2, DRC_GREATER=3, DRC_ADJ_PG=4, DRC_PG_UNITY=5, DRC_CASCADE=6, DRC_STRETCH_ONLY=7, DRC_INVALID=255 };
static void drc_aggregate(const struct e003i_conv_input *in,const double normal[7],
                          const double drc[7],float *pred,double out[7],
                          float *stretch_ratio,float *drc_ratio,uint32_t *branch)
{
    float stretch=pow103_float((float)(normal[E003I_LANE_SAFE]-normal[E003I_LANE_SHORT]));
    float drcr=pow103_float((float)(normal[E003I_LANE_SAFE]-drc[E003I_LANE_SHORT]));
    float p=*pred; unsigned i;
    memcpy(out,normal,7*sizeof(double)); out[E003I_LANE_LONG]=drc[E003I_LANE_LONG];
    *stretch_ratio=stretch;*drc_ratio=drcr;
    if(stretch<1.0f){*branch=DRC_INVALID;return;}
    if(drcr<=1.0f){*branch=DRC_NORMAL_PRED;return;}
    if(stretch<=1.0f){memcpy(out,drc,7*sizeof(double));*pred=1.0f;*branch=DRC_USE_DRC;return;}
    if(in->drc_policy==0){
        if(drcr>=stretch){memcpy(out,drc,7*sizeof(double));*pred=1.0f;*branch=DRC_GREATER;return;}
        if(drcr<=p){*pred=fdiv32(p,drcr);*branch=DRC_ADJ_PG;return;}
        *pred=1.0f;*branch=DRC_PG_UNITY;return;
    }
    if(in->drc_policy==1){
        float delta=log103_float(stretch);
        memcpy(out,drc,7*sizeof(double));out[E003I_LANE_SHORT]=drc[E003I_LANE_SHORT]-(double)delta;
        *branch=DRC_CASCADE;return;
    }
    if(in->drc_policy==2){*branch=DRC_STRETCH_ONLY;return;}
    for(i=0;i<7;i++) out[i]=normal[i];
    out[E003I_LANE_LONG]=drc[E003I_LANE_LONG];
    *branch=DRC_INVALID;
}

static int converge_single_request(const struct e003i_conv_input *in,
                                   struct e003i_conv_output *out)
{
    double basic,normal[7],drc[7],final[7]; float pred,sh,ss,sr,dr; uint32_t dir,branch; unsigned i;
    if(!in||!out) return -1;
    memset(out,0,sizeof(*out));
    if(!in->history1.lanes[E003I_LANE_SHORT] || !in->history1.lanes[E003I_LANE_LONG] ||
       !in->history1.lanes[E003I_LANE_SAFE] || !in->history2.lanes[E003I_LANE_SHORT] ||
       !in->history2.lanes[E003I_LANE_LONG] || !in->history2.lanes[E003I_LANE_SAFE] ||
       !in->delayed_history.lanes[E003I_LANE_SAFE]) return -2;
    if(basic_safe(in,&basic,&dir)) return -3;
    if(stretch_apply(in,basic,normal,&pred,&sh,&ss)) return -4;
    memcpy(drc,normal,sizeof(drc));
    drc[E003I_LANE_SHORT]=get_exposure_info(in,0,normal[E003I_LANE_SAFE]);
    drc[E003I_LANE_LONG]=get_exposure_info(in,1,normal[E003I_LANE_SAFE]);
    drc_aggregate(in,normal,drc,&pred,final,&sr,&dr,&branch);

    /* activeExposureCount == 1: s1..s4 are all Short before PopulateOutput. */
    for(i=3;i<7;i++) final[i]=final[E003I_LANE_SHORT];
    for(i=0;i<7;i++) {
        double x=pow(k_pow_base,final[i]);
        if(!isfinite(x)||x<0.0||x>(double)UINT64_MAX) return -5;
        out->linear[i]=(uint64_t)x;
        out->post_stretch_log[i]=normal[i]; out->final_log[i]=final[i];
    }
    out->basic_safe_log=basic;out->pred_gain=pred;out->short_stretch=sh;out->safe_stretch=ss;
    out->stretch_ratio=sr;out->drc_ratio=dr;out->basic_direction_ok=dir;out->drc_branch=branch;
    return 0;
}


int e003i_converge_front_preview_unlocked_zero_delta_history(
    const struct e003i_front_preview_unlocked_zero_delta_history_input *in,
    struct e003i_conv_output *out)
{
    struct e003i_conv_input rt;
    if (!in || !out)
        return -1;

    memset(&rt, 0, sizeof(rt));
    memcpy(rt.target_log, in->target_log, sizeof(in->target_log));
    rt.history1.lanes[E003I_LANE_SHORT] = in->history1.short_exposure;
    rt.history1.lanes[E003I_LANE_LONG] = in->history1.long_exposure;
    rt.history1.lanes[E003I_LANE_SAFE] = in->history1.safe_exposure;
    rt.history1.drc_gain = in->history1.drc_gain;
    /* BU: Windows normal-preview recurrence proves this retained field is +0.0f. */
    rt.history1.previous_delta = 0.0f;

    rt.history2.lanes[E003I_LANE_SHORT] = in->history2.short_exposure;
    rt.history2.lanes[E003I_LANE_LONG] = in->history2.long_exposure;
    rt.history2.lanes[E003I_LANE_SAFE] = in->history2.safe_exposure;
    rt.history2.drc_gain = in->history2.drc_gain;

    rt.delayed_history.lanes[E003I_LANE_SAFE] = in->delayed_history.safe_exposure;

    /* BM + BN + BO: exact normal Windows front-preview profile. */
    rt.pipeline_delay = 3;
    rt.base_speed = f32bits(0x3f4ccccdU);   /* 0.8f */
    rt.base_capping = f32bits(0x3ea8f5c3U); /* 0.33f */
    rt.drc_speed = f32bits(0x3e19999aU);    /* 0.15f */
    rt.capping_type = 2;
    rt.tolerance_steps = 2;
    rt.minimum_step = f32bits(0x3f000000U); /* 0.5f */
    rt.drc_policy = 0;

    /* BM DisableStretch: stretchType=0, factor=1 -> offset 0, while
     * tempWeight=1 selects that zero instead of the retained previous delta. */
    rt.stretch_capacity = 1;
    rt.stretch_active_count = 1;
    rt.stretch_agg_type = 0;
    rt.stretch_direction_mode = 0;
    rt.stretch_target_negative = 0;
    rt.stretch[0].weight = 1.0f;
    rt.stretch[0].offset = 0.0f;
    rt.stretch[0].comp = 1.0f;
    rt.stretch[0].temp_weight = 1.0f;
    rt.stretch[0].negative = 0;

    /* BQ: ordinary normal-streaming + AEC-unlocked + temporary
     * metering-lock-context-inactive projection. These are runtime state,
     * not tuning, and are deliberately zero only for this scoped wrapper. */
    rt.intolerance_gate = 0;
    rt.small_delta_exemption = 0;
    rt.state_flag_short = 0;
    rt.state_flag_long = 0;

    return converge_single_request(&rt, out);
}
