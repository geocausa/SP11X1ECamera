/* E011BW invariant source-cold-weights and source-cold-quad host derivative. */
/* SPDX-License-Identifier: MIT */
#include "/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean/experiments/E004-front-ir-vd55g0/e011al-rear-bg-weight-quad-integration/weight-quad-producer.h"
static unsigned int weight_quad_negative_cases,weight_quad_producer_negative_cases;
static void e011al_host_rejected(struct e008o_rear_packet_semantics *base,
    const struct e011al_startup_weight_quad_source *source)
{
    size_t bytes=4*sizeof(*base);void *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    CHECK(e011al_rear_bind_startup_weight_quad(base,source)<0);
    CHECK(memcmp(before,base,bytes)==0);free(before);weight_quad_negative_cases++;
}
static void e011al_host_producer_checks(void)
{
    struct e011al_weight_quad_input good={{0x3e800000,0x3f000000,0x3e800000},1},in;
    struct e011al_weight_quad_output out,before;
    const uint32_t bad[]={0xbf000000,0x3f800001,0x7f800000,0xff800000,0x7fc00000,0xffffffff};
    memset(&out,0xa5,sizeof(out));before=out;
    for(unsigned int j=0;j<3;j++) for(unsigned int k=0;k<6;k++) {
        in=good;in.weight_bits[j]=bad[k];
        CHECK(e011al_produce_weight_quad(&in,&out)==-ERANGE);
        CHECK(memcmp(&out,&before,sizeof(out))==0);weight_quad_producer_negative_cases++;
    }
    for(unsigned int k=0;k<2;k++) {
        in=good;in.awb_quad=k?0xffffffffU:2;
        CHECK(e011al_produce_weight_quad(&in,&out)==-ERANGE);
        CHECK(memcmp(&out,&before,sizeof(out))==0);weight_quad_producer_negative_cases++;
    }
    CHECK(e011al_produce_weight_quad(NULL,&out)==-EINVAL);
    CHECK(memcmp(&out,&before,sizeof(out))==0);weight_quad_producer_negative_cases++;
    CHECK(e011al_produce_weight_quad(&good,NULL)==-EINVAL);weight_quad_producer_negative_cases++;
    CHECK(e011al_produce_weight_quad(&good,&out)==0);
    CHECK(out.aec_weight_q4[0]==4&&out.aec_weight_q4[1]==8&&out.aec_weight_q4[2]==4&&out.awb_quad==1);
    in=good;in.weight_bits[0]=0x3cffffff;in.weight_bits[1]=0x3d000000;in.weight_bits[2]=0x3d000001;
    CHECK(e011al_produce_weight_quad(&in,&out)==0);
    CHECK(out.aec_weight_q4[0]==0&&out.aec_weight_q4[1]==1&&out.aec_weight_q4[2]==1);
    in=good;in.weight_bits[0]=0x80000000;in.weight_bits[1]=1;in.weight_bits[2]=0x3f800000;in.awb_quad=0;
    CHECK(e011al_produce_weight_quad(&in,&out)==0);
    CHECK(out.aec_weight_q4[0]==0&&out.aec_weight_q4[1]==0&&out.aec_weight_q4[2]==16&&!out.awb_quad);
}
static void e011al_host_bind(struct e008o_rear_packet_semantics *base)
{
    struct e011al_startup_weight_quad_source source={0},saved;
    size_t bytes=4*sizeof(*base);struct e008o_rear_packet_semantics *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    for(unsigned int p=0;p<2;p++) read_exact((u8 *)&source.phase[p],4);
    CHECK(source.phase[0].awb_quad==255);
    for(unsigned lane=0;lane<3;lane++) {
        CHECK(source.phase[0].aec_weight_q4[lane]==255);
        source.phase[0].aec_weight_q4[lane]=e011bw_cold_output.aec_weight_q4[lane];
    }
    source.phase[0].awb_quad=e011bw_cold_output.awb_quad;
    source.source_id[0]=0;source.source_id[1]=1;saved=source;
    CHECK(e011al_rear_bind_startup_weight_quad(NULL,&source)==-EINVAL);weight_quad_negative_cases++;
    CHECK(e011al_rear_bind_startup_weight_quad(base,NULL)==-EINVAL);weight_quad_negative_cases++;
    CHECK(e011al_rear_bind_startup_weight_quad(base,(const void *)base)==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);weight_quad_negative_cases++;
    CHECK(e011al_rear_bind_startup_weight_quad(base,(const void *)((u8 *)base+1))==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);weight_quad_negative_cases++;
    for(unsigned int p=0;p<2;p++) {
        for(unsigned int q=0;q<3;q++) {
            source.phase[p].aec_weight_q4[q]=17;e011al_host_rejected(base,&source);source=saved;
        }
        source.phase[p].awb_quad=2;e011al_host_rejected(base,&source);source=saved;
        source.source_id[p]=2;e011al_host_rejected(base,&source);source=saved;
    }
    for(unsigned int p=0;p<4;p++) {
        base[p].ready=true;e011al_host_rejected(base,&source);base[p]=before[p];
        base[p].request_id=0;e011al_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.request_id++;e011al_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.startup_phase=4;e011al_host_rejected(base,&source);base[p]=before[p];
        base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STEADY;e011al_host_rejected(base,&source);base[p]=before[p];
    }
    base[3].request_id=base[2].request_id;base[3].regs.scalar.request_id=base[2].request_id;
    e011al_host_rejected(base,&source);base[3]=before[3];
    CHECK(e011al_rear_bind_startup_weight_quad(base,&source)==0);
    for(unsigned int p=0;p<4;p++) {
        memcpy(before[p].regs.aec_be.y_weight_q4,source.phase[p?1:0].aec_weight_q4,3);
        before[p].regs.awb_bg.quad_sync_enable=source.phase[p?1:0].awb_quad;
    }
    CHECK(memcmp(base,before,bytes)==0);CHECK(memcmp(&source,&saved,sizeof(source))==0);
    CHECK(e011al_rear_runtime_authorization()==-EOPNOTSUPP);
    e011al_host_producer_checks();free(before);
}
