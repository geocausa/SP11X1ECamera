/* SPDX-License-Identifier: MIT */
/*
 * E006g compile-only rear RT-CDM materializer contract.
 *
 * Generated from E006a safe structural decode plus E006d/E006f producer
 * classifications. No Windows payload bytes, pointers or IOVAs are present.
 * This include is intentionally retained but unreachable: no probe, stream,
 * ioctl, RT-CDM submit, MMIO write or module-init path references it.
 */

enum e006g_rear_payload_kind {
	E006G_PAYLOAD_STABLE = 0,
	E006G_PAYLOAD_LSC,
	E006G_PAYLOAD_LSC_GIC_ALIAS,
	E006G_PAYLOAD_GTM,
	E006G_PAYLOAD_BF_ROI,
	E006G_PAYLOAD_BF_GAMMA,
};

struct e006g_rear_dmi_slot {
	u16 dmi_reg;
	u16 payload_bytes;
	u8 selector;
	u8 kind;
};

struct e006g_rear_variant {
	u16 main_bytes;
	u8 dmi_count;
	const struct e006g_rear_dmi_slot *slots;
};

struct e006g_rear_bl_shape {
	u16 len[6];
	u8 count;
};

#define E006G_SLOT(_reg, _sel, _bytes, _kind) \
	{ .dmi_reg = (_reg), .selector = (_sel), .payload_bytes = (_bytes), .kind = (_kind) }

static const struct e006g_rear_dmi_slot e006g_rear_ac8_slots[] = {
	E006G_SLOT(0x3d08, 1, 512, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x4308, 1, 884, E006G_PAYLOAD_LSC),
	E006G_SLOT(0x4308, 2, 884, E006G_PAYLOAD_LSC),
	E006G_SLOT(0x4308, 3, 884, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x4708, 1, 512, E006G_PAYLOAD_LSC_GIC_ALIAS),
	E006G_SLOT(0x4908, 1, 256, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5a08, 1, 2048, E006G_PAYLOAD_GTM),
	E006G_SLOT(0x5f08, 1, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5f08, 2, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5f08, 3, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa008, 1, 768, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa008, 2, 768, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa208, 1, 384, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa208, 2, 384, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xbc08, 1, 300, E006G_PAYLOAD_BF_ROI),
	E006G_SLOT(0xbc08, 2, 128, E006G_PAYLOAD_BF_GAMMA),
};

static const struct e006g_rear_dmi_slot e006g_rear_a98_slots[] = {
	E006G_SLOT(0x3d08, 1, 512, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x4308, 1, 884, E006G_PAYLOAD_LSC),
	E006G_SLOT(0x4308, 2, 884, E006G_PAYLOAD_LSC),
	E006G_SLOT(0x4308, 3, 884, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x4908, 1, 256, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5a08, 1, 2048, E006G_PAYLOAD_GTM),
	E006G_SLOT(0x5f08, 1, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5f08, 2, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5f08, 3, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa008, 1, 768, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa008, 2, 768, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa208, 1, 384, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa208, 2, 384, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xbc08, 1, 300, E006G_PAYLOAD_BF_ROI),
	E006G_SLOT(0xbc08, 2, 128, E006G_PAYLOAD_BF_GAMMA),
};

static const struct e006g_rear_dmi_slot e006g_rear_8f0_slots[] = {
	E006G_SLOT(0x4308, 1, 884, E006G_PAYLOAD_LSC),
	E006G_SLOT(0x4308, 2, 884, E006G_PAYLOAD_LSC),
	E006G_SLOT(0x4308, 3, 884, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5a08, 1, 2048, E006G_PAYLOAD_GTM),
	E006G_SLOT(0x5f08, 1, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5f08, 2, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0x5f08, 3, 1024, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa008, 1, 768, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa008, 2, 768, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa208, 1, 384, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xa208, 2, 384, E006G_PAYLOAD_STABLE),
	E006G_SLOT(0xbc08, 1, 300, E006G_PAYLOAD_BF_ROI),
	E006G_SLOT(0xbc08, 2, 128, E006G_PAYLOAD_BF_GAMMA),
};

static const struct e006g_rear_dmi_slot e006g_rear_658_slots[] = {
	E006G_SLOT(0x5a08, 1, 2048, E006G_PAYLOAD_GTM),
	E006G_SLOT(0xbc08, 1, 300, E006G_PAYLOAD_BF_ROI),
	E006G_SLOT(0xbc08, 2, 128, E006G_PAYLOAD_BF_GAMMA),
};

static_assert(ARRAY_SIZE(e006g_rear_ac8_slots) == 16);
static_assert(ARRAY_SIZE(e006g_rear_a98_slots) == 15);
static_assert(ARRAY_SIZE(e006g_rear_8f0_slots) == 13);
static_assert(ARRAY_SIZE(e006g_rear_658_slots) == 3);

