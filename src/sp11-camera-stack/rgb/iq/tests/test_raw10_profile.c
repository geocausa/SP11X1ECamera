/* SPDX-License-Identifier: MIT
 * Strict synthetic full-frame RAW10 Bayer diagnostic with no hardware IO.
 * Only known isolated values are written at the sparse sample locations.
 */
#include "../raw10_profile.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void pack(uint8_t *row,size_t x,uint16_t v)
{
    const size_t g=(x/4u)*5u;
    const unsigned s=(unsigned)(x&3u)*2u;
    row[g+(x&3u)]=(uint8_t)(v>>2);
    row[g+4u]=(uint8_t)((row[g+4u]&~(3u<<s))|((v&3u)<<s));
}
static void exercise(size_t w,size_t h,size_t stride,
                     enum sp11_rgb_bayer phase,const uint16_t values[4])
{
    const size_t bytes=h*stride;
    uint8_t *frame=calloc(bytes,1u);
    assert(frame);
    /* Deliberately poison the rear's non-image stride padding; no sampled
       Bayer channel may include it, including the rightmost pixel. */
    const size_t packed=(w/4u)*5u;
    for (size_t y=0;y<h;y++)
        memset(frame+y*stride+packed,0xff,stride-packed);
    const size_t step=16u, interval=2u*step;
    for (size_t y=0;y+1u<h;y+=interval) {
        for (size_t x=0;x+1u<w;x+=interval) {
            const unsigned map[4]={
                phase==SP11_RGB_RGGB?SP11_RGB_R:SP11_RGB_G0,
                phase==SP11_RGB_RGGB?SP11_RGB_G0:SP11_RGB_R,
                phase==SP11_RGB_RGGB?SP11_RGB_G1:SP11_RGB_B,
                phase==SP11_RGB_RGGB?SP11_RGB_B:SP11_RGB_G1
            };
            pack(frame+y*stride,x,values[map[0]]);
            pack(frame+y*stride,x+1u,values[map[1]]);
            pack(frame+(y+1u)*stride,x,values[map[2]]);
            pack(frame+(y+1u)*stride,x+1u,values[map[3]]);
        }
    }
    struct sp11_raw10_profile *p=malloc(sizeof(*p));
    assert(p);
    assert(sp11_raw10_profile_frame(frame,bytes,stride,w,h,phase,step,p)==0);
    assert(p->sampled_bayer_blocks>1000u);
    for (unsigned c=0;c<4;c++) {
        const struct sp11_raw10_channel *v=&p->channel[c];
        assert(v->sampled==p->sampled_bayer_blocks);
        assert(v->lowest==values[c] && v->highest==values[c]);
        assert(v->p01==values[c] && v->p50==values[c]);
        assert(v->p95==values[c] && v->p99==values[c]);
        assert(v->low_two_bits[values[c]&3u]==v->sampled);
        assert(v->histogram[values[c]]==v->sampled);
    }
    /* Reject any stray mode/crop, frame truncation or unbounded sampling. */
    assert(sp11_raw10_profile_frame(frame,bytes-1,stride,w,h,phase,step,p)==-1);
    assert(sp11_raw10_profile_frame(frame,bytes,stride,w,h,phase,0,p)==-1);
    assert(sp11_raw10_profile_frame(frame,bytes,stride,w,h,phase,33,p)==-1);
    assert(sp11_raw10_profile_frame(frame,bytes,stride,w,h,
          phase==SP11_RGB_RGGB?SP11_RGB_GRBG:SP11_RGB_RGGB,step,p)==-1);
    assert(sp11_raw10_profile_frame(NULL,bytes,stride,w,h,phase,step,p)==-1);
    assert(sp11_raw10_profile_frame(frame,bytes,stride,w,h,phase,step,NULL)==-1);
    free(p);
    free(frame);
}
int main(void)
{
    const uint16_t front[]={101u,202u,303u,404u};
    const uint16_t rear[]={505u,606u,707u,808u};
    exercise(3840u,2160u,4800u,SP11_RGB_RGGB,front);
    exercise(4076u,2806u,5104u,SP11_RGB_GRBG,rear);
    uint64_t bins[1024]={0};
    bins[23]=1;bins[250]=98;bins[990]=1;
    assert(sp11_raw10_quantile(bins,100,1)==23);
    assert(sp11_raw10_quantile(bins,100,50)==250);
    assert(sp11_raw10_quantile(bins,100,99)==250);
    assert(sp11_raw10_quantile(bins,100,100)==990);
    puts("RGB_RAW10_CHANNEL_PROFILE_OFFLINE_TEST=PASS FRONT_REAR_BAYER_STRIDE_LSB_QUANTILES");
    return 0;
}
