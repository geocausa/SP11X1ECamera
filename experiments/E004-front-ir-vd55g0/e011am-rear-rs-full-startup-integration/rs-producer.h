/* SPDX-License-Identifier: MIT */
#ifndef E011AM_RS_PRODUCER_H
#define E011AM_RS_PRODUCER_H
#include <stdint.h>
#include <errno.h>
/* L4 whole-frame, zero-offset RS inputs. Counts are caller policy inputs:
 * their earlier AFD producer is outside this arithmetic slice.
 * half_width is the source pixel-format==1 branch, not module enable.
 * No stripe offsets, color matrix, register words or hardware calls. */
struct e011am_rs_input {
    uint32_t crop_width,crop_height,h_num,v_num,half_width,color_conversion;
};
struct e011am_rs_output {
    uint32_t h_num,v_num,region_width,region_height,h_offset,v_offset;
    uint32_t color_conversion,shift_bits;
};
static int e011am_produce_rs(const struct e011am_rs_input *in,
                            struct e011am_rs_output *out)
{
    struct e011am_rs_output v={0};
    uint32_t width,height,region_width,region_height,area;
    if(!in||!out) return -EINVAL;
    if(in->crop_width<16||in->crop_width>16384||
       in->crop_height<16||in->crop_height>16384||
       !in->h_num||in->h_num>16||!in->v_num||in->v_num>1024||
       in->half_width>1||in->color_conversion>1) return -ERANGE;
    width=in->half_width?in->crop_width/2:in->crop_width;
    height=in->crop_height;
    region_width=width/in->h_num;
    if(region_width<2) region_width=2;
    if(region_width>8192) region_width=8192;
    region_height=(height/in->v_num)&~1U;
    if(region_height<2) region_height=2;
    if(region_height>16) region_height=16;
    v.h_num=in->h_num;v.v_num=in->v_num;
    if(v.h_num>width/region_width) v.h_num=width/region_width;
    if(v.v_num>height/region_height) v.v_num=height/region_height;
    if(!v.h_num||!v.v_num) return -ERANGE;
    v.region_width=region_width;v.region_height=region_height;
    v.color_conversion=in->color_conversion;
    for(area=region_width*region_height;area;area>>=1) v.shift_bits++;
    v.shift_bits=v.shift_bits>4?v.shift_bits-4:0;
    *out=v;return 0;
}
#endif
