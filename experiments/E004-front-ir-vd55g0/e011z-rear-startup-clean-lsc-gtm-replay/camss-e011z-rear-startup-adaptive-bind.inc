/* SPDX-License-Identifier: MIT */
/*
 * E011Z: offline-only adaptive startup binder for E008o packet semantics.
 *
 * This does not create a request identity.  The caller supplies four already
 * coherent non-adaptive E008o packet objects; this helper installs only the
 * clean-produced startup LSC/GTM payloads and preserves each packet's explicit
 * request identity.  No MMIO, DMI submission or runtime entry point exists.
 */
#ifndef VFE680_E011Z_REAR_STARTUP_ADAPTIVE_BIND_INC
#define VFE680_E011Z_REAR_STARTUP_ADAPTIVE_BIND_INC

#define E011Z_LSC_STATES 2

struct e011z_rear_startup_adaptive_wire {
	u8 lsc_selector1[E011Z_LSC_STATES][E006G_LSC_BYTES];
	u8 lsc_selector2[E011Z_LSC_STATES][E006G_LSC_BYTES];
	u8 gtm[E006G_GTM_BYTES];
};

static int
e011z_rear_bind_startup_adaptive(
	struct e008o_rear_semantic_set *set,
	const struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
	const struct e011z_rear_startup_adaptive_wire *wire)
{
	unsigned int p;

	if (!set || !base || !wire)
		return -EINVAL;

	memset(set, 0, sizeof(*set));
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e007q_rear_dmi_state *q;
		struct e007i_rear_dmi_state *i;
		unsigned int lsc_state = p ? 1 : 0;

		if (base[p].request_id < 4)
			return -EINVAL;
		if (base[p].regs.scalar.epoch_kind != E006Z_EPOCH_STARTUP ||
		    base[p].regs.scalar.startup_phase != p ||
		    base[p].regs.scalar.request_id != base[p].request_id)
			return -EPROTO;

		set->packet[p] = base[p];
		set->packet[p].ready = false;

		/*
		 * v -> u -> t -> s -> q -> i.
		 * Recursive E007v validation rebinds all internal callback pointers
		 * after this value-copy, so no pointer from base[] is relied upon.
		 */
		q = &set->packet[p].dmi.dmi.dmi.dmi.dmi;
		i = &q->dmi;

		i->lsc.request_id = set->packet[p].request_id;
		i->lsc.valid_mask = E007I_LSC_VALID_ALL;
		memcpy(i->lsc.selector1, wire->lsc_selector1[lsc_state],
		       E006G_LSC_BYTES);
		memcpy(i->lsc.selector2, wire->lsc_selector2[lsc_state],
		       E006G_LSC_BYTES);

		q->gtm.request_id = set->packet[p].request_id;
		q->gtm.valid_mask = E007Q_GTM_VALID;
		memcpy(q->gtm.payload, wire->gtm, E006G_GTM_BYTES);

		set->packet[p].ready = true;
	}

	set->sealed = true;
	return e008o_rear_validate_semantic_set(set);
}

static int __used e011z_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif
