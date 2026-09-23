/* SPDX-License-Identifier: MIT
 * Rear RGB trial-only bounded NV12 VIDEO-RANGE luminance preview curve.
 * Pure in-memory output transformation: NOT sensor AE, color-calibrated ISP,
 * scene recognition, measured black level or approved production rendering.
 * A sparse histogram gates amplification of almost-uniform rear scenes.
 * NEVER enabled by normal maintained camera builds, camera-free tests only.
 */
#ifndef SP11_REAR_PREVIEW_TONE_H
#define SP11_REAR_PREVIEW_TONE_H
#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum { SP11_REAR_PREVIEW_W=3840,SP11_REAR_PREVIEW_H=2160,
       SP11_REAR_PREVIEW_Y=SP11_REAR_PREVIEW_W*SP11_REAR_PREVIEW_H };
struct sp11_rear_preview_tone_result {
    int applied;
    unsigned input_p01,input_p50,input_p99;
    unsigned output_p01_estimate,output_p50_estimate,output_p99_estimate;
    size_t sampled;
    unsigned char unchanged_chroma;
    unsigned char black_reference_calibrated;
    unsigned char real_scene_detail_verified;
};
static inline unsigned sp11_tone_percentile(const uint32_t *h,size_t n,unsigned q)
{
    size_t rank=(n*q+99u)/100u,seen=0;
    if(!rank) rank=1;
    for(unsigned i=0;i<256;i++) {
        seen+=h[i];if(seen>=rank) return i;
    }
    return 255u;
}
static inline unsigned char sp11_tone_map_y(unsigned y,unsigned low)
{
    /* p01 maps to 125, gain 7/2. Clip to legal video Y. */
    int v=125+((int)y-(int)low)*7/2;
    if(v<16) v=16;
    if(v>235) v=235;
    return (unsigned char)v;
}
static inline int sp11_rear_trial_tone_nv12(unsigned char *nv12,size_t bytes,
                                    int width,int height,
                                    struct sp11_rear_preview_tone_result *result)
{
    if(!result||!nv12||width!=SP11_REAR_PREVIEW_W||
       height!=SP11_REAR_PREVIEW_H||bytes!=SP11_REAR_PREVIEW_Y*3u/2u)
        return -1;
    memset(result,0,sizeof(*result));
    uint32_t hist[256]={0};
    size_t count=0;
    for(int y=0;y<height;y+=16)
        for(int x=0;x<width;x+=16) {
            hist[nv12[(size_t)y*width+x]]++;
            count++;
        }
    if(count<1000) return -1;
    const unsigned p01=sp11_tone_percentile(hist,count,1u);
    const unsigned p50=sp11_tone_percentile(hist,count,50u);
    const unsigned p99=sp11_tone_percentile(hist,count,99u);
    result->input_p01=p01;result->input_p50=p50;result->input_p99=p99;
    result->sampled=count;result->unchanged_chroma=1;
    result->output_p01_estimate=p01;
    result->output_p50_estimate=p50;
    result->output_p99_estimate=p99;
    /* Deliberately do NOT lift an almost uniform/dark/no-signal frame,
       nor transform an already bright or unsupported scene. A p99/p01
       difference is a spatial spread, NOT proof of scene/noise quality. */
    if(p01<20u||p01>50u||p99>65u||p99-p01<8u) return 0;
    unsigned char lut[256];
    for(unsigned v=0;v<256u;v++)lut[v]=sp11_tone_map_y(v,p01);
    for(size_t i=0;i<SP11_REAR_PREVIEW_Y;i++)nv12[i]=lut[nv12[i]];
    result->applied=1;
    result->output_p01_estimate=lut[p01];
    result->output_p50_estimate=lut[p50];
    result->output_p99_estimate=lut[p99];
    return 0;
}
#endif
