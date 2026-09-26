/* SPDX-License-Identifier: MIT */
/*
 * E006j compile-only rear dynamic-register producer binding.
 *
 * Generated exclusively from the safe E006h symbolic recipe and E006i
 * ownership closure. No raw Windows command bytes, addresses, pointers or
 * observed dynamic register values are embedded.
 *
 * This file is intentionally unreachable at runtime.
 */

enum e006j_rear_producer {
	E006J_PRODUCER_DEMUX_BLS,
	E006J_PRODUCER_PDPC,
	E006J_PRODUCER_LSC,
	E006J_PRODUCER_WB,
	E006J_PRODUCER_GIC,
	E006J_PRODUCER_BPC_ABF,
	E006J_PRODUCER_GTM,
	E006J_PRODUCER_GAMMA,
	E006J_PRODUCER_DSX,
	E006J_PRODUCER_BFSTATS25,
	E006J_PRODUCER_COUNT,
};

struct e006j_rear_reg_owner {
	u16 reg;
	u8 producer;
};

static const struct e006j_rear_reg_owner e006j_rear_reg_owners[] = {
	{ .reg = 0x3b70, .producer = E006J_PRODUCER_DEMUX_BLS },
	{ .reg = 0x3b74, .producer = E006J_PRODUCER_DEMUX_BLS },
	{ .reg = 0x3d58, .producer = E006J_PRODUCER_PDPC },
	{ .reg = 0x3d5c, .producer = E006J_PRODUCER_PDPC },
	{ .reg = 0x3d7c, .producer = E006J_PRODUCER_PDPC },
	{ .reg = 0x3d84, .producer = E006J_PRODUCER_PDPC },
	{ .reg = 0x4358, .producer = E006J_PRODUCER_LSC },
	{ .reg = 0x435c, .producer = E006J_PRODUCER_LSC },
	{ .reg = 0x456c, .producer = E006J_PRODUCER_WB },
	{ .reg = 0x4758, .producer = E006J_PRODUCER_GIC },
	{ .reg = 0x475c, .producer = E006J_PRODUCER_GIC },
	{ .reg = 0x4958, .producer = E006J_PRODUCER_BPC_ABF },
	{ .reg = 0x495c, .producer = E006J_PRODUCER_BPC_ABF },
	{ .reg = 0x49b8, .producer = E006J_PRODUCER_BPC_ABF },
	{ .reg = 0x49bc, .producer = E006J_PRODUCER_BPC_ABF },
	{ .reg = 0x5a58, .producer = E006J_PRODUCER_GTM },
	{ .reg = 0x5a5c, .producer = E006J_PRODUCER_GTM },
	{ .reg = 0x5f58, .producer = E006J_PRODUCER_GAMMA },
	{ .reg = 0x5f5c, .producer = E006J_PRODUCER_GAMMA },
	{ .reg = 0xa058, .producer = E006J_PRODUCER_DSX },
	{ .reg = 0xa05c, .producer = E006J_PRODUCER_DSX },
	{ .reg = 0xa258, .producer = E006J_PRODUCER_DSX },
	{ .reg = 0xa25c, .producer = E006J_PRODUCER_DSX },
	{ .reg = 0xbc58, .producer = E006J_PRODUCER_BFSTATS25 },
	{ .reg = 0xbc5c, .producer = E006J_PRODUCER_BFSTATS25 },
};

static_assert(ARRAY_SIZE(e006j_rear_reg_owners) == 25);

typedef int (*e006j_scalar_fn)(void *ctx, u16 reg, u32 *value);

struct e006j_rear_scalar_ops {
	e006j_scalar_fn demux_bls;
	e006j_scalar_fn pdpc;
	e006j_scalar_fn lsc;
	e006j_scalar_fn wb;
	e006j_scalar_fn gic;
	e006j_scalar_fn bpc_abf;
	e006j_scalar_fn gtm;
	e006j_scalar_fn gamma;
	e006j_scalar_fn dsx;
	e006j_scalar_fn bfstats25;
};

