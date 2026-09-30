/* E011AS additive inactive-gamma derivative; see PROVIDERS.json. */
/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008o: packet-isolated semantic state contract for the four E007y rear
 * startup packets.  This is materialization-only: no MMIO or RT-CDM submit.
 */
#ifndef VFE680_E008O_REAR_PACKET_SEMANTIC_STATE_CONTRACT_INC
#define VFE680_E008O_REAR_PACKET_SEMANTIC_STATE_CONTRACT_INC

struct e008o_rear_packet_semantics {
	struct e007d_rear_register_state regs;
	struct e007v_rear_dmi_state dmi;
	u64 request_id;
	bool ready;
};

struct e008o_rear_semantic_set {
	struct e008o_rear_packet_semantics packet[E007Y_STARTUP_PACKETS];
	bool sealed;
};

static int
e008o_rear_validate_packet_semantics(struct e008o_rear_packet_semantics *s,
				      u8 packet)
{
	struct e007e_bf_dmi_state *bf;
	int ret;

	if (!s || packet >= E007Y_STARTUP_PACKETS || !s->ready)
		return -EINVAL;
	if (s->request_id < 4)
		return -EINVAL;
	bf = &s->dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25;
	/* Source-locked startup policy: cold inactive, normal active. */
	if (!packet) {
		if (s->regs.bfstats.gamma_lut_enable ||
		    !bf->gamma_inactive || bf->gamma_valid)
			return -EPROTO;
	} else if (s->regs.bfstats.gamma_lut_enable != 1 ||
		   bf->gamma_inactive || !bf->gamma_valid) {
		return -EPROTO;
	}

	/*
	 * Startup bank selection is packet-phase state.  Sharing one mutable
	 * e007d state across all four offline materializations is not legal.
	 */
	if (s->regs.scalar.epoch_kind != E006Z_EPOCH_STARTUP ||
	    s->regs.scalar.startup_phase != packet ||
	    s->regs.scalar.request_id != s->request_id)
		return -EPROTO;

	if (s->regs.period.valid_mask != E007C_PERIOD_VALID_MASK)
		return -EINVAL;

	/*
	 * E007v recursively checks request-tagged LSC/GTM handoffs, BFStats DMI
	 * readiness and all stable-DMI provider bindings.  This intentionally
	 * fails closed if the caller has not supplied a real semantic bootstrap.
	 */
	ret = e007v_rear_validate_request(&s->dmi, s->request_id);
	if (ret)
		return ret;

	return 0;
}

static int
e008o_rear_validate_semantic_set(struct e008o_rear_semantic_set *set)
{
	unsigned int p;
	int ret;

	if (!set || !set->sealed)
		return -EINVAL;

	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		ret = e008o_rear_validate_packet_semantics(&set->packet[p], p);
		if (ret)
			return ret;
	}

	return 0;
}

static int
e008o_rear_materialize_commands(struct e008o_rear_semantic_set *set,
				 struct e008l_rear_command_set *commands)
{
	unsigned int p;
	int ret;

	if (!commands || !commands->allocated || commands->hardware_exposed)
		return -EINVAL;

	ret = e008o_rear_validate_semantic_set(set);
	if (ret)
		return ret;

	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e007y_rear_startup_output *out =
			e008l_rear_command_output(commands, p);
		struct e008o_rear_packet_semantics *s = &set->packet[p];

		if (!out)
			return -EINVAL;
		ret = e007y_rear_materialize(&s->regs, &s->dmi,
					     s->request_id, p, out);
		if (ret)
			return ret;
	}

	return 0;
}

struct e008o_rear_semantic_ops {
	int (*validate_packet)(struct e008o_rear_packet_semantics *, u8);
	int (*validate_set)(struct e008o_rear_semantic_set *);
	int (*materialize)(struct e008o_rear_semantic_set *,
			   struct e008l_rear_command_set *);
};

static const struct e008o_rear_semantic_ops
e008o_rear_semantic_recipe __used = {
	.validate_packet = e008o_rear_validate_packet_semantics,
	.validate_set = e008o_rear_validate_semantic_set,
	.materialize = e008o_rear_materialize_commands,
};

static int __used e008o_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif
