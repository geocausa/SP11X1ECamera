/* SPDX-License-Identifier: MIT */
/*
 * E006z compile-only rear clean scalar + bank providers.
 *
 * No captured Windows register values are embedded.  The scalar state fields
 * are the source-locked outputs of the corresponding common calculations:
 * Demux/BLS Q10-normalized channels, PDPC Q12 AWB ratios, and WB Q10 gains.
 * Live rear 3A/tuning acquisition remains an upstream responsibility.
 */

enum e006z_rear_epoch_kind {
	E006Z_EPOCH_STARTUP = 0,
	E006Z_EPOCH_STEADY,
};

struct e006z_rear_scalar_state {
	u8 epoch_kind;
	u8 startup_phase;
	u16 demux_q10[4];
	u32 pdpc_q12[4];
	u16 wb_b_q10;
	u16 wb_r_q10;
	u64 request_id;
};

static bool e006z_rear_bank_regular(u16 reg)
{
	switch (reg) {
	case 0x3d58:
	case 0x3d5c:
	case 0x4758:
	case 0x475c:
	case 0x4958:
	case 0x495c:
	case 0xa058:
	case 0xa05c:
	case 0xa258:
	case 0xa25c:
		return true;
	default:
		return false;
	}
}

static bool e006z_rear_bank_inverse(u16 reg)
{
	switch (reg) {
	case 0x4358:
	case 0x435c:
	case 0x5a58:
	case 0x5a5c:
	case 0x5f58:
	case 0x5f5c:
		return true;
	default:
		return false;
	}
}

static int e006z_rear_bank_value(const struct e006z_rear_scalar_state *s,
				 u16 reg, u32 *value)
{
	if (!s || !value)
		return -EINVAL;
	if (!e006z_rear_bank_regular(reg) && !e006z_rear_bank_inverse(reg))
		return -ENOENT;

	if (s->epoch_kind == E006Z_EPOCH_STARTUP) {
		if (s->startup_phase > 3)
			return -ERANGE;
		*value = s->startup_phase & 1;
		return 0;
	}
	if (s->epoch_kind != E006Z_EPOCH_STEADY)
		return -EINVAL;

	if (e006z_rear_bank_inverse(reg))
		*value = s->request_id & 1;
	else
		*value = (s->request_id + 1) & 1;
	return 0;
}

static int e006z_rear_clean_scalar_bank_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006z_rear_scalar_state *s = ctx;
	u32 v;

	if (!s || !value)
		return -EINVAL;

	if (e006z_rear_bank_regular(reg) || e006z_rear_bank_inverse(reg))
		return e006z_rear_bank_value(s, reg, value);

	switch (reg) {
	case 0x3b70:
		if (s->demux_q10[0] > 0x7fff || s->demux_q10[1] > 0x7fff)
			return -ERANGE;
		*value = ((u32)s->demux_q10[0] << 16) | s->demux_q10[1];
		return 0;
	case 0x3b74:
		if (s->demux_q10[2] > 0x7fff || s->demux_q10[3] > 0x7fff)
			return -ERANGE;
		*value = ((u32)s->demux_q10[3] << 16) | s->demux_q10[2];
		return 0;
	case 0x3d78:
		v = s->pdpc_q12[0];
		break;
	case 0x3d7c:
		v = s->pdpc_q12[1];
		break;
	case 0x3d80:
		v = s->pdpc_q12[2];
		break;
	case 0x3d84:
		v = s->pdpc_q12[3];
		break;
	case 0x456c:
		if (s->wb_b_q10 > 0x7fff)
			return -ERANGE;
		*value = (u32)s->wb_b_q10 << 17;
		return 0;
	case 0x4570:
		if (s->wb_r_q10 > 0x7fff)
			return -ERANGE;
		*value = (u32)s->wb_r_q10 << 17;
		return 0;
	default:
		return -ENOENT;
	}

	if (v > 0x3ffff)
		return -ERANGE;
	*value = v;
	return 0;
}

static const u16 e006z_rear_closed_regs[] = {
	0x3b70, 0x3b74,
	0x3d58, 0x3d5c, 0x3d78, 0x3d7c, 0x3d80, 0x3d84,
	0x4358, 0x435c,
	0x456c, 0x4570,
	0x4758, 0x475c,
	0x4958, 0x495c,
	0x5a58, 0x5a5c,
	0x5f58, 0x5f5c,
	0xa058, 0xa05c, 0xa258, 0xa25c,
};

static_assert(ARRAY_SIZE(e006z_rear_closed_regs) == 24);

struct e006z_rear_clean_provider_static_ops {
	int (*lookup)(void *ctx, u16 reg, u32 *value);
};

static const struct e006z_rear_clean_provider_static_ops
e006z_rear_clean_provider_recipe __used = {
	.lookup = e006z_rear_clean_scalar_bank_lookup,
};