/*
 * E006g owns DMI/payload production. E006j adds the steady dynamic scalar
 * register side. Keeping them in one bundle makes omission of BPC/ABF411's
 * rear-only 0x49B8/0x49BC words visible to the compiler contract.
 */
struct e006j_rear_producer_bundle {
	struct e006g_rear_producer_ops payload;
	struct e006j_rear_scalar_ops scalar;
};

static e006j_scalar_fn
e006j_rear_scalar_fn_for(const struct e006j_rear_scalar_ops *ops, u8 producer)
{
	if (!ops)
		return NULL;

	switch (producer) {
	case E006J_PRODUCER_DEMUX_BLS:
		return ops->demux_bls;
	case E006J_PRODUCER_PDPC:
		return ops->pdpc;
	case E006J_PRODUCER_LSC:
		return ops->lsc;
	case E006J_PRODUCER_WB:
		return ops->wb;
	case E006J_PRODUCER_GIC:
		return ops->gic;
	case E006J_PRODUCER_BPC_ABF:
		return ops->bpc_abf;
	case E006J_PRODUCER_GTM:
		return ops->gtm;
	case E006J_PRODUCER_GAMMA:
		return ops->gamma;
	case E006J_PRODUCER_DSX:
		return ops->dsx;
	case E006J_PRODUCER_BFSTATS25:
		return ops->bfstats25;
	default:
		return NULL;
	}
}

static int
e006j_rear_validate_scalar_contract(const struct e006j_rear_scalar_ops *ops)
{
	unsigned int i;
	bool saw_49b8 = false;
	bool saw_49bc = false;

	if (!ops)
		return -EINVAL;

	for (i = 0; i < ARRAY_SIZE(e006j_rear_reg_owners); i++) {
		const struct e006j_rear_reg_owner *o = &e006j_rear_reg_owners[i];

		if (i && e006j_rear_reg_owners[i - 1].reg >= o->reg)
			return -EINVAL;
		if (!e006j_rear_scalar_fn_for(ops, o->producer))
			return -EOPNOTSUPP;
		if (o->reg == 0x49b8) {
			if (o->producer != E006J_PRODUCER_BPC_ABF)
				return -EINVAL;
			saw_49b8 = true;
		}
		if (o->reg == 0x49bc) {
			if (o->producer != E006J_PRODUCER_BPC_ABF)
				return -EINVAL;
			saw_49bc = true;
		}
	}

	return saw_49b8 && saw_49bc ? 0 : -EINVAL;
}

static int
e006j_rear_fill_scalar(const struct e006j_rear_scalar_ops *ops,
			void *ctx, u16 reg, u32 *value)
{
	unsigned int i;

	if (!ops || !value)
		return -EINVAL;

	for (i = 0; i < ARRAY_SIZE(e006j_rear_reg_owners); i++) {
		const struct e006j_rear_reg_owner *o = &e006j_rear_reg_owners[i];
		e006j_scalar_fn fn;

		if (o->reg != reg)
			continue;
		fn = e006j_rear_scalar_fn_for(ops, o->producer);
		if (!fn)
			return -EOPNOTSUPP;
		return fn(ctx, reg, value);
	}

	return -ENOENT;
}

struct e006j_rear_binding_static_ops {
	int (*validate_scalar)(const struct e006j_rear_scalar_ops *ops);
	int (*fill_scalar)(const struct e006j_rear_scalar_ops *ops,
			   void *ctx, u16 reg, u32 *value);
};

/* Retention only. There is deliberately no runtime caller. */
static const struct e006j_rear_binding_static_ops
e006j_rear_binding_recipe __used = {
	.validate_scalar = e006j_rear_validate_scalar_contract,
	.fill_scalar = e006j_rear_fill_scalar,
};
