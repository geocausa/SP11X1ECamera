/* SPDX-License-Identifier: MIT */
/* Host-only checks, independent float source reference and L4 producer. */
#include "../e008z-rear-af-default-rectangle/af-default-rectangle.h"
#include "../e008x-rear-af-bf-roi-map/af-bf-roi-map.h"
static unsigned int af_negative_cases, af_axis_checks, af_map_checks;

static void e011ah_host_inputs(const struct e008o_rear_packet_semantics *base,
                              struct e011ah_request_af_roi normal[3],
                              bool neutral_control)
{
    struct e008z_af_default_inputs in = {
        .camif_width=4064,.camif_height=2286,
        .width_fraction=0.25f,.height_fraction=0.25f,
        .mode_scale=1.0f,.pd_width_scale=1.0f,.pd_height_scale=1.0f,
    };
    u32 bits=0x3f7f3f0f; float first_zoom;
    memcpy(&first_zoom,&bits,sizeof(first_zoom));
    for(unsigned int p=1;p<4;p++) {
        struct e008z_af_rect rect;
        in.zoom=p==1&&!neutral_control?first_zoom:1.0f;
        CHECK(e008z_af_default_rect(&in,&rect)==0);
        normal[p-1]=(struct e011ah_request_af_roi){
            .caller_request_id=base[p].request_id,.startup_phase=p,
            .camif_width=in.camif_width,.camif_height=in.camif_height,
            .af={rect.x,rect.y,rect.width,rect.height},
        };
    }
}

static void e011ah_host_rejected(struct e008o_rear_packet_semantics *base,
                                struct e011ah_request_af_roi normal[3])
{
    const size_t bytes=4*sizeof(*base);
    void *before=malloc(bytes); CHECK(before);memcpy(before,base,bytes);
    CHECK(e011ah_rear_bind_request_af_roi(base,normal)<0);
    CHECK(memcmp(before,base,bytes)==0);free(before);af_negative_cases++;
}

static void e011ah_host_check(struct e008o_rear_packet_semantics *base,
                             bool neutral_control)
{
    struct e011ah_request_af_roi normal[3], saved[3];
    struct e011ah_af_rect mapped[25], old[25];
    struct e008x_roi ref[25];
    const size_t bytes=4*sizeof(*base);
    struct e008o_rear_packet_semantics *before=malloc(bytes);
    CHECK(before);memcpy(before,base,bytes);
    /* Exhaust the full bounded dimension domain for the integer lowering. */
    for(u32 n=0;n<=16384;n++) {
        CHECK((u32)((float)n*(1.0f/5.0f))==n/5U);af_axis_checks++;
    }
    e011ah_host_inputs(base,normal,neutral_control);
    memcpy(saved,normal,sizeof(saved));
    /* Independent E008x float map reference across odd/even rectangles. */
    for(u32 w=30;w<=300;w++) for(u32 h=24;h<=90;h++) {
        struct e011ah_request_af_roi in=normal[2];
        in.af=(struct e011ah_af_rect){1515,855,(u16)w,(u16)h};
        struct e008x_rect rect={in.af.x&~1U,in.af.y&~1U,
            in.af.width&~1U,(in.af.height&~1U)+16U};
        CHECK(e008x_normal_roi_map(rect,ref)==0);
        CHECK(e011ah_map_af_rect(&in,mapped)==0);
        for(unsigned int i=0;i<25;i++)
            CHECK(mapped[i].x==ref[i].left&&mapped[i].y==ref[i].top&&
                  mapped[i].width==ref[i].width&&mapped[i].height==ref[i].height);
        af_map_checks++;
    }
    CHECK(e011ah_rear_bind_request_af_roi(NULL,normal)==-EINVAL);af_negative_cases++;
    CHECK(e011ah_rear_bind_request_af_roi(base,NULL)==-EINVAL);af_negative_cases++;
    CHECK(e011ah_rear_bind_request_af_roi(base,(const void *)base)==-EINVAL);
    CHECK(memcmp(base,before,bytes)==0);af_negative_cases++;
    for(unsigned int p=0;p<4;p++) {
        base[p].ready=true;e011ah_host_rejected(base,normal);base[p]=before[p];
        base[p].request_id=1;e011ah_host_rejected(base,normal);base[p]=before[p];
        base[p].regs.scalar.request_id++;e011ah_host_rejected(base,normal);base[p]=before[p];
        base[p].regs.scalar.startup_phase=4;e011ah_host_rejected(base,normal);base[p]=before[p];
        base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STEADY;e011ah_host_rejected(base,normal);base[p]=before[p];
    }
    base[3].request_id=base[2].request_id;base[3].regs.scalar.request_id=base[2].request_id;
    e011ah_host_rejected(base,normal);base[3]=before[3];
    for(unsigned int p=0;p<3;p++) {
        normal[p].startup_phase=0;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].caller_request_id++;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].camif_width--;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].camif_height--;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].af.x=0;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].af.y=0;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].af.width=0;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].af.height=0;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].af.height=0xffff;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        normal[p].af.width=20;e011ah_host_rejected(base,normal);normal[p]=saved[p];
        e008t_rear_bf_dmi(&base[p+1].dmi)->gamma_valid=false;
        e011ah_host_rejected(base,normal);base[p+1]=before[p+1];
        e008t_rear_bf_dmi(&base[p+1].dmi)->roi_count=24;
        e011ah_host_rejected(base,normal);base[p+1]=before[p+1];
    }
    memset(mapped,0xa5,sizeof(mapped));memcpy(old,mapped,sizeof(old));
    normal[2].af.x=0xffff;
    CHECK(e011ah_map_af_rect(&normal[2],mapped)<0);
    CHECK(memcmp(mapped,old,sizeof(old))==0);af_negative_cases++;
    normal[2]=saved[2];
    CHECK(e011ah_rear_bind_request_af_roi(base,normal)==0);
    CHECK(memcmp(&base[0],&before[0],sizeof(base[0]))==0);
    for(unsigned int p=1;p<4;p++) {
        struct e007e_bf_dmi_state *d=e008t_rear_bf_dmi(&base[p].dmi);
        struct e007e_bf_dmi_state *prior=e008t_rear_bf_dmi(&before[p].dmi);
        CHECK(e011ah_map_af_rect(&normal[p-1],mapped)==0);
        for(unsigned int i=0;i<25;i++) {
            CHECK(d->roi[i].left==mapped[i].x&&d->roi[i].top==mapped[i].y&&
                  d->roi[i].width==mapped[i].width&&d->roi[i].height==mapped[i].height);
            prior->roi[i].left=mapped[i].x;prior->roi[i].top=mapped[i].y;
            prior->roi[i].width=mapped[i].width;prior->roi[i].height=mapped[i].height;
        }
    }
    CHECK(memcmp(base,before,bytes)==0); /* Only normal geometry changed. */
    CHECK(memcmp(normal,saved,sizeof(normal))==0);
    CHECK(e011ah_rear_runtime_authorization()==-EOPNOTSUPP);
    free(before);
}
