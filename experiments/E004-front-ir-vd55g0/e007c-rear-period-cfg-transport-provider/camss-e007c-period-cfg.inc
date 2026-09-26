/* SPDX-License-Identifier: MIT */
/*
 * E007c compile-only VFE680 PERIOD_CFG transport-state provider.
 *
 * Windows proves that register 0x008c is populated upstream of the KMD
 * transport and is not mutated by qccamisp's downstream start handling.
 * Packet 0 consumes one opaque caller value; packets 1/2/3 consume a second
 * shared opaque caller value. No captured Windows value is embedded here.
 */

#define E007C_PERIOD_CFG_REG 0x008c
#define E007C_PERIOD_CFG_VALUES 2
#define E007C_STARTUP_PACKETS 4
#define E007C_PERIOD_VALID_MASK 0x3

struct e007c_period_cfg_state {
	u32 value[E007C_PERIOD_CFG_VALUES];
	u32 valid_mask;
};

struct e007c_rear_startup_context {
	void *producer_ctx;
	struct e007c_period_cfg_state period;
};

static int
e007c_period_cfg_lookup(const struct e007c_period_cfg_state *s,
			u8 packet, u16 reg, u32 *value)
{
	unsigned int index;

	if (!s || !value)
		return -EINVAL;
	if (reg != E007C_PERIOD_CFG_REG)
		return -ENOENT;
	if (packet >= E007C_STARTUP_PACKETS)
		return -EINVAL;
	if (s->valid_mask != E007C_PERIOD_VALID_MASK)
		return -EINVAL;

	index = packet ? 1 : 0;
	*value = s->value[index];
	return 0;
}

static int
e007c_rear_fill_startup_packet(const struct e006m_rear_startup_bundle *b,
			       struct e007c_rear_startup_context *ctx,
			       u8 packet, u16 reg, u32 *value)
{
	if (!ctx || !value)
		return -EINVAL;

	if (reg == E007C_PERIOD_CFG_REG)
		return e007c_period_cfg_lookup(&ctx->period, packet, reg, value);

	return e006m_rear_fill_startup_scalar(b, ctx->producer_ctx, reg, value);
}

struct e007c_rear_startup_packet_ops {
	int (*period)(const struct e007c_period_cfg_state *s,
		      u8 packet, u16 reg, u32 *value);
	int (*fill)(const struct e006m_rear_startup_bundle *b,
		    struct e007c_rear_startup_context *ctx,
		    u8 packet, u16 reg, u32 *value);
};

static const struct e007c_rear_startup_packet_ops
e007c_rear_startup_packet_recipe __used = {
	.period = e007c_period_cfg_lookup,
	.fill = e007c_rear_fill_startup_packet,
};
