/* SPDX-License-Identifier: MIT */
#ifndef E011AJ_BG_PRODUCER_H
#define E011AJ_BG_PRODUCER_H
#include <stdint.h>
#include <errno.h>
/* L4 caller geometry and thresholds, BEFORE hardware lowering.
 * Bounded Titan680 non-HDR Bayer policy: region limits16..512,
 * even region sizes, threshold gain exactly1. No weights/flags/black policy. */
struct e011aj_bg_input {
    uint32_t crop_width,crop_height,h_num,v_num;
    uint32_t h_offset,v_offset,roi_width,roi_height;
    uint32_t threshold[4]; /* R,B,GR,GB */
    uint32_t bit_depth,gain_bits;
};
struct e011aj_bg_output {
    uint32_t h_num,v_num,h_offset,v_offset,region_width,region_height;
    uint32_t threshold[4];
};
static inline uint32_t e011aj_bg_region(uint32_t span,uint32_t *count)
{
    uint32_t region=(span/(*count))&~1U;
    if(region<16) { region=16;*count=span/region; }
    else if(region>512) { region=512;*count=span/region; }
    return region;
}
static int e011aj_produce_bg(const struct e011aj_bg_input *in,
                            struct e011aj_bg_output *out)
{
    struct e011aj_bg_output v={0};
    uint32_t width,height,limit;
    if(!in||!out) return -EINVAL;
    if(in->gain_bits!=0x3f800000U) return -EOPNOTSUPP;
    if(in->crop_width<16||in->crop_width>16384||
       in->crop_height<16||in->crop_height>16384||
       !in->h_num||in->h_num>64||!in->v_num||in->v_num>64||
       in->h_offset>0x3ffe||in->v_offset>0x3ffe||
       in->h_offset>=in->crop_width||in->v_offset>=in->crop_height||
       !in->roi_width||!in->roi_height||
       in->roi_width>in->crop_width-in->h_offset||
       in->roi_height>in->crop_height-in->v_offset||
       !in->bit_depth||in->bit_depth>18) return -ERANGE;
    /* The original adjusts span against min/max region*count, clips to crop,
     * then floors even dimensions and revises count only at a region bound. */
    width=in->roi_width;height=in->roi_height;
    if(width<16*in->h_num) width=16*in->h_num;
    if(width>512*in->h_num) width=512*in->h_num;
    if(width>in->crop_width-in->h_offset) width=in->crop_width-in->h_offset;
    if(height<16*in->v_num) height=16*in->v_num;
    if(height>512*in->v_num) height=512*in->v_num;
    if(height>in->crop_height-in->v_offset) height=in->crop_height-in->v_offset;
    if(width<16||height<16) return -ERANGE;
    v.h_num=in->h_num;v.v_num=in->v_num;
    v.region_width=e011aj_bg_region(width,&v.h_num);
    v.region_height=e011aj_bg_region(height,&v.v_num);
    if(!v.h_num||v.h_num>64||!v.v_num||v.v_num>64) return -ERANGE;
    v.h_offset=in->h_offset&~1U;v.v_offset=in->v_offset&~1U;
    limit=(1U<<in->bit_depth)-1;
    for(unsigned int i=0;i<4;i++)
        v.threshold[i]=in->threshold[i]>limit?limit:in->threshold[i];
    *out=v;return 0;
}
#endif
