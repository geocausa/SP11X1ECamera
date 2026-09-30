/* SPDX-License-Identifier: GPL-2.0-only */
/* Detached integer results only; cold input authority remains caller-owned. */
#ifndef VFE680_E011AL_STARTUP_WEIGHT_QUAD_BIND_INC
#define VFE680_E011AL_STARTUP_WEIGHT_QUAD_BIND_INC
struct e011al_weight_quad_values { u8 aec_weight_q4[3],awb_quad; };
struct e011al_startup_weight_quad_source {
    struct e011al_weight_quad_values phase[2];
    u64 source_id[2]; /* cold0, normal1; independent of caller request IDs */
};
static int e011al_rear_bind_startup_weight_quad(
    struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
    const struct e011al_startup_weight_quad_source *source)
{
    unsigned int p,q;
    if(!base||!source||
       e011ag_overlap(base,sizeof(*base)*E007Y_STARTUP_PACKETS,source,sizeof(*source)))
        return -EINVAL;
    for(p=0;p<2;p++) {
        if(source->source_id[p]!=p) return -EINVAL;
        if(source->phase[p].awb_quad>1) return -ERANGE;
        for(q=0;q<3;q++) if(source->phase[p].aec_weight_q4[q]>16) return -ERANGE;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        const struct e006z_rear_scalar_state *tag=&base[p].regs.scalar;
        if(base[p].ready||base[p].request_id<E007Y_STARTUP_PACKETS||
           tag->epoch_kind!=E006Z_EPOCH_STARTUP||tag->startup_phase!=p||
           tag->request_id!=base[p].request_id) return -EINVAL;
        for(q=0;q<p;q++) if(base[q].request_id==base[p].request_id) return -EINVAL;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        const struct e011al_weight_quad_values *v=&source->phase[p?1:0];
        for(q=0;q<3;q++) base[p].regs.aec_be.y_weight_q4[q]=v->aec_weight_q4[q];
        base[p].regs.awb_bg.quad_sync_enable=v->awb_quad;
    }
    return 0;
}
struct e011al_rear_weight_quad_ops {
    int (*bind)(struct e008o_rear_packet_semantics *,
                const struct e011al_startup_weight_quad_source *);
};
static const struct e011al_rear_weight_quad_ops e011al_rear_weight_quad_recipe __used={
    .bind=e011al_rear_bind_startup_weight_quad,
};
static int __used e011al_rear_runtime_authorization(void) { return -EOPNOTSUPP; }
#endif
