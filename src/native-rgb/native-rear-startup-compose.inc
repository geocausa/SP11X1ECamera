/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Complete integer rear bootstrap composition, without hardware access.
 * Inputs are caller-owned kernel memory supplied by a future typed IPA path.
 * This is configuration validation, not independent tuning or live ISP proof.
 */
#ifndef NATIVE_REAR_STARTUP_COMPOSE_INC
#define NATIVE_REAR_STARTUP_COMPOSE_INC

struct native_rear_packet_adaptive_input {
	u64 request_id;
	u8 phase;
	bool valid;
	u8 lsc1[E006G_LSC_BYTES];
	u8 lsc2[E006G_LSC_BYTES];
	u8 gtm[E006G_GTM_BYTES];
};

struct native_rear_startup_input {
	u64 request_id[E007Y_STARTUP_PACKETS];
	struct native_rear_startup_scalars scalars;
	struct native_rear_geometry_mode geometry;
	struct native_rear_startup_stats_input statistics;
	struct native_rear_startup_iq_input iq;
	struct native_rear_packet_adaptive_input adaptive[E007Y_STARTUP_PACKETS];
};

struct native_rear_startup_work {
	struct native_rear_startup_input input;
	struct e008o_rear_semantic_set pending;
};

/* Value-copying a semantic object invalidates its cached self-pointers.
 * These six known bind functions only reject NULL; all objects exist here.
 * Rebind in outer-to-inner order at the final stable destination address.
 */
static void native_rear_startup_relocate(struct e008o_rear_semantic_set *set)
{
	unsigned int p;

	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e007v_rear_dmi_state *v = &set->packet[p].dmi;
		struct e007u_rear_dmi_state *u = &v->dmi;
		struct e007t_rear_dmi_state *t = &u->dmi;
		struct e007s_rear_dmi_state *s = &t->dmi;
		struct e007q_rear_dmi_state *q = &s->dmi;
		struct e007i_rear_dmi_state *i = &q->dmi;

		(void)e007v_rear_bind(v);
		(void)e007u_rear_bind(u);
		(void)e007t_rear_bind(t);
		(void)e007s_rear_bind(s);
		(void)e007q_rear_bind(q);
		(void)e007i_rear_bind(i);
	}
}

/* Sleepable and exclusively caller-owned; no ISR, userspace pointer or MMIO. */
static int __maybe_unused
native_rear_compose_startup(struct e008o_rear_semantic_set *out,
			    const struct native_rear_startup_input *input)
{
	struct native_rear_startup_work *work;
	unsigned int p;
	int ret;

	if (!out || !input)
		return -EINVAL;
	if (out->sealed)
		return -EBUSY;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
		if (out->packet[p].ready)
			return -EBUSY;
	work = kzalloc(sizeof(*work), GFP_KERNEL);
	if (!work)
		return -ENOMEM;
	work->input = *input;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		const struct native_rear_packet_adaptive_input *a = &work->input.adaptive[p];

		if (work->input.request_id[p] < 4 ||
		    work->input.geometry.request_id[p] != work->input.request_id[p] ||
		    a->request_id != work->input.request_id[p] || a->phase != p) {
			ret = -ESTALE;
			goto out;
		}
		if (!a->valid) {
			ret = -EAGAIN;
			goto out;
		}
		work->pending.packet[p].request_id = work->input.request_id[p];
	}
	ret = native_rear_bind_startup_scalars(work->pending.packet, &work->input.scalars);
	if (ret)
		goto out;
	ret = native_rear_bind_startup_geometry(work->pending.packet, &work->input.geometry);
	if (ret)
		goto out;
	ret = native_rear_bind_startup_statistics(work->pending.packet, &work->input.statistics);
	if (ret)
		goto out;
	ret = native_rear_bind_startup_iq(work->pending.packet, &work->input.iq);
	if (ret)
		goto out;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e008o_rear_packet_semantics *packet = &work->pending.packet[p];
		struct e007q_rear_dmi_state *q = &packet->dmi.dmi.dmi.dmi.dmi;
		struct e007i_rear_dmi_state *i = &q->dmi;
		const struct native_rear_packet_adaptive_input *a = &work->input.adaptive[p];

		i->lsc.request_id = packet->request_id;
		i->lsc.valid_mask = E007I_LSC_VALID_ALL;
		memcpy(i->lsc.selector1, a->lsc1, E006G_LSC_BYTES);
		memcpy(i->lsc.selector2, a->lsc2, E006G_LSC_BYTES);
		q->gtm.request_id = packet->request_id;
		q->gtm.valid_mask = E007Q_GTM_VALID;
		memcpy(q->gtm.payload, a->gtm, E006G_GTM_BYTES);
		packet->ready = true;
	}
	work->pending.sealed = true;
	ret = e008o_rear_validate_semantic_set(&work->pending);
	if (ret)
		goto out;
	/* Commit only after every family and phase has succeeded. */
	*out = work->pending;
	native_rear_startup_relocate(out);
out:
	memzero_explicit(work, sizeof(*work));
	kfree(work);
	return ret;
}
#endif
