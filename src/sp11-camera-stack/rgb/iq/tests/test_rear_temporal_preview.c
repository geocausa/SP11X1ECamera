/* SPDX-License-Identifier: MIT
 * Camera-free full 4K synthetic temporal examples: zero optical pixels.
 * Correct geometry, luma Y only, preservation UV, fail-closed scene cuts,
 * moving contrast edges, short-memory noise and source sequence discontinuity.
 */
#include "../rear_temporal_preview.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { W=SP11_REAR_PREVIEW_W,H=SP11_REAR_PREVIEW_H,YP=SP11_REAR_PREVIEW_Y };
static const size_t BYTES=(size_t)YP*3u/2u;
static uint8_t *image,*history;
static struct sp11_rear_temporal_state s;
static struct sp11_rear_temporal_stats m;
static void setframe(unsigned Y) {
    memset(image,(int)Y,YP);
    memset(image+YP,99u,YP/2u);
}
static void uvcheck(void) {
    for(size_t i=YP;i<BYTES;i++)assert(image[i]==99u);
}
static void call(uint32_t seq,double timestamp,unsigned profile,int toned) {
    assert(!sp11_rear_temporal_nv12(image,BYTES,W,H,toned,
                                   seq,timestamp,profile,&s,&m));
    uvcheck();
}
static void test(void) {
    image=malloc(BYTES);history=malloc(YP);assert(image&&history);
    assert(!sp11_rear_temporal_init(&s,history,YP));
    setframe(125);
    /* Reject any unexpected physical format/size, timestamp/profile or
     * missing caller allocation WITHOUT touching image luma/chroma. */
    assert(sp11_rear_temporal_nv12(image,BYTES-1,W,H,1,1,10.,1,&s,&m)==-1);
    assert(sp11_rear_temporal_nv12(image,BYTES,1920,1080,1,1,10.,1,&s,&m)==-1);
    assert(sp11_rear_temporal_nv12(image,BYTES,W,H,1,1,10.,0,&s,&m)==-1);
    assert(sp11_rear_temporal_nv12(image,BYTES,W,H,1,1,-1.,1,&s,&m)==-1);
    assert(sp11_rear_temporal_nv12(NULL,BYTES,W,H,1,1,10.,1,&s,&m)==-1);
    assert(sp11_rear_temporal_nv12(image,BYTES,W,H,1,1,10.,1,&s,NULL)==-1);
    assert(sp11_rear_temporal_init(NULL,history,YP)==-1);
    assert(sp11_rear_temporal_init(&s,history,YP-1)==-1);
    /* A baseline/no-tone frame cannot seed stale prior exposure pixels. */
    call(1u,10.,1u,0);
    assert(m.reset_tone&&!s.valid&&image[0]==125);
    call(2u,43.3,1u,1);
    assert(m.initialized&&!m.filtered&&s.valid&&image[0]==125);
    /* Synthetic stationary scene with changing +/-2 luma noise. 50:50
     * recurrence attenuates this alternating component on every block. */
    for(size_t i=0;i<YP;i++)image[i]=127;
    call(3u,76.6,1u,1);
    assert(m.filtered && m.blocks_filtered>1000000u);
    assert(!m.blocks_bypassed && m.pixels_changed>0 && image[0]==126);
    setframe(123);
    call(4u,109.9,1u,1);
    assert(m.filtered && image[0]==125 && !m.reset_scene);
    /* A local moving high-contrast 2x2 edge must not include prior dark
     * pixels even when global histogram/median do not change. */
    setframe(125);
    for(int y=100;y<102;y++)for(int x=100;x<102;x++)image[(size_t)y*W+x]=175;
    call(5u,143.2,1u,1);
    assert(m.filtered && m.blocks_bypassed>=1 && image[100u*W+100u]==175);
    assert(image[0]==125 && image[100u*W+101u]==175);
    /* Widespread exposure/scene step must reset, with NO blended ghosts. */
    setframe(180);
    call(6u,176.5,1u,1);
    assert(m.reset_scene && m.initialized && !m.filtered && image[0]==180);
    /* Distinct profile, discontinuous timestamp, dropped source frame
     * always invalidate history even when displayed mean is unchanged. */
    setframe(181);
    call(7u,209.8,2u,1);
    assert(m.reset_scene && m.initialized && image[0]==181);
    setframe(180);
    call(9u,243.1,2u,1);
    assert(m.reset_sequence && m.initialized && image[0]==180);
    setframe(181);
    call(10u,500.0,2u,1);
    assert(m.reset_sequence && m.initialized && image[0]==181);
    setframe(180);
    call(11u,533.3,2u,0);
    assert(m.reset_tone&&!s.valid&&image[0]==180);
    /* No hidden history after release; no files/device access. */
    sp11_rear_temporal_reset(&s);
    assert(!s.valid&&history[0]==0);
    free(history);free(image);
}
int main(void) {
    test();
    puts("REAR_4K_TEMPORAL_CAMERA_FREE=PASS OPTIN_TONE_SEQUENCE_SCENE_CUT_MOVING_EDGE_NO_GHOST_EXPOSURE_RESET_UV_UNCHANGED");
    return 0;
}
