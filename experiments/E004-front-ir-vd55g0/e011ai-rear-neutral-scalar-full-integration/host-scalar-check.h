/* SPDX-License-Identifier: MIT */
/* Host-only rejection/preservation checks and explicit private source wire. */
#include "scalar-producer.h"
static unsigned int scalar_negative_cases, scalar_producer_negative_cases;
static void e011ai_host_rejected(struct e008o_rear_packet_semantics *base,
                                struct e011ai_startup_scalar_source *source) {
    size_t bytes=4*sizeof(*base);void *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    CHECK(e011ai_rear_bind_startup_scalar(base,source)<0);
    CHECK(memcmp(before,base,bytes)==0);free(before);scalar_negative_cases++;
}
static void e011ai_host_producer_negatives(void) {
    struct e011ai_scalar_inputs in={.demux_gain=1,.awb_g=1,.awb_b=1,.awb_r=1,
        .predictive_gain=1,.bayer=2,.channel={1,1,1,1}};
    struct e011ai_scalar_output out,before;
    memset(&out,0xa5,sizeof(out));before=out;
    float *fields[13]={&in.demux_gain,&in.bls[0],&in.bls[1],&in.bls[2],&in.bls[3],
        &in.channel[0],&in.channel[1],&in.channel[2],&in.channel[3],
        &in.awb_g,&in.awb_b,&in.awb_r,&in.predictive_gain};
    for(unsigned int i=0;i<13;i++) {
        float save=*fields[i];
        const float bad[4]={NAN,INFINITY,-INFINITY,-1.0f};
        for(unsigned int j=0;j<4;j++) {
            *fields[i]=bad[j];
            CHECK(e011ai_produce_scalar(&in,&out)<0);
            CHECK(memcmp(&out,&before,sizeof(out))==0);scalar_producer_negative_cases++;
        }
        *fields[i]=(i>=1&&i<=4)?16383.0f:33.0f;
        CHECK(e011ai_produce_scalar(&in,&out)<0);
        CHECK(memcmp(&out,&before,sizeof(out))==0);scalar_producer_negative_cases++;
        *fields[i]=save;
    }
    in.bayer=0;CHECK(e011ai_produce_scalar(&in,&out)<0);
    CHECK(memcmp(&out,&before,sizeof(out))==0);scalar_producer_negative_cases++;in.bayer=2;
    in.predictive_gain=0;CHECK(e011ai_produce_scalar(&in,&out)<0);
    CHECK(memcmp(&out,&before,sizeof(out))==0);scalar_producer_negative_cases++;in.predictive_gain=1;
    CHECK(e011ai_produce_scalar(NULL,&out)<0);CHECK(memcmp(&out,&before,sizeof(out))==0);scalar_producer_negative_cases++;
    CHECK(e011ai_produce_scalar(&in,NULL)<0);scalar_producer_negative_cases++;
    CHECK(e011ai_produce_scalar(&in,&out)==0);
    for(unsigned int i=0;i<4;i++)CHECK(out.demux_q10[i]==1024&&out.pdpc_q12[i]==4096);
    CHECK(out.wb_b_q10==1024&&out.wb_r_q10==1024);
    in.awb_g=in.awb_b=in.awb_r=0;
    CHECK(e011ai_produce_scalar(&in,&out)==0);
    for(unsigned int i=0;i<4;i++)CHECK(out.pdpc_q12[i]==128);
}
static void e011ai_host_bind(struct e008o_rear_packet_semantics *base) {
    struct e011ai_startup_scalar_source source={0},saved;
    size_t bytes=4*sizeof(*base);
    struct e008o_rear_packet_semantics *before=malloc(bytes);CHECK(before);
    memcpy(before,base,bytes);
    for(unsigned int p=0;p<3;p++) {
        u8 wire[28];read_exact(wire,sizeof(wire));
        for(unsigned int i=0;i<4;i++)
            source.value[p].demux_q10[i]=(u16)wire[2*i]|((u16)wire[2*i+1]<<8);
        for(unsigned int i=0;i<4;i++)
            source.value[p].pdpc_q12[i]=get_unaligned_le32(wire+8+4*i);
        source.value[p].wb_b_q10=(u16)wire[24]|((u16)wire[25]<<8);
        source.value[p].wb_r_q10=(u16)wire[26]|((u16)wire[27]<<8);
        source.source_request_id[p]=p;
    }
    saved=source;
    CHECK(e011ai_rear_bind_startup_scalar(NULL,&source)==-EINVAL);scalar_negative_cases++;
    CHECK(e011ai_rear_bind_startup_scalar(base,NULL)==-EINVAL);scalar_negative_cases++;
    CHECK(e011ai_rear_bind_startup_scalar(base,(const void *)base)==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);scalar_negative_cases++;
    for(unsigned int p=0;p<3;p++) {
        source.source_request_id[p]=3;e011ai_host_rejected(base,&source);source=saved;
        for(unsigned int i=0;i<4;i++) {
            source.value[p].demux_q10[i]=0x8000;e011ai_host_rejected(base,&source);source=saved;
            source.value[p].pdpc_q12[i]=127;e011ai_host_rejected(base,&source);source=saved;
            source.value[p].pdpc_q12[i]=131072;e011ai_host_rejected(base,&source);source=saved;
        }
        source.value[p].wb_b_q10=0x8000;e011ai_host_rejected(base,&source);source=saved;
        source.value[p].wb_r_q10=0x8000;e011ai_host_rejected(base,&source);source=saved;
    }
    for(unsigned int p=0;p<4;p++) {
        base[p].ready=true;e011ai_host_rejected(base,&source);base[p]=before[p];
        base[p].request_id=1;e011ai_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.request_id++;e011ai_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.startup_phase=4;e011ai_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STEADY;e011ai_host_rejected(base,&source);base[p]=before[p];
    }
    base[3].request_id=base[2].request_id;base[3].regs.scalar.request_id=base[2].request_id;
    e011ai_host_rejected(base,&source);base[3]=before[3];
    CHECK(e011ai_rear_bind_startup_scalar(base,&source)==0);
    for(unsigned int p=0;p<4;p++) {
        struct e006z_rear_scalar_state *s=&before[p].regs.scalar;
        const struct e011ai_scalar_values *v=&source.value[p<3?p:2];
        memcpy(s->demux_q10,v->demux_q10,sizeof(s->demux_q10));
        memcpy(s->pdpc_q12,v->pdpc_q12,sizeof(s->pdpc_q12));
        s->wb_b_q10=v->wb_b_q10;s->wb_r_q10=v->wb_r_q10;
    }
    CHECK(memcmp(base,before,bytes)==0);
    CHECK(memcmp(&source,&saved,sizeof(source))==0);
    CHECK(e011ai_rear_runtime_authorization()==-EOPNOTSUPP);
    e011ai_host_producer_negatives();free(before);
}
