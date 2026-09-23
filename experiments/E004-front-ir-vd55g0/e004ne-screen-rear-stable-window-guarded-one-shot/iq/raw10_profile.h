/* SPDX-License-Identifier: MIT
 * Pure-memory RAW10 Bayer channel profiling. No devices, image export,
 * sensor controls, or inference of optical black level/white balance.
 */
#ifndef SP11_RGB_RAW10_PROFILE_H
#define SP11_RGB_RAW10_PROFILE_H
#include "raw10_unpack.h"
#include <stdint.h>
#include <stddef.h>
#include <string.h>

enum sp11_rgb_bayer { SP11_RGB_RGGB=1, SP11_RGB_GRBG=2 };
enum { SP11_RGB_R=0, SP11_RGB_G0=1, SP11_RGB_G1=2, SP11_RGB_B=3 };
struct sp11_raw10_channel {
    uint64_t histogram[1024];
    uint64_t low_two_bits[4];
    uint64_t sampled;
    uint16_t p01, p50, p95, p99, lowest, highest;
};
struct sp11_raw10_profile {
    struct sp11_raw10_channel channel[4];
    size_t block_step, sampled_bayer_blocks;
    enum sp11_rgb_bayer phase;
};

static inline uint16_t sp11_raw10_quantile(const uint64_t histogram[1024],
                                            uint64_t samples, unsigned pct)
{
    if (!samples || pct>100u) return 0;
    /* ceil(samples*pct/100) without potentially overflowing multiplication */
    uint64_t target=(samples/100u)*pct +
        (((samples%100u)*pct + 99u)/100u);
    if (!target) target=1;
    uint64_t count=0;
    for (unsigned i=0; i<1024; i++) {
        count+=histogram[i];
        if (count>=target) return (uint16_t)i;
    }
    return 1023; /* only reachable if supplied histogram is inconsistent */
}

static inline int sp11_raw10_profile_frame(const uint8_t *frame,
                 size_t available, size_t stride, size_t width, size_t height,
                 enum sp11_rgb_bayer phase, size_t block_step,
                 struct sp11_raw10_profile *output)
{
    /* Probe exactly one of the accepted native raw RGB modes. Fail closed
       instead of profile-by-guessing an ISP-compressed or IR source. */
    const int front = width==3840u && height==2160u && stride==4800u &&
                      phase==SP11_RGB_RGGB;
    const int rear = width==4076u && height==2806u && stride==5104u &&
                     phase==SP11_RGB_GRBG;
    if (!frame || !output || (!front && !rear) ||
        block_step<1u || block_step>32u ||
        height>SIZE_MAX/stride || available < height*stride)
        return -1;
    memset(output,0,sizeof(*output));
    output->block_step=block_step;
    output->phase=phase;
    const size_t skip=2u*block_step;
    /* Sample Bayer 2x2 blocks, never stride padding, with both green sites
       kept separate. Low-two-bit distribution checks real RAW packing. */
    for (size_t y=0; y+1u<height; y+=skip) {
        const uint8_t *top=frame+y*stride;
        const uint8_t *bottom=top+stride;
        for (size_t x=0; x+1u<width; x+=skip) {
            uint16_t pixel[4];
            if (sp11_raw10_pixel(top,stride,width,x,&pixel[0]) ||
                sp11_raw10_pixel(top,stride,width,x+1u,&pixel[1]) ||
                sp11_raw10_pixel(bottom,stride,width,x,&pixel[2]) ||
                sp11_raw10_pixel(bottom,stride,width,x+1u,&pixel[3]))
                return -1;
            static const unsigned rggb[4]={SP11_RGB_R,SP11_RGB_G0,SP11_RGB_G1,SP11_RGB_B};
            static const unsigned grbg[4]={SP11_RGB_G0,SP11_RGB_R,SP11_RGB_B,SP11_RGB_G1};
            const unsigned *map=front?rggb:grbg;
            for (unsigned k=0;k<4;k++) {
                struct sp11_raw10_channel *c=&output->channel[map[k]];
                const unsigned raw=pixel[k];
                c->histogram[raw]++;
                c->low_two_bits[raw & 3u]++;
                c->sampled++;
            }
            output->sampled_bayer_blocks++;
        }
    }
    if (!output->sampled_bayer_blocks) return -1;
    for (unsigned c=0;c<4;c++) {
        struct sp11_raw10_channel *v=&output->channel[c];
        if (v->sampled!=output->sampled_bayer_blocks) return -1;
        v->p01=sp11_raw10_quantile(v->histogram,v->sampled,1);
        v->p50=sp11_raw10_quantile(v->histogram,v->sampled,50);
        v->p95=sp11_raw10_quantile(v->histogram,v->sampled,95);
        v->p99=sp11_raw10_quantile(v->histogram,v->sampled,99);
        for (unsigned i=0;i<1024;i++) {
            if (v->histogram[i]) {
                v->lowest=(uint16_t)i;
                break;
            }
        }
        for (int i=1023;i>=0;i--) {
            if (v->histogram[i]) {
                v->highest=(uint16_t)i;
                break;
            }
        }
    }
    return 0;
}
#endif
