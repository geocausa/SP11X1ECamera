/* Synthetic ONLY: camera-free NV12 rear 4K brightness experiment. */
#include "../rear_preview_tone.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char *make(unsigned v)
{
    unsigned char *b=malloc(SP11_REAR_PREVIEW_Y*3u/2u);
    assert(b);
    memset(b,(int)v,SP11_REAR_PREVIEW_Y);
    memset(b+SP11_REAR_PREVIEW_Y,128,SP11_REAR_PREVIEW_Y/2u);
    return b;
}
static void test(void)
{
    const size_t n=SP11_REAR_PREVIEW_Y*3u/2u;
    struct sp11_rear_preview_tone_result m;
    unsigned char *b=make(30);
    for(size_t i=0;i<SP11_REAR_PREVIEW_Y;i+=2u)b[i]=31;
    for(int y=0;y<2160;y+=16)for(int x=0;x<3840;x+=32)
        b[(size_t)y*3840+x]=30;
    assert(sp11_rear_trial_tone_nv12(b,n,3840,2160,&m)==0);
    assert(!m.applied && m.input_p01==30 && m.input_p99==31);
    assert(b[0]==30 && b[1]==30 && b[SP11_REAR_PREVIEW_Y]==128);
    memset(b,128,SP11_REAR_PREVIEW_Y);
    assert(sp11_rear_trial_tone_nv12(b,n,3840,2160,&m)==0);
    assert(!m.applied && b[100]==128);
    for(int y=0;y<2160;y++)for(int x=0;x<3840;x++) {
        int value=33+(x/32)%16;
        b[(size_t)y*3840+x]=(unsigned char)value;
    }
    assert(sp11_rear_trial_tone_nv12(b,n,3840,2160,&m)==0);
    assert(m.applied && m.input_p01==33 && m.input_p99==48);
    assert(m.output_p01_estimate==125 &&
           m.output_p50_estimate>=140 &&
           m.output_p99_estimate>=175 && m.output_p99_estimate<=185);
    assert(m.unchanged_chroma==1 && !m.black_reference_calibrated &&
           !m.real_scene_detail_verified);
    assert(b[0]==125 && b[31]==125 &&
           b[33]==sp11_tone_map_y(34,33));
    for(size_t i=SP11_REAR_PREVIEW_Y;i<n;i++)assert(b[i]==128);
    /* A wrong device geometry, truncated frame or missing stats fails closed
       without applying an unknown image transform. */
    assert(sp11_rear_trial_tone_nv12(b,n-1,3840,2160,&m)==-1);
    assert(sp11_rear_trial_tone_nv12(b,n,1920,1080,&m)==-1);
    assert(sp11_rear_trial_tone_nv12(NULL,n,3840,2160,&m)==-1);
    assert(sp11_rear_trial_tone_nv12(b,n,3840,2160,NULL)==-1);
    free(b);
}
int main(void) {
    test();
    puts("REAR_OPTIN_TONE_CAMERA_FREE=PASS GATED_DARK_FLAT_BRIGHT_VIDEO_RANGE_CHROMA_UNCHANGED");
    return 0;
}
