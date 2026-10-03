#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "normal-rs-input.h"
#define CHECK(x) do { if (!(x)) abort(); } while (0)
static void put32(uint8_t *p,uint32_t value)
{
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(value>>(8*i));
}
static unsigned negatives(void)
{
    uint8_t wire[132]={0};
    struct e011dk_whole_frame_crop original={0,0,4063,2285};
    put32(wire,16);put32(wire+4,1024);put32(wire+128,1);
    for(unsigned test=0;test<18;test++) {
        uint8_t record[132];memcpy(record,wire,sizeof(record));
        struct e011dk_whole_frame_crop crop=original;
        struct e011am_rs_input out,before;
        memset(&out,0xa5,sizeof(out));before=out;
        const uint8_t *input=record;const struct e011dk_whole_frame_crop *c=&crop;
        size_t size=132;uint32_t half=0;
        if(test==0)input=NULL;
        if(test==1)c=NULL;
        if(test==2)size=131;
        if(test==3)size=133;
        if(test==4)crop.left=1;
        if(test==5)crop.top=1;
        if(test==6)put32(record+8,1);
        if(test==7)put32(record+12,1);
        if(test==8)crop.right=UINT32_MAX;
        if(test==9)crop.bottom=UINT32_MAX;
        if(test==10)crop.right=14;
        if(test==11)crop.bottom=14;
        if(test==12)put32(record,0);
        if(test==13)put32(record,17);
        if(test==14)put32(record+4,0);
        if(test==15)put32(record+4,1025);
        if(test==16)put32(record+128,2);
        if(test==17)half=2;
        CHECK(e011dk_decode_rs_input(input,size,c,half,&out)<0);
        CHECK(!memcmp(&out,&before,sizeof(out)));
    }
    CHECK(e011dk_decode_rs_input(wire,132,&original,0,NULL)<0);
    uint8_t unchanged[132];memcpy(unchanged,wire,sizeof(wire));
    CHECK(e011dk_decode_rs_input(wire,132,&original,0,(void *)wire)<0);
    CHECK(!memcmp(wire,unchanged,sizeof(wire)));
    struct e011dk_whole_frame_crop before_crop=original;
    CHECK(e011dk_decode_rs_input(wire,132,&original,0,(void *)&original)<0);
    CHECK(!memcmp(&original,&before_crop,sizeof(original)));
    return 21;
}
int main(int argc,char **argv)
{
    unsigned rejected=negatives();
    if(argc==2 && !strcmp(argv[1],"--selfcheck")) {
        printf("{\"atomic_negative_cases\":%u}\n",rejected);
        return 0;
    }
    uint8_t wire[152];
    for(;;) {
        size_t got=fread(wire,1,sizeof(wire),stdin);
        if(!got)break;
        CHECK(got==sizeof(wire));
        struct e011dk_whole_frame_crop crop={
            e011dk_le32(wire+132),e011dk_le32(wire+136),
            e011dk_le32(wire+140),e011dk_le32(wire+144)};
        struct e011am_rs_input in;
        struct e011am_rs_output out;
        CHECK(e011dk_decode_rs_input(wire,132,&crop,e011dk_le32(wire+148),&in)==0);
        CHECK(e011am_produce_rs(&in,&out)==0);
        uint8_t result[56];
        uint32_t fields[14]={in.crop_width,in.crop_height,in.h_num,in.v_num,
            in.half_width,in.color_conversion,out.h_num,out.v_num,
            out.region_width,out.region_height,out.h_offset,out.v_offset,
            out.color_conversion,out.shift_bits};
        for(unsigned i=0;i<14;i++)put32(result+4*i,fields[i]);
        CHECK(fwrite(result,1,sizeof(result),stdout)==sizeof(result));
    }
    CHECK(feof(stdin));
    return 0;
}
