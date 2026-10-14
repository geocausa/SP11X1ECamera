/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Source Bayer0 pattern adapter for the retained normal-front proof.
 * Reuse the validated channel fields, gain packing and calibration policy.
 * Source Bayer2 remains unchanged in the previous generic fragment.
 * No activation, private input, MMIO or runtime caller; physical gate remains.
 */
#ifndef SP11_FRONT_CHANNEL_BAYER0_H
#define SP11_FRONT_CHANNEL_BAYER0_H

#include "sp11-front-channel-gain.h"

static inline int
sp11_front_channel_bayer0_config(u8 *out, size_t capacity,
				 const struct sp11_front_cold_policy *policy,
				 const struct sp11_front_channel_gain_state *state)
{
	u8 tmp[SP11_FRONT_CHANNEL_GAIN_CONFIG_BYTES];
	int ret;

	if (!out || !policy || !state)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), state, sizeof(*state)))
		return -EINVAL;
	ret = sp11_front_channel_gain_config(tmp, sizeof(tmp), policy, state);
	if (ret)
		return ret;
	/* Exact source Bayer0 common -> normal-slot packer. */
	sp11_cdm_put32(tmp + 8, 0xc9U);
	sp11_cdm_put32(tmp + 12, 0xacU);
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

static inline int
sp11_front_channel_bayer0_cold_config(u8 *out, size_t capacity,
				      const struct sp11_front_cold_policy *policy)
{
	const struct sp11_front_channel_gain_state state = {
		.gain_q10 = { 1024, 1024, 1024, 1024 },
		.black_in14 = { 0, 0, 0, 0 },
		.black_out14 = { 0, 0, 0, 0 },
	};

	return sp11_front_channel_bayer0_config(out, capacity, policy, &state);
}
#endif