static const struct e006g_rear_variant e006g_rear_variants[] = {
	{ .main_bytes = 0x0ac8, .dmi_count = ARRAY_SIZE(e006g_rear_ac8_slots),
	  .slots = e006g_rear_ac8_slots },
	{ .main_bytes = 0x0a98, .dmi_count = ARRAY_SIZE(e006g_rear_a98_slots),
	  .slots = e006g_rear_a98_slots },
	{ .main_bytes = 0x08f0, .dmi_count = ARRAY_SIZE(e006g_rear_8f0_slots),
	  .slots = e006g_rear_8f0_slots },
	{ .main_bytes = 0x0658, .dmi_count = ARRAY_SIZE(e006g_rear_658_slots),
	  .slots = e006g_rear_658_slots },
};

static const struct e006g_rear_bl_shape e006g_rear_startup_bl[] = {
	{ .len = { 0x4, 0xf1c, 0x4, 0x3c }, .count = 4 },
	{ .len = { 0x4, 0xebc, 0xc, 0x4, 0x10, 0x14 }, .count = 6 },
	{ .len = { 0x4, 0xa00, 0xc, 0x4, 0x10, 0x14 }, .count = 6 },
	{ .len = { 0x4, 0x658, 0xc, 0x4, 0x10, 0x14 }, .count = 6 },
};

static_assert(ARRAY_SIZE(e006g_rear_startup_bl) == 4);

/*
 * Boundary to accepted producer families:
 *  - lsc: stateful LSC411/Tintless producer;
 *  - gtm: request-time GTM131/TMC producer;
 *  - bfstats: BFStats25 AF-request ROI/gamma producer;
 *  - stable: independently-derived stable payload provider.
 *
 * The kernel skeleton does not implement those algorithms or ingest raw
 * Windows payloads. The explicit contract prevents stale snapshot replay.
 */
struct e006g_rear_producer_ops {
	int (*lsc)(void *ctx, u8 selector, u8 *dst, size_t bytes);
	int (*gtm)(void *ctx, u8 *dst, size_t bytes);
	int (*bfstats)(void *ctx, u8 selector, u8 *dst, size_t bytes);
	int (*stable)(void *ctx, u16 dmi_reg, u8 selector, u8 *dst, size_t bytes);
};

#define E006G_LSC_BYTES         884
#define E006G_GIC_BYTES         512
#define E006G_GIC_LSC0_OFFSET   558
#define E006G_GIC_LSC0_BYTES    326
#define E006G_GIC_LSC1_BYTES    186
#define E006G_GTM_BYTES         2048
#define E006G_BF_ROI_BYTES      300
#define E006G_BF_GAMMA_BYTES    128

static_assert(E006G_GIC_LSC0_BYTES + E006G_GIC_LSC1_BYTES == E006G_GIC_BYTES);
static_assert(E006G_GIC_LSC0_OFFSET + E006G_GIC_LSC0_BYTES == E006G_LSC_BYTES);

struct e006g_rear_dynamic_payloads {
	u8 lsc1[E006G_LSC_BYTES];
	u8 lsc2[E006G_LSC_BYTES];
	u8 gic_alias[E006G_GIC_BYTES];
	u8 gtm[E006G_GTM_BYTES];
	u8 bf_roi[E006G_BF_ROI_BYTES];
	u8 bf_gamma[E006G_BF_GAMMA_BYTES];
	bool materialized;
};

struct e006g_rear_slot_buffer {
	u8 *cpu;
	size_t bytes;
};

static int e006g_rear_validate_contract(void)
{
	unsigned int v, i;

	for (v = 0; v < ARRAY_SIZE(e006g_rear_variants); v++) {
		const struct e006g_rear_variant *variant = &e006g_rear_variants[v];

		if (!variant->slots || !variant->dmi_count || !variant->main_bytes)
			return -EINVAL;
		for (i = 0; i < variant->dmi_count; i++) {
			const struct e006g_rear_dmi_slot *s = &variant->slots[i];

			if (!s->dmi_reg || !s->selector || !s->payload_bytes)
				return -EINVAL;
			switch (s->kind) {
			case E006G_PAYLOAD_STABLE:
				break;
			case E006G_PAYLOAD_LSC:
				if (s->dmi_reg != 0x4308 ||
				    (s->selector != 1 && s->selector != 2) ||
				    s->payload_bytes != E006G_LSC_BYTES)
					return -EINVAL;
				break;
			case E006G_PAYLOAD_LSC_GIC_ALIAS:
				if (s->dmi_reg != 0x4708 || s->selector != 1 ||
				    s->payload_bytes != E006G_GIC_BYTES)
					return -EINVAL;
				break;
			case E006G_PAYLOAD_GTM:
				if (s->dmi_reg != 0x5a08 || s->selector != 1 ||
				    s->payload_bytes != E006G_GTM_BYTES)
					return -EINVAL;
				break;
			case E006G_PAYLOAD_BF_ROI:
				if (s->dmi_reg != 0xbc08 || s->selector != 1 ||
				    s->payload_bytes != E006G_BF_ROI_BYTES)
					return -EINVAL;
				break;
			case E006G_PAYLOAD_BF_GAMMA:
				if (s->dmi_reg != 0xbc08 || s->selector != 2 ||
				    s->payload_bytes != E006G_BF_GAMMA_BYTES)
					return -EINVAL;
				break;
			default:
				return -EINVAL;
			}
		}
	}

	return 0;
}

