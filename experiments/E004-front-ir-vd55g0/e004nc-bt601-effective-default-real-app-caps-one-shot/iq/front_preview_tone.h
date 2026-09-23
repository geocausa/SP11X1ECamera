/* SPDX-License-Identifier: MIT
 * E004mx: opt-in FRONT 1080p NV12 Y preview ONLY after VERIFIED sensor
 * gain; never an IR, sensor-register, black-level, colour, calibrated
 * AE or Windows ISP operation. NORMAL maintained camera remains OFF.
 *
 * Hard no-signal, low-spread, bright, clipping and geometry bypasses.
 * Absolute luma after the transform is for an on-device display
 * experiment, NOT recovered optical scene detail or real SNR.
 */
#ifndef SP11_FRONT_PREVIEW_TONE_H
#define SP11_FRONT_PREVIEW_TONE_H
#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum { SP11_FRONT_PREVIEW_W=1920, SP11_FRONT_PREVIEW_H=1080,
       SP11_FRONT_PREVIEW_Y=1920*1080 };
struct sp11_front_preview_tone_result {
    int applied;
    unsigned input_p01,input_p50,input_p99;
    unsigned output_p01_estimate,output_p50_estimate,output_p99_estimate;
    size_t sampled;
    int unchanged_chroma,colour_calibrated,scene_recognition_proven;
};
static inline unsigned sp11_front_hist_percentile(const uint32_t *h,size_t n,unsigned q)
{
    size_t rank=(n*q+99u)/100u,seen=0;
    if(rank==0)rank=1;
    for(unsigned i=0;i<256;i++) {
        seen+=h[i];if(seen>=rank)return i;
    }
    return 255u;
}
static inline unsigned char sp11_front_tone_y(unsigned y,unsigned low)
{
    /* p01->100; multiplier2; legal studio range [16,235].
     * Unlike rear p01->125 x3.5, this limits front noise magnification.
     */
    int value=100+2*((int)y-(int)low);
    if(value<16)value=16;
    if(value>235)value=235;
    return (unsigned char)value;
}
static inline int sp11_front_optin_tone_nv12(unsigned char *nv12,size_t bytes,
             int width,int height,struct sp11_front_preview_tone_result *out)
{
    if(!out||!nv12||width!=SP11_FRONT_PREVIEW_W||
       height!=SP11_FRONT_PREVIEW_H||
       bytes!=SP11_FRONT_PREVIEW_Y*3u/2u)return -1;
    memset(out,0,sizeof(*out));out->unchanged_chroma=1;
    uint32_t hist[256]={0};size_t count=0;
    for(int y=0;y<height;y+=16)
        for(int x=0;x<width;x+=16) {
            hist[nv12[(size_t)y*width+(size_t)x]]++;
            count++;
        }
    if(count<1000)return -1;
    const unsigned p01=sp11_front_hist_percentile(hist,count,1u);
    const unsigned p50=sp11_front_hist_percentile(hist,count,50u);
    const unsigned p99=sp11_front_hist_percentile(hist,count,99u);
    out->input_p01=p01;out->input_p50=p50;out->input_p99=p99;
    out->output_p01_estimate=p01;out->output_p50_estimate=p50;
    out->output_p99_estimate=p99;out->sampled=count;
    /* Flat near-black front baseline must remain unchanged; a cap,
     * empty or lens-covered scene is NOT proof of real scene.
     * Known gain source p01~30, p50~34, p99~61 from E004mv.
     * An already bright scene MUST NOT be re-amplified.
     */
    if(p01<20u||p01>55u||p99>75u||
       p99-p01<12u||sp11_front_tone_y(p99,p01)>215u)return 0;
    unsigned char lut[256];
    for(unsigned i=0;i<256;i++)lut[i]=sp11_front_tone_y(i,p01);
    for(size_t i=0;i<SP11_FRONT_PREVIEW_Y;i++)nv12[i]=lut[nv12[i]];
    out->applied=1;
    out->output_p01_estimate=lut[p01];
    out->output_p50_estimate=lut[p50];
    out->output_p99_estimate=lut[p99];
    return 0;
}
#endif
