/* SPDX-License-Identifier: MIT */
#include "bg-producer.h"
static unsigned int bg_negative_cases,bg_producer_negative_cases;
static void e011aj_host_rejected(struct e008o_rear_packet_semantics *base,
                                const struct e011aj_startup_bg_source *source)
{
    size_t bytes=4*sizeof(*base);void *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    CHECK(e011aj_rear_bind_startup_bg(base,source)<0);
    CHECK(memcmp(before,base,bytes)==0);free(before);bg_negative_cases++;
}
static void e011aj_host_producer_negatives(void)
{
    struct e011aj_bg_input good={4064,2286,64,48,0,0,3658,2058,
        {0x3ffff,0x3ffff,0x3ffff,0x3ffff},18,0x3f800000};
    struct e011aj_bg_input in;
    struct e011aj_bg_output out,before;
    memset(&out,0xa5,sizeof(out));before=out;
    for(unsigned int i=0;i<12;i++) {
        in=good;
        switch(i) {
        case 0:in.crop_width=0;break;
        case 1:in.crop_height=16385;break;
        case 2:in.h_num=0;break;
        case 3:in.v_num=65;break;
        case 4:in.h_offset=in.crop_width;break;
        case 5:in.v_offset=0x3fff;break;
        case 6:in.roi_width=0;break;
        case 7:in.roi_height=in.crop_height+1;break;
        case 8:in.bit_depth=0;break;
        case 9:in.bit_depth=19;break;
        case 10:in.gain_bits=0x40000000;break;
        default:in.h_offset=in.crop_width-1;in.roi_width=1;break;
        }
        CHECK(e011aj_produce_bg(&in,&out)<0);
        CHECK(memcmp(&out,&before,sizeof(out))==0);bg_producer_negative_cases++;
    }
    CHECK(e011aj_produce_bg(NULL,&out)<0);CHECK(memcmp(&out,&before,sizeof(out))==0);bg_producer_negative_cases++;
    CHECK(e011aj_produce_bg(&good,NULL)<0);bg_producer_negative_cases++;
    CHECK(e011aj_produce_bg(&good,&out)==0);
    CHECK(out.region_width==56&&out.region_height==42);
    in=good;in.h_num=in.v_num=64;in.crop_width=in.crop_height=16;
    in.roi_width=in.roi_height=16;
    CHECK(e011aj_produce_bg(&in,&out)==0);
    CHECK(out.h_num==1&&out.v_num==1&&out.region_width==16&&out.region_height==16);
    in=good;in.h_num=in.v_num=1;in.roi_width=in.crop_width;in.roi_height=in.crop_height;
    CHECK(e011aj_produce_bg(&in,&out)==0);
    CHECK(out.region_width==512&&out.region_height==512&&out.h_num==1&&out.v_num==1);
    in=good;in.threshold[0]=0xffffffffU;in.bit_depth=1;
    CHECK(e011aj_produce_bg(&in,&out)==0);CHECK(out.threshold[0]==1);
}
static void e011aj_host_bind(struct e008o_rear_packet_semantics *base)
{
    struct e011aj_startup_bg_source source={0},saved;
    struct e011aj_bg_values *values[4]={&source.aec[0],&source.aec[1],&source.awb[0],&source.awb[1]};
    size_t bytes=4*sizeof(*base);
    struct e008o_rear_packet_semantics *before=malloc(bytes);CHECK(before);memcpy(before,base,bytes);
    for(unsigned int i=0;i<4;i++) {
        u8 wire[40];u32 fields[10];read_exact(wire,sizeof(wire));
        for(unsigned int j=0;j<10;j++)fields[j]=get_unaligned_le32(wire+4*j);
        memcpy(values[i],fields,sizeof(fields));
    }
    source.source_id[0]=0;source.source_id[1]=1;saved=source;
    CHECK(e011aj_rear_bind_startup_bg(NULL,&source)==-EINVAL);bg_negative_cases++;
    CHECK(e011aj_rear_bind_startup_bg(base,NULL)==-EINVAL);bg_negative_cases++;
    CHECK(e011aj_rear_bind_startup_bg(base,(const void *)base)==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);bg_negative_cases++;
    for(unsigned int i=0;i<4;i++) {
        for(unsigned int j=0;j<10;j++) {
            u32 fields[10];memcpy(fields,values[i],sizeof(fields));
            fields[j]=j<2?65:j<4?1:j<6?15:0x40000;
            memcpy(values[i],fields,sizeof(fields));
            e011aj_host_rejected(base,&source);source=saved;
        }
        values[i]->region_width=513;e011aj_host_rejected(base,&source);source=saved;
        values[i]->region_height=513;e011aj_host_rejected(base,&source);source=saved;
        values[i]->h_num=0;e011aj_host_rejected(base,&source);source=saved;
        values[i]->v_num=0;e011aj_host_rejected(base,&source);source=saved;
        values[i]->h_offset=0x4000;e011aj_host_rejected(base,&source);source=saved;
        values[i]->v_offset=0x4000;e011aj_host_rejected(base,&source);source=saved;
    }
    for(unsigned int i=0;i<2;i++) {
        source.source_id[i]=2;e011aj_host_rejected(base,&source);source=saved;
    }
    for(unsigned int p=0;p<4;p++) {
        base[p].ready=true;e011aj_host_rejected(base,&source);base[p]=before[p];
        base[p].request_id=0;e011aj_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.request_id++;e011aj_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.startup_phase=4;e011aj_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STEADY;e011aj_host_rejected(base,&source);base[p]=before[p];
    }
    base[3].request_id=base[2].request_id;base[3].regs.scalar.request_id=base[2].request_id;
    e011aj_host_rejected(base,&source);base[3]=before[3];
    CHECK(e011aj_rear_bind_startup_bg(base,&source)==0);
    for(unsigned int p=0;p<4;p++) {
        e011aj_bg_apply(&before[p].regs.aec_be,&source.aec[p?1:0]);
        e011aj_bg_apply(&before[p].regs.awb_bg,&source.awb[p?1:0]);
    }
    CHECK(memcmp(base,before,bytes)==0);CHECK(memcmp(&source,&saved,sizeof(source))==0);
    CHECK(e011aj_rear_runtime_authorization()==-EOPNOTSUPP);
    e011aj_host_producer_negatives();free(before);
}
