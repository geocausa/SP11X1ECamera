/* SPDX-License-Identifier: GPL-2.0-only */
/* Detached bounded whole-frame RS results; no runtime caller. */
#ifndef VFE680_E011AM_STARTUP_RS_BIND_INC
#define VFE680_E011AM_STARTUP_RS_BIND_INC
struct e011am_rs_values {
    u32 h_num,v_num,region_width,region_height,h_offset,v_offset;
    u32 color_conversion,shift_bits;
};
struct e011am_startup_rs_source {
    struct e011am_rs_values phase[3];
    u64 source_id[3]; /* cold0, first normal1, second normal2 */
};
static int e011am_rs_values_validate(const struct e011am_rs_values *v)
{
    if(!v->h_num||v->h_num>16||!v->v_num||v->v_num>1024||
       v->region_width<2||v->region_width>8192||
       v->region_height<2||v->region_height>16||(v->region_height&1)||
       v->h_offset||v->v_offset||v->color_conversion>1||v->shift_bits>15||
       v->shift_bits!=e006v_rs14_shift_bits(v->region_width,v->region_height))
        return -ERANGE;
    return 0;
}
static void e011am_rs_apply(struct e006v_rs14_state *state,
                           const struct e011am_rs_values *v)
{
    state->h_num=v->h_num;state->v_num=v->v_num;
    state->region_width=v->region_width;state->region_height=v->region_height;
    state->h_offset=v->h_offset;state->v_offset=v->v_offset;
    state->color_conversion=v->color_conversion;
    state->enabled=true; /* original RS packer enables independently */
}
static int e011am_rear_bind_startup_rs(
    struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
    const struct e011am_startup_rs_source *source)
{
    unsigned int p,q;
    if(!base||!source||
       e011ag_overlap(base,sizeof(*base)*E007Y_STARTUP_PACKETS,source,sizeof(*source)))
        return -EINVAL;
    for(p=0;p<3;p++) {
        if(source->source_id[p]!=p) return -EINVAL;
        if(e011am_rs_values_validate(&source->phase[p])) return -ERANGE;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        const struct e006z_rear_scalar_state *tag=&base[p].regs.scalar;
        if(base[p].ready||base[p].request_id<E007Y_STARTUP_PACKETS||
           tag->epoch_kind!=E006Z_EPOCH_STARTUP||tag->startup_phase!=p||
           tag->request_id!=base[p].request_id) return -EINVAL;
        for(q=0;q<p;q++) if(base[q].request_id==base[p].request_id) return -EINVAL;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++)
        e011am_rs_apply(&base[p].regs.rs,&source->phase[p<2?p:2]);
    return 0;
}
struct e011am_rear_rs_ops {
    int (*bind)(struct e008o_rear_packet_semantics *,const struct e011am_startup_rs_source *);
};
static const struct e011am_rear_rs_ops e011am_rear_rs_recipe __used={
    .bind=e011am_rear_bind_startup_rs,
};
static int __used e011am_rear_runtime_authorization(void) { return -EOPNOTSUPP; }
#endif
