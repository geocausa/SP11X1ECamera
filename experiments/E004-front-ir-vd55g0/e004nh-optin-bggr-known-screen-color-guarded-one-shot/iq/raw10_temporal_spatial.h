/* SPDX-License-Identifier: MIT
 * Offline-only RAW10 two-frame aggregate for front/rear visible Bayer.
 * No device IO, pixels, tile arrays, user images or black level inferred.
 * Temporal difference can contain scene/camera motion and flicker; even a
 * perfectly static spatial pattern may be optical detail OR sensor FPN.
 */
#ifndef SP11_RGB_RAW10_TEMPORAL_SPATIAL_H
#define SP11_RGB_RAW10_TEMPORAL_SPATIAL_H
#include "raw10_profile.h"
#include <math.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

enum { SP11_TEMPORAL_TILE_Y=12, SP11_TEMPORAL_TILE_X=16,
       SP11_TEMPORAL_TILES=SP11_TEMPORAL_TILE_Y*SP11_TEMPORAL_TILE_X };
struct sp11_raw10_temporal_spatial {
    uint64_t paired_green_blocks;
    double frame_a_green_mean,frame_b_green_mean;
    double frame_a_sample_green_std,frame_b_sample_green_std;
    double frame_a_tile_means_std,frame_b_tile_means_std;
    double tile_means_pearson_correlation;
    double paired_mean_delta,paired_abs_delta_mean,paired_delta_rms;
    double tile_delta_rms;
    int both_frames_are_exact_expected_visible_bayer_format;
    int scene_motion_or_flicker_excluded;
    int calibrated_black_or_scene_recognition_proven;
};

static inline int sp11_raw10_temporal_spatial(
    const uint8_t *a,size_t a_bytes,const uint8_t *b,size_t b_bytes,
    size_t stride,size_t width,size_t height,
    enum sp11_rgb_bayer phase,size_t block_step,
    struct sp11_raw10_temporal_spatial *out)
{
    const int front=(width==3840u&&height==2160u&&stride==4800u&&phase==SP11_RGB_RGGB);
    const int rear=(width==4076u&&height==2806u&&stride==5104u&&phase==SP11_RGB_GRBG);
    if (!a||!b||a==b||!out||(!front&&!rear)||
        block_step<1u||block_step>32u||
        height>SIZE_MAX/stride||a_bytes<height*stride||b_bytes<height*stride)
        return -1;
    memset(out,0,sizeof(*out));
    double at[SP11_TEMPORAL_TILES]={0},bt[SP11_TEMPORAL_TILES]={0};
    uint64_t count[SP11_TEMPORAL_TILES]={0};
    double sa=0,sb=0,saa=0,sbb=0,sd=0,sad=0,sdd=0;
    const size_t skip=2u*block_step;
    for(size_t y=0;y+1u<height;y+=skip) {
        const uint8_t *a0=a+y*stride,*a1=a0+stride;
        const uint8_t *b0=b+y*stride,*b1=b0+stride;
        const size_t ty=y*SP11_TEMPORAL_TILE_Y/height;
        for(size_t x=0;x+1u<width;x+=skip) {
            uint16_t ag0,ag1,bg0,bg1;
            const size_t x0=front?x+1u:x;
            const size_t x1=front?x:x+1u;
            if(sp11_raw10_pixel(a0,stride,width,x0,&ag0) ||
               sp11_raw10_pixel(a1,stride,width,x1,&ag1) ||
               sp11_raw10_pixel(b0,stride,width,x0,&bg0) ||
               sp11_raw10_pixel(b1,stride,width,x1,&bg1))
                return -1;
            /* Average both separate green Bayer sites without silently
               dropping either or truncating RAW10 to eight bits. */
            const double av=((double)ag0+(double)ag1)*0.5;
            const double bv=((double)bg0+(double)bg1)*0.5;
            const double delta=bv-av;
            const size_t tx=x*SP11_TEMPORAL_TILE_X/width;
            const size_t i=ty*SP11_TEMPORAL_TILE_X+tx;
            if(i>=SP11_TEMPORAL_TILES) return -1;
            at[i]+=av;bt[i]+=bv;count[i]++;
            sa+=av;sb+=bv;saa+=av*av;sbb+=bv*bv;
            sd+=delta;sad+=fabs(delta);sdd+=delta*delta;
            out->paired_green_blocks++;
        }
    }
    const double n=(double)out->paired_green_blocks;
    if (n<1000.) return -1;
    out->frame_a_green_mean=sa/n;
    out->frame_b_green_mean=sb/n;
    out->frame_a_sample_green_std=sqrt(fmax(0.,saa/n-(sa/n)*(sa/n)));
    out->frame_b_sample_green_std=sqrt(fmax(0.,sbb/n-(sb/n)*(sb/n)));
    out->paired_mean_delta=sd/n;
    out->paired_abs_delta_mean=sad/n;
    out->paired_delta_rms=sqrt(sdd/n);
    double ma=0,mb,ma2=0,mb2=0,ab=0,dd=0;
    mb=0;
    for(size_t i=0;i<SP11_TEMPORAL_TILES;i++) {
        if(count[i]==0u) return -1;
        at[i]/=(double)count[i];bt[i]/=(double)count[i];
        ma+=at[i];mb+=bt[i];
        ma2+=at[i]*at[i];mb2+=bt[i]*bt[i];ab+=at[i]*bt[i];
        const double delta=bt[i]-at[i];dd+=delta*delta;
    }
    const double tiles=(double)SP11_TEMPORAL_TILES;
    ma/=tiles;mb/=tiles;
    const double va=fmax(0.,ma2/tiles-ma*ma);
    const double vb=fmax(0.,mb2/tiles-mb*mb);
    out->frame_a_tile_means_std=sqrt(va);
    out->frame_b_tile_means_std=sqrt(vb);
    out->tile_delta_rms=sqrt(dd/tiles);
    out->tile_means_pearson_correlation=(va>1.e-12&&vb>1.e-12)?
        fmax(-1.,fmin(1.,(ab/tiles-ma*mb)/sqrt(va*vb))):0.;
    out->both_frames_are_exact_expected_visible_bayer_format=1;
    out->scene_motion_or_flicker_excluded=0;
    out->calibrated_black_or_scene_recognition_proven=0;
    return 0;
}
#endif
