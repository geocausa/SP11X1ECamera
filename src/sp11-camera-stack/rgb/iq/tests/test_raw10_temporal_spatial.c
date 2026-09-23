/* Camera-free sparse synthetic Bayer frames, absolutely no optical pixels. */
#include "../raw10_temporal_spatial.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static void pack(uint8_t *row,size_t x,uint16_t v)
{
    const size_t g=(x/4u)*5u;
    const unsigned shift=(unsigned)(x&3u)*2u;
    row[g+(x&3u)]=(uint8_t)(v>>2u);
    row[g+4u]=(uint8_t)((row[g+4u]&~(3u<<shift))|((v&3u)<<shift));
}
static void fill(uint8_t *p,size_t w,size_t h,size_t stride,
                 enum sp11_rgb_bayer phase,int checker_delta,int patterned)
{
    const size_t skip=32u;
    for(size_t y=0;y+1u<h;y+=skip) {
        for(size_t x=0;x+1u<w;x+=skip) {
            const size_t tx=x*SP11_TEMPORAL_TILE_X/w;
            const size_t ty=y*SP11_TEMPORAL_TILE_Y/h;
            const int spatial=patterned?(int)(3u*tx+2u*ty):0;
            const int variation=checker_delta?(((x/skip+y/skip)&1u)?checker_delta:-checker_delta):0;
            const uint16_t value=(uint16_t)(64+spatial+variation);
            const size_t a=phase==SP11_RGB_RGGB?x+1u:x;
            const size_t b=phase==SP11_RGB_RGGB?x:x+1u;
            pack(p+y*stride,a,value);
            pack(p+(y+1u)*stride,b,value);
        }
    }
}
static void test_mode(size_t w,size_t h,size_t stride,
                      enum sp11_rgb_bayer phase)
{
    const size_t bytes=h*stride;
    uint8_t *a=calloc(bytes,1u),*b=calloc(bytes,1u);
    assert(a&&b);
    struct sp11_raw10_temporal_spatial x;
    fill(a,w,h,stride,phase,0,0);
    fill(b,w,h,stride,phase,0,0);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes,stride,w,h,phase,16u,&x)==0);
    assert(x.paired_green_blocks>1000u);
    assert(x.frame_a_green_mean==64.&&x.frame_b_green_mean==64.);
    assert(x.frame_a_tile_means_std==0.&&x.frame_b_tile_means_std==0.);
    assert(x.paired_delta_rms==0.&&x.tile_means_pearson_correlation==0.);
    assert(x.both_frames_are_exact_expected_visible_bayer_format==1);
    assert(!x.scene_motion_or_flicker_excluded);
    assert(!x.calibrated_black_or_scene_recognition_proven);

    fill(a,w,h,stride,phase,0,1);
    fill(b,w,h,stride,phase,0,1);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes,stride,w,h,phase,16u,&x)==0);
    assert(x.frame_a_tile_means_std>5.);
    assert(x.frame_b_tile_means_std>5.);
    assert(fabs(x.tile_means_pearson_correlation-1.)<1.e-9);
    assert(x.paired_delta_rms==0.);
    /* Repeatable spatial pattern might be synthetic fixed-pattern noise:
       a correlation of 1 must NEVER promote it to recognizable scene. */
    assert(!x.calibrated_black_or_scene_recognition_proven);

    fill(b,w,h,stride,phase,8,1);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes,stride,w,h,phase,16u,&x)==0);
    assert(x.paired_delta_rms==8.);
    assert(x.paired_abs_delta_mean==8.);
    assert(x.frame_b_sample_green_std>x.frame_a_sample_green_std);
    assert(!x.scene_motion_or_flicker_excluded);
    assert(!x.calibrated_black_or_scene_recognition_proven);

    assert(sp11_raw10_temporal_spatial(a,bytes,a,bytes,stride,w,h,phase,16u,&x)==-1);
    assert(sp11_raw10_temporal_spatial(a,bytes-1,b,bytes,stride,w,h,phase,16u,&x)==-1);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes-1,stride,w,h,phase,16u,&x)==-1);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes,stride,w,h,phase,33u,&x)==-1);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes,stride,w,h,
             phase==SP11_RGB_GRBG?SP11_RGB_RGGB:SP11_RGB_GRBG,16u,&x)==-1);
    assert(sp11_raw10_temporal_spatial(a,bytes,b,bytes,stride,w,h,phase,16u,NULL)==-1);
    free(a);free(b);
}
int main(void)
{
    test_mode(3840u,2160u,4800u,SP11_RGB_RGGB);
    test_mode(4076u,2806u,5104u,SP11_RGB_GRBG);
    puts("RGB_RAW10_TEMPORAL_SPATIAL_CAMERA_FREE_TEST=PASS FRONT_REAR_CONSTANT_PATTERN_JITTER_BOUNDS");
    return 0;
}
