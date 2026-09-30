/* SPDX-License-Identifier: GPL-2.0-only */
/* Explicit absent cold BF gamma; no table is invented or produced. */
#ifndef CAMSS_E011AS_COLD_GAMMA_POLICY_INC
#define CAMSS_E011AS_COLD_GAMMA_POLICY_INC
static int
e011as_rear_mark_cold_gamma_inactive(struct e008o_rear_packet_semantics *p)
{
	struct e007e_bf_dmi_state *bf;
	unsigned int i;

	if (!p || p->request_id < 4 ||
	    p->regs.scalar.epoch_kind != E006Z_EPOCH_STARTUP ||
	    p->regs.scalar.startup_phase ||
	    p->regs.scalar.request_id != p->request_id ||
	    p->regs.bfstats.gamma_lut_enable)
		return -EINVAL;
	bf = &p->dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25;
	if (bf->gamma_valid)
		return -EINVAL;
	for (i = 0; i < E007E_BF_GAMMA_COUNT; i++)
		if (bf->gamma[i])
			return -EINVAL;
	/* All gates precede the only mutation; ROI and other modules survive. */
	bf->gamma_inactive = true;
	return 0;
}
struct e011as_rear_gamma_policy_ops {
	int (*mark_cold_inactive)(struct e008o_rear_packet_semantics *);
};
static const struct e011as_rear_gamma_policy_ops e011as_rear_gamma_policy_recipe __used = {
	.mark_cold_inactive = e011as_rear_mark_cold_gamma_inactive,
};
static int __used e011as_rear_gamma_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}
#endif
