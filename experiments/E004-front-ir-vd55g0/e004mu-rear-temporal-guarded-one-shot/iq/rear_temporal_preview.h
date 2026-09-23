/* SPDX-License-Identifier: MIT
 * Default-OFF rear-only, single-previous-frame 4K NV12 Y temporal trial.
 *
 * Strictly display-domain. This is NOT real optical SNR, Windows ISP, AE,
 * calibrated black, recognized details, true motion segmentation or release
 * approval. The independent preview tone is a SEPARATE opt-in prerequisite.
 * Never used by normal maintained publisher, front camera or protected Golden.
 * Only caller-owned heap for *one* previous filtered Y plane; no RAW, files,
 * image hashes, UV writes, frame queue or off-device optical data.
 */
#ifndef SP11_REAR_TEMPORAL_PREVIEW_H
#define SP11_REAR_TEMPORAL_PREVIEW_H
#include "rear_preview_tone.h"
#include <math.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

struct sp11_rear_temporal_state {
    uint8_t *last_y;
    size_t capacity;
    uint32_t last_sequence;
    double last_ms;
    unsigned last_median;
    unsigned last_profile;
    int valid;
};
struct sp11_rear_temporal_stats {
    int filtered, initialized, reset_scene, reset_sequence, reset_tone;
    uint64_t blocks_filtered, blocks_bypassed, pixels_changed;
    unsigned current_median;
    double sampled_global_abs_delta, sampled_high_motion_fraction;
    double sampled_input_delta_RMS_vs_prior_filtered;
    double sampled_output_delta_RMS_vs_prior_filtered;
    uint64_t sampled_temporal_sites;
    int uv_unchanged, optical_detail_or_motion_proven;
};
/* Caller owns a private, unique whole-4K-Y buffer and frees/clears it.
 * This primitive never allocates or persists pixels and never delays frames.
 */
static inline int sp11_rear_temporal_init(struct sp11_rear_temporal_state *s,
    uint8_t *private_heap,size_t capacity)
{
    if(!s||!private_heap||capacity!=SP11_REAR_PREVIEW_Y) return -1;
    memset(s,0,sizeof(*s));
    s->last_y=private_heap;
    s->capacity=capacity;
    return 0;
}
static inline void sp11_rear_temporal_reset(struct sp11_rear_temporal_state *s)
{
    if(s&&s->last_y&&s->capacity==SP11_REAR_PREVIEW_Y) {
        memset(s->last_y,0,SP11_REAR_PREVIEW_Y);
        s->valid=0;s->last_sequence=0;s->last_ms=0.;
        s->last_median=0;s->last_profile=0;
    }
}
/* profile is a caller-selected opt-in epoch, NOT a sensor-register readback.
 * Timestamp is from the real source monotonic clock, never wall clock.
 * Sequence and timestamp discontinuities discard all old pixel history.
 * The guard compares prior FILTERED Y with current tone-mapped Y, so both
 * must be comparable and the tone gate must remain explicitly active.
 */
static inline int sp11_rear_temporal_nv12(uint8_t *nv12,size_t bytes,
    int width,int height,int tone_applied,
    uint32_t sequence,double source_ms,unsigned profile,
    struct sp11_rear_temporal_state *s,
    struct sp11_rear_temporal_stats *out)
{
    if(!nv12||!s||!out||!s->last_y||
       s->capacity!=SP11_REAR_PREVIEW_Y||
       width!=SP11_REAR_PREVIEW_W||height!=SP11_REAR_PREVIEW_H||
       bytes!=SP11_REAR_PREVIEW_Y*3u/2u ||
       !isfinite(source_ms)||source_ms<=0.||profile==0u)
        return -1;
    memset(out,0,sizeof(*out));out->uv_unchanged=1;
    if(tone_applied!=1) {
        sp11_rear_temporal_reset(s);
        out->reset_tone=1;
        return 0;
    }
    uint32_t hist[256]={0};
    uint64_t abs_total=0,high_delta=0,nsample=0;
    for(int y=0;y<height;y+=32)
        for(int x=0;x<width;x+=32) {
            const size_t pos=(size_t)y*width+x;
            const unsigned v=nv12[pos];
            hist[v]++;nsample++;
            if(s->valid) {
                const unsigned old=s->last_y[pos];
                const unsigned d=v>old?v-old:old-v;
                abs_total+=d;high_delta+=(d>18u);
            }
        }
    if(nsample<1000u) return -1;
    const unsigned median=sp11_tone_percentile(hist,(size_t)nsample,50u);
    out->current_median=median;
    if(s->valid) {
        out->sampled_global_abs_delta=(double)abs_total/(double)nsample;
        out->sampled_high_motion_fraction=(double)high_delta/(double)nsample;
        if(sequence!=s->last_sequence+1u ||
           source_ms<=s->last_ms || source_ms-s->last_ms>100.) {
            sp11_rear_temporal_reset(s);out->reset_sequence=1;
        } else if(profile!=s->last_profile ||
                  (median>s->last_median?median-s->last_median:
                                           s->last_median-median)>12u ||
                  out->sampled_global_abs_delta>12. ||
                  out->sampled_high_motion_fraction>0.20) {
            sp11_rear_temporal_reset(s);out->reset_scene=1;
        }
    }
    if(!s->valid) {
        memcpy(s->last_y,nv12,SP11_REAR_PREVIEW_Y);
        s->valid=1;s->last_sequence=sequence;s->last_ms=source_ms;
        s->last_median=median;s->last_profile=profile;
        out->initialized=1;
        return 0;
    }
    /* A 2x2 motion/noise gate prevents *whole blocks* near a moving,
     * high-contrast edge from mixing old pixels into newly visible areas.
     * Low-contrast motion may still ghost: do not describe as motion-safe.
     * For stable blocks 50:50 IIR of current and *one stored prior
     * filtered* frame; no additional raw source frames or latency.
     */
    uint64_t current_delta2=0,output_delta2=0,temporal_samples=0;
    for(int y=0;y<height;y+=2)
        for(int x=0;x<width;x+=2) {
            const size_t p=(size_t)y*width+x;
            const size_t positions[4]={p,p+1,p+(size_t)width,p+(size_t)width+1};
            unsigned maxdelta=0;
            for(int k=0;k<4;k++) {
                const unsigned a=nv12[positions[k]];
                const unsigned b=s->last_y[positions[k]];
                const unsigned d=a>b?a-b:b-a;
                if(d>maxdelta)maxdelta=d;
            }
            /* Scalar-only same-coordinate before/after filter delta
             * relative to ONE previous FILTERED output frame. The
             * independent candidate also measures previous UNFILTERED
             * Y separately; do not represent this paired history
             * comparator as physical scene or noise ground truth. */
            const int sampled=((x&31)==0 && (y&31)==0);
            const int before_difference=(int)nv12[p]-(int)s->last_y[p];
            unsigned after=(unsigned)nv12[p];
            if(maxdelta<=8u)
                after=(after+(unsigned)s->last_y[p]+1u)/2u;
            const int after_difference=(int)after-(int)s->last_y[p];
            if(sampled) {
                current_delta2+=(uint64_t)(before_difference*before_difference);
                output_delta2+=(uint64_t)(after_difference*after_difference);
                temporal_samples++;
            }
            if(maxdelta>8u) {
                for(int k=0;k<4;k++) s->last_y[positions[k]]=nv12[positions[k]];
                out->blocks_bypassed++;
            } else {
                for(int k=0;k<4;k++) {
                    const size_t i=positions[k];const unsigned current=nv12[i];
                    const unsigned average=(current+(unsigned)s->last_y[i]+1u)/2u;
                    out->pixels_changed+=(average!=current);
                    nv12[i]=s->last_y[i]=(uint8_t)average;
                }
                out->blocks_filtered++;
            }
        }
    if(temporal_samples<1000u) return -1;
    out->sampled_temporal_sites=temporal_samples;
    out->sampled_input_delta_RMS_vs_prior_filtered=
         sqrt((double)current_delta2/(double)temporal_samples);
    out->sampled_output_delta_RMS_vs_prior_filtered=
         sqrt((double)output_delta2/(double)temporal_samples);
    s->last_sequence=sequence;s->last_ms=source_ms;
    s->last_median=median;s->last_profile=profile;
    out->filtered=1;
    return 0;
}
#endif
