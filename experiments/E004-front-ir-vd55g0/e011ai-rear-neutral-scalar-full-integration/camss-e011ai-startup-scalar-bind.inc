/* SPDX-License-Identifier: GPL-2.0-only */
/* Detached L4 scalar results -> L2 startup states. No float or runtime caller. */
#ifndef VFE680_E011AI_STARTUP_SCALAR_BIND_INC
#define VFE680_E011AI_STARTUP_SCALAR_BIND_INC

struct e011ai_scalar_values {
    u16 demux_q10[4];
    u32 pdpc_q12[4];
    u16 wb_b_q10, wb_r_q10;
};
struct e011ai_startup_scalar_source {
    struct e011ai_scalar_values value[3];
    u64 source_request_id[3];
};

/* Source IDs0/1/2 denote independently observed cold/request1/request2
 * calculations; caller packet IDs are separate. Packet3 holds source2.
 * Rejected tags, aliases and values preserve all four detached inputs.
 * Caller guarantees valid owned objects, serialization and no exposed arena. */
static int e011ai_rear_bind_startup_scalar(
    struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
    const struct e011ai_startup_scalar_source *source)
{
    unsigned int p,i,q;
    if(!base||!source||
       e011ag_overlap(base,sizeof(*base)*E007Y_STARTUP_PACKETS,source,sizeof(*source)))
        return -EINVAL;
    for(p=0;p<3;p++) {
        const struct e011ai_scalar_values *v=&source->value[p];
        if(source->source_request_id[p]!=p)
            return -EINVAL;
        for(i=0;i<4;i++)
            if(v->demux_q10[i]>0x7fff||v->pdpc_q12[i]<128||
               v->pdpc_q12[i]>131071)
                return -ERANGE;
        if(v->wb_b_q10>0x7fff||v->wb_r_q10>0x7fff)
            return -ERANGE;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        const struct e006z_rear_scalar_state *v=&base[p].regs.scalar;
        if(base[p].ready||base[p].request_id<E007Y_STARTUP_PACKETS||
           v->epoch_kind!=E006Z_EPOCH_STARTUP||v->startup_phase!=p||
           v->request_id!=base[p].request_id)
            return -EINVAL;
        for(q=0;q<p;q++)
            if(base[q].request_id==base[p].request_id)
                return -EINVAL;
    }
    for(p=0;p<E007Y_STARTUP_PACKETS;p++) {
        struct e006z_rear_scalar_state *v=&base[p].regs.scalar;
        const struct e011ai_scalar_values *src=&source->value[p<3?p:2];
        memcpy(v->demux_q10,src->demux_q10,sizeof(v->demux_q10));
        memcpy(v->pdpc_q12,src->pdpc_q12,sizeof(v->pdpc_q12));
        v->wb_b_q10=src->wb_b_q10;v->wb_r_q10=src->wb_r_q10;
    }
    return 0;
}
struct e011ai_rear_scalar_ops {
    int (*bind)(struct e008o_rear_packet_semantics *,
                const struct e011ai_startup_scalar_source *);
};
static const struct e011ai_rear_scalar_ops e011ai_rear_scalar_recipe __used = {
    .bind=e011ai_rear_bind_startup_scalar,
};
static int __used e011ai_rear_runtime_authorization(void) { return -EOPNOTSUPP; }
#endif
