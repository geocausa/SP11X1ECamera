/* SPDX-License-Identifier: MIT */
#include "rs-producer.h"
static unsigned int rs_negative_cases,rs_producer_negative_cases;
static void e011am_host_rejected(struct e008o_rear_packet_semantics *base,
    const struct e011am_startup_rs_source *source)
{
    size_t bytes=4*sizeof(*base);void *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    CHECK(e011am_rear_bind_startup_rs(base,source)<0);
    CHECK(memcmp(before,base,bytes)==0);free(before);rs_negative_cases++;
}
static void e011am_host_producer_checks(void)
{
    struct e011am_rs_input good={4064,2286,16,1024,0,1},in;
    struct e011am_rs_output out,before;
    memset(&out,0xa5,sizeof(out));before=out;
    for(unsigned int i=0;i<12;i++) {
        in=good;
        switch(i) {
        case 0:in.crop_width=0;break;
        case 1:in.crop_width=15;break;
        case 2:in.crop_width=16385;break;
        case 3:in.crop_height=0;break;
        case 4:in.crop_height=15;break;
        case 5:in.crop_height=16385;break;
        case 6:in.h_num=0;break;
        case 7:in.h_num=17;break;
        case 8:in.v_num=0;break;
        case 9:in.v_num=1025;break;
        case 10:in.half_width=2;break;
        default:in.color_conversion=2;break;
        }
        CHECK(e011am_produce_rs(&in,&out)==-ERANGE);
        CHECK(memcmp(&out,&before,sizeof(out))==0);rs_producer_negative_cases++;
    }
    CHECK(e011am_produce_rs(NULL,&out)==-EINVAL);
    CHECK(memcmp(&out,&before,sizeof(out))==0);rs_producer_negative_cases++;
    CHECK(e011am_produce_rs(&good,NULL)==-EINVAL);rs_producer_negative_cases++;
    CHECK(e011am_produce_rs(&good,&out)==0);
    CHECK(out.h_num==16&&out.v_num==1024&&out.region_width==254&&out.region_height==2&&out.shift_bits==5);
    in=(struct e011am_rs_input){16,16,16,1024,1,0};
    CHECK(e011am_produce_rs(&in,&out)==0);
    CHECK(out.h_num==4&&out.v_num==8&&out.region_width==2&&out.region_height==2&&!out.color_conversion&&!out.shift_bits);
    in=(struct e011am_rs_input){16384,16384,1,1,0,1};
    CHECK(e011am_produce_rs(&in,&out)==0);
    CHECK(out.h_num==1&&out.v_num==1&&out.region_width==8192&&out.region_height==16&&out.shift_bits==14);
    in=(struct e011am_rs_input){31,31,16,1024,0,1};
    CHECK(e011am_produce_rs(&in,&out)==0);
    CHECK(out.h_num==15&&out.v_num==15&&out.region_width==2&&out.region_height==2&&!out.h_offset&&!out.v_offset);
}
static void e011am_host_bind(struct e008o_rear_packet_semantics *base)
{
    struct e011am_startup_rs_source source={0},saved;
    size_t bytes=4*sizeof(*base);struct e008o_rear_packet_semantics *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    for(unsigned int p=0;p<3;p++) {
        u8 wire[32];u32 fields[8];read_exact(wire,sizeof(wire));
        for(unsigned int q=0;q<8;q++)fields[q]=get_unaligned_le32(wire+4*q);
        memcpy(&source.phase[p],fields,sizeof(fields));source.source_id[p]=p;
    }
    saved=source;
    CHECK(e011am_rear_bind_startup_rs(NULL,&source)==-EINVAL);rs_negative_cases++;
    CHECK(e011am_rear_bind_startup_rs(base,NULL)==-EINVAL);rs_negative_cases++;
    CHECK(e011am_rear_bind_startup_rs(base,(const void *)base)==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);rs_negative_cases++;
    CHECK(e011am_rear_bind_startup_rs(base,(const void *)((u8 *)base+1))==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);rs_negative_cases++;
    for(unsigned int p=0;p<3;p++) {
        for(unsigned int q=0;q<8;q++) {
            u32 fields[8];memcpy(fields,&source.phase[p],sizeof(fields));
            fields[q]=q==0?17:q==1?1025:q<4?1:q<6?1:q==6?2:16;
            memcpy(&source.phase[p],fields,sizeof(fields));e011am_host_rejected(base,&source);source=saved;
        }
        source.phase[p].h_num=0;e011am_host_rejected(base,&source);source=saved;
        source.phase[p].v_num=0;e011am_host_rejected(base,&source);source=saved;
        source.phase[p].region_width=8193;e011am_host_rejected(base,&source);source=saved;
        source.phase[p].region_height=18;e011am_host_rejected(base,&source);source=saved;
        source.phase[p].region_height=3;e011am_host_rejected(base,&source);source=saved;
        source.phase[p].shift_bits=(source.phase[p].shift_bits+1)&15;e011am_host_rejected(base,&source);source=saved;
        source.source_id[p]=3;e011am_host_rejected(base,&source);source=saved;
    }
    for(unsigned int p=0;p<4;p++) {
        base[p].ready=true;e011am_host_rejected(base,&source);base[p]=before[p];
        base[p].request_id=0;e011am_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.request_id++;e011am_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.startup_phase=4;e011am_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STEADY;e011am_host_rejected(base,&source);base[p]=before[p];
    }
    base[3].request_id=base[2].request_id;base[3].regs.scalar.request_id=base[2].request_id;
    e011am_host_rejected(base,&source);base[3]=before[3];
    CHECK(e011am_rear_bind_startup_rs(base,&source)==0);
    for(unsigned int p=0;p<4;p++) e011am_rs_apply(&before[p].regs.rs,&source.phase[p<2?p:2]);
    CHECK(memcmp(base,before,bytes)==0);CHECK(memcmp(&source,&saved,sizeof(source))==0);
    CHECK(e011am_rear_runtime_authorization()==-EOPNOTSUPP);
    e011am_host_producer_checks();free(before);
}
