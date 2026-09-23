/* SPDX-License-Identifier: MIT
 * Experiment E004mv ONLY: sparse aggregate SAME FRAME RAW10 photosite upper
 * 8-bit and software-converted NV12-Y statistics. Never store pixels, tiles,
 * hashes, decoded photos or registers. No camera or graph action here.
 */
#ifndef SP11_E004MV_RAW_NV12_PROBE_H
#define SP11_E004MV_RAW_NV12_PROBE_H
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stddef.h>
#include <time.h>

struct sp11_mc_hist {
    uint64_t bins[256];
    uint64_t sum;
    uint64_t total;
    uint64_t above32;
};
struct sp11_mc_pair {
    struct sp11_mc_hist source;
    struct sp11_mc_hist output;
};
static void sp11_mc_add(struct sp11_mc_hist *h,unsigned char v) {
    h->bins[v]++;h->sum+=v;h->total++;h->above32+=(v>32);
}
static unsigned sp11_mc_percentile(const struct sp11_mc_hist *h,unsigned percent) {
    if(!h->total || percent>100) return 0;
    uint64_t target=(h->total*percent+99)/100;
    if(target<1)target=1;
    uint64_t accum=0;
    for(unsigned value=0;value<256;value++) {
        accum+=h->bins[value];
        if(accum>=target) return value;
    }
    return 255;
}
static bool sp11_mc_measure(const unsigned char *packed,
                            const unsigned char *yuv,
                            int source_w,int source_h,int source_stride,
                            int out_w,int out_h,int scale,int crop_x,int crop_y,
                            struct sp11_mc_pair *pair) {
    if(!packed||!yuv||!pair||source_w<16||source_h<16||
       source_stride<(source_w/4)*5 || out_w<16||out_h<16 ||
       (scale!=1 && scale!=2)||crop_x<0||crop_y<0||
       crop_x+out_w*scale>source_w || crop_y+out_h*scale>source_h ||
       (source_w%4) || (out_w%2) || (out_h%2))return false;
    *pair=(struct sp11_mc_pair){0};
    /* Approx. 8k spaced OUTPUT locations for each native front/rear mode.
     * Four Bayer photosites are sampled for each output luma value, rather
     * than selecting only one colour mosaic phase. RAW10 fifth packed
     * low-bit byte is deliberately omitted; this matches the current
     * accepted 8-bit software conversion, NOT the full 10-bit dynamic range.
     */
    const int step=(scale==2?16:32);
    for(int oy=0;oy<out_h;oy+=step) {
        int sy=crop_y+oy*scale;
        for(int ox=0;ox<out_w;ox+=step) {
            int sx=crop_x+ox*scale;
            sp11_mc_add(&pair->output,yuv[(size_t)oy*out_w+ox]);
            for(int dy=0;dy<2;dy++) {
                const unsigned char *row=packed+(size_t)(sy+dy)*source_stride;
                for(int dx=0;dx<2;dx++) {
                    int x=sx+dx;
                    sp11_mc_add(&pair->source,row[(size_t)(x/4)*5+(x%4)]);
                }
            }
        }
    }
    return pair->source.total>=32 && pair->source.total==4*pair->output.total;
}
static void sp11_mc_report(const char *camera,long frame,
                           const struct sp11_mc_pair *p) {
    const struct sp11_mc_hist *a=&p->source,*b=&p->output;
    struct timespec now={0};
    if(clock_gettime(CLOCK_MONOTONIC,&now))return;
    double mono_ms=(double)now.tv_sec*1000.+now.tv_nsec/1000000.;
    fprintf(stderr,
      "E004MV_PAIRED_RAW_NV12 camera=%s frame=%ld mono_ms=%.3f "
      "raw_mean8=%.3f raw_p95=%u raw_p99=%u raw_gt32=%.5f "
      "nv12_y_mean=%.3f nv12_y_p95=%u nv12_y_p99=%u nv12_y_gt32=%.5f "
      "source_bright_nv12_dark=%d raw_samples=%llu y_samples=%llu "
      "raw8_upper_only=YES frame_pair=YES pixels_saved=NO\n",
      camera,frame,mono_ms,(double)a->sum/a->total,
      sp11_mc_percentile(a,95),sp11_mc_percentile(a,99),
      (double)a->above32/a->total,
      (double)b->sum/b->total,
      sp11_mc_percentile(b,95),sp11_mc_percentile(b,99),
      (double)b->above32/b->total,
      (sp11_mc_percentile(a,99)>=80 && sp11_mc_percentile(b,99)<=20),
      (unsigned long long)a->total,(unsigned long long)b->total);
}
#endif
