/* SPDX-License-Identifier: MIT */
/*
 * Offline BPC-only composition step. The caller supplies source-produced
 * cold/request1/request2 common states and four independent E008o objects.
 * Request3 holds request2 (E011AB); packet identity is never synthesized.
 * The result is deliberately unsealed until all other semantic gates pass.
 */
#ifndef VFE680_E011AE_REAR_STARTUP_BPC_BIND_INC
#define VFE680_E011AE_REAR_STARTUP_BPC_BIND_INC

struct e011ae_rear_startup_bpc_source {
	struct e007a_bpcabf411_calc_state common[3];
	u64 source_request_id[3];
};

static int
e011ae_rear_bind_startup_bpc(struct e008o_rear_semantic_set *set,
			   const struct e011ae_rear_startup_bpc_source *source)
{
	unsigned int p;
	int ret;

	if (!set || !source)
		return -EINVAL;
	/* Validate the complete domain before mutating any packet. */
	for (p = 0; p < 3; p++) {
		if (source->source_request_id[p] != p)
			return -EPROTO;
		ret = e007a_bpcabf411_validate(&source->common[p]);
		if (ret)
			return ret;
	}
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		const struct e008o_rear_packet_semantics *s = &set->packet[p];

		if (s->request_id < 4)
			return -EINVAL;
		if (s->regs.scalar.epoch_kind != E006Z_EPOCH_STARTUP ||
		    s->regs.scalar.startup_phase != p ||
		    s->regs.scalar.request_id != s->request_id)
			return -EPROTO;
	}
	set->sealed = false;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		set->packet[p].regs.bpcabf = source->common[p < 3 ? p : 2];
		set->packet[p].ready = false;
	}
	return 0;
}

static int __used e011ae_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}
#endif