static int e006g_rear_prepare_dynamic(const struct e006g_rear_producer_ops *ops,
				      void *ctx,
				      struct e006g_rear_dynamic_payloads *out)
{
	int ret;

	if (!ops || !ops->lsc || !ops->gtm || !ops->bfstats || !out ||
	    out->materialized)
		return -EINVAL;

	ret = ops->lsc(ctx, 1, out->lsc1, sizeof(out->lsc1));
	if (ret)
		return ret;
	ret = ops->lsc(ctx, 2, out->lsc2, sizeof(out->lsc2));
	if (ret)
		goto err_zero;

	/* Exact Surface/Titan680 GIC wire alias proven in E006d. */
	memcpy(out->gic_alias, out->lsc1 + E006G_GIC_LSC0_OFFSET,
	       E006G_GIC_LSC0_BYTES);
	memcpy(out->gic_alias + E006G_GIC_LSC0_BYTES, out->lsc2,
	       E006G_GIC_LSC1_BYTES);

	ret = ops->gtm(ctx, out->gtm, sizeof(out->gtm));
	if (ret)
		goto err_zero;
	ret = ops->bfstats(ctx, 1, out->bf_roi, sizeof(out->bf_roi));
	if (ret)
		goto err_zero;
	ret = ops->bfstats(ctx, 2, out->bf_gamma, sizeof(out->bf_gamma));
	if (ret)
		goto err_zero;

	out->materialized = true;
	return 0;

err_zero:
	memzero_explicit(out, sizeof(*out));
	return ret;
}

static int e006g_rear_fill_slot(const struct e006g_rear_producer_ops *ops,
				void *ctx,
				const struct e006g_rear_dynamic_payloads *dyn,
				const struct e006g_rear_dmi_slot *slot,
				struct e006g_rear_slot_buffer *out)
{
	const u8 *src = NULL;

	if (!ops || !dyn || !dyn->materialized || !slot || !out || !out->cpu ||
	    out->bytes != slot->payload_bytes)
		return -EINVAL;

	switch (slot->kind) {
	case E006G_PAYLOAD_STABLE:
		if (!ops->stable)
			return -EOPNOTSUPP;
		return ops->stable(ctx, slot->dmi_reg, slot->selector,
				   out->cpu, out->bytes);
	case E006G_PAYLOAD_LSC:
		src = slot->selector == 1 ? dyn->lsc1 : dyn->lsc2;
		break;
	case E006G_PAYLOAD_LSC_GIC_ALIAS:
		src = dyn->gic_alias;
		break;
	case E006G_PAYLOAD_GTM:
		src = dyn->gtm;
		break;
	case E006G_PAYLOAD_BF_ROI:
		src = dyn->bf_roi;
		break;
	case E006G_PAYLOAD_BF_GAMMA:
		src = dyn->bf_gamma;
		break;
	default:
		return -EINVAL;
	}

	memcpy(out->cpu, src, out->bytes);
	return 0;
}

static int e006g_rear_steady_bl_shape(const struct e006g_rear_variant *variant,
				      struct e006g_rear_bl_shape *out)
{
	if (!variant || !out)
		return -EINVAL;

	memset(out, 0, sizeof(*out));
	out->len[0] = 0x4;
	out->len[1] = variant->main_bytes;
	out->len[2] = 0xc;
	out->len[3] = 0x4;
	out->len[4] = 0x10;
	out->len[5] = 0x14;
	out->count = 6;
	return 0;
}

struct e006g_rear_materializer_static_ops {
	int (*validate)(void);
	int (*prepare_dynamic)(const struct e006g_rear_producer_ops *ops,
			       void *ctx, struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(const struct e006g_rear_producer_ops *ops, void *ctx,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
	int (*steady_bl_shape)(const struct e006g_rear_variant *variant,
			       struct e006g_rear_bl_shape *out);
};

/* Retention only. There is deliberately no runtime caller. */
static const struct e006g_rear_materializer_static_ops
e006g_rear_materializer_recipe __used = {
	.validate = e006g_rear_validate_contract,
	.prepare_dynamic = e006g_rear_prepare_dynamic,
	.fill_slot = e006g_rear_fill_slot,
	.steady_bl_shape = e006g_rear_steady_bl_shape,
};
