/* SPDX-License-Identifier: GPL-2.0-only */
/* Detached L4 geometry/threshold results only. No runtime caller. */
#ifndef VFE680_E011AJ_STARTUP_BG_BIND_INC
#define VFE680_E011AJ_STARTUP_BG_BIND_INC
struct e011aj_bg_values {
    u32 h_num,v_num,h_offset,v_offset,region_width,region_height;
    u32 threshold[4];
};
struct e011aj_startup_bg_source {
    struct e011aj_bg_values aec[2],awb[2];
    u64 source_id[2]; /* cold0, normal1; caller request IDs are independent */
};
static int e011aj_bg_values_validate(const struct e011aj_bg_values *v)
{
    unsigned int i;
    if(!v->h_num||v->h_num>64||!v->v_num||v->v_num>64||
       v->h_offset>0x3ffe||v->v_offset>0x3ffe||
       (v->h_offset&1)||(v->v_offset&1)||
       v->region_width<16||v->region_width>512||
       v->region_height<16||v->region_height>512||
       (v->region_width&1)||(v->region_height&1)) return -ERANGE;
    for(i=0;i<4;i++) if(v->threshold[i]>0x3ffff) return -ERANGE;
    return 0;
}
static void e011aj_bg_apply(struct e006w_aecbe17_state *state,
                           const struct e011aj_bg_values *v)
{
    state->h_num=v->h_num;state->v_num=v->v_num;
    state->h_offset=v->h_offset;state->v_offset=v->v_offset;
    state->region_width=v->region_width;state->region_height=v->region_height;
    state->threshold_r=v->threshold[0];state->threshold_b=v->threshold[1];
    state->threshold_gr=v->threshold[2];state->threshold_gb=v->threshold[3];
}
/* All validation precedes mutation; weights, flags, black level and
 * unrelated modules are preserved. Caller supplies owned serialized state. */
static int e011aj_rear_bind_startup_bg(
    struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
    const struct e011aj_startup_bg_source *source)
{
    unsigned int p,q;
    if(!base||!source||
       e011ag_overlap(base,sizeof(*base)*E007Y_STARTUP_PACKETS,source,sizeof(*source)))
        return -EINVAL;
    for(p=0;p<2;p++) {
        if(source->source_id[p]!=p) return -EINVAL;
        if(e011aj_bg_values_validate(&source->aec[p])||
           e011aj_bg_values_validate(&source->awb[p])) return -ERANGE;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        const struct e006z_rear_scalar_state *tag=&base[p].regs.scalar;
        if(base[p].ready||base[p].request_id<E007Y_STARTUP_PACKETS||
           tag->epoch_kind!=E006Z_EPOCH_STARTUP||tag->startup_phase!=p||
           tag->request_id!=base[p].request_id) return -EINVAL;
        for(q=0;q<p;q++) if(base[q].request_id==base[p].request_id) return -EINVAL;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        e011aj_bg_apply(&base[p].regs.aec_be,&source->aec[p?1:0]);
        e011aj_bg_apply(&base[p].regs.awb_bg,&source->awb[p?1:0]);
    }
    return 0;
}
struct e011aj_rear_bg_ops {
    int (*bind)(struct e008o_rear_packet_semantics *,
                const struct e011aj_startup_bg_source *);
};
static const struct e011aj_rear_bg_ops e011aj_rear_bg_recipe __used = {
    .bind=e011aj_rear_bind_startup_bg,
};
static int __used e011aj_rear_runtime_authorization(void) { return -EOPNOTSUPP; }
#endif
