/* Camera-free exact front1080 NV12 Y opt-in and UV-invariant gate tests. */
#include "../front_preview_tone.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum {W=1920,H=1080,YP=SP11_FRONT_PREVIEW_Y};
static unsigned char *buf;
static void frame(unsigned y) {
    memset(buf,(int)y,YP);
    for(size_t p=YP;p<YP*3u/2u;p++)
        buf[p]=(unsigned char)(119u+(p-YP)%15u);
}
static void chroma_unchanged(void) {
    for(size_t p=YP;p<YP*3u/2u;p++)
        assert(buf[p]==119u+(p-YP)%15u);
}
int main(void) {
    buf=malloc(YP*3u/2u);assert(buf);
    struct sp11_front_preview_tone_result m;
    frame(30);
    for(int y=0;y<H;y++)for(int x=0;x<W;x++)buf[y*W+x]=30+(x/257)%8;
    assert(!sp11_front_optin_tone_nv12(buf,YP*3u/2u,W,H,&m));
    assert(!m.applied&&m.input_p01==30&&m.input_p99<=37&&buf[0]==30);
    chroma_unchanged();
    frame(128);
    assert(!sp11_front_optin_tone_nv12(buf,YP*3u/2u,W,H,&m));
    assert(!m.applied&&buf[0]==128);
    frame(30);
    for(int y=0;y<H;y++)for(int x=0;x<W;x++)
        buf[(size_t)y*W+x]=(unsigned char)(30+(x/60)%32);
    assert(!sp11_front_optin_tone_nv12(buf,YP*3u/2u,W,H,&m));
    assert(m.applied&&m.input_p01==30&&m.input_p99==61);
    assert(m.output_p01_estimate==100&&m.output_p99_estimate==162);
    assert(buf[0]==100&&buf[62]==102&&buf[YP-1]>=100);
    chroma_unchanged();
    assert(!m.colour_calibrated&&!m.scene_recognition_proven);
    assert(sp11_front_optin_tone_nv12(buf,YP*3u/2u-1,W,H,&m)==-1);
    assert(sp11_front_optin_tone_nv12(buf,YP*3u/2u,3840,2160,&m)==-1);
    assert(sp11_front_optin_tone_nv12(NULL,YP*3u/2u,W,H,&m)==-1);
    assert(sp11_front_optin_tone_nv12(buf,YP*3u/2u,W,H,NULL)==-1);
    free(buf);
    puts("FRONT_OPTIN_TONE_1080P_CAMERA_FREE=PASS FLAT_DARK_GAIN_BRIGHT_GEOMETRY_Y_ONLY_UV_PRESERVED");
    return 0;
}
