/* SPDX-License-Identifier: MIT */
/*
 * E007w semantic VFE680 IRQ subsample-period provider.
 *
 * Surface Titan680 UpdateSubsampleConfig writes register 0x008c from
 * numBatchedFrames. Only bits [4:0] are semantically produced:
 *
 *   period = numBatchedFrames > 1 ? numBatchedFrames - 1 : 0
 *
 * The Windows binary preserves undefined upper bits from a local stack word.
 * Linux deliberately canonicalizes those non-semantic bits to zero.
 *
 * E007c's two-slot packet-aware state is retained only as a compatibility
 * wrapper for the existing startup materializer. Both slots carry the same
 * canonical semantic register value.
 */

#define E007W_PERIOD_CFG_MASK 0x1f
#define E007W_MAX_BATCHED_FRAMES 32

static int
e007w_period_cfg_value(u32 num_batched_frames, u32 *value)
{
	u32 period;

	if (!value)
		return -EINVAL;
	if (!num_batched_frames || num_batched_frames > E007W_MAX_BATCHED_FRAMES)
		return -EINVAL;

	period = num_batched_frames > 1 ? num_batched_frames - 1 : 0;
	*value = period & E007W_PERIOD_CFG_MASK;
	return 0;
}

static int
e007w_period_cfg_state_init(struct e007c_period_cfg_state *period,
			    u32 num_batched_frames)
{
	u32 value;
	int ret;

	if (!period)
		return -EINVAL;

	ret = e007w_period_cfg_value(num_batched_frames, &value);
	if (ret)
		return ret;

	period->value[0] = value;
	period->value[1] = value;
	period->valid_mask = E007C_PERIOD_VALID_MASK;
	return 0;
}

static int
e007w_rear_startup_context_init(struct e007c_rear_startup_context *ctx,
				void *producer_ctx,
				u32 num_batched_frames)
{
	int ret;

	if (!ctx)
		return -EINVAL;

	ret = e007w_period_cfg_state_init(&ctx->period, num_batched_frames);
	if (ret)
		return ret;

	ctx->producer_ctx = producer_ctx;
	return 0;
}

struct e007w_period_cfg_ops {
	int (*value)(u32 num_batched_frames, u32 *value);
	int (*period_state)(struct e007c_period_cfg_state *period,
			    u32 num_batched_frames);
	int (*startup_context)(struct e007c_rear_startup_context *ctx,
			       void *producer_ctx,
			       u32 num_batched_frames);
};

static const struct e007w_period_cfg_ops e007w_period_cfg_recipe __used = {
	.value = e007w_period_cfg_value,
	.period_state = e007w_period_cfg_state_init,
	.startup_context = e007w_rear_startup_context_init,
};
