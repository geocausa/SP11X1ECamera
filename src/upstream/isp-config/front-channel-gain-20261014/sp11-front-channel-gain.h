/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Normal-slot CHANNEL_GAIN configuration from retained DemuxBLS141 source.
 * Gain packing reuses E006z/native-front-params; no new gain calculation.
 * Source pattern2, period0 and zero initial image are explicit scope.
 * No module activation, DMI, MMIO, private profile or runtime caller.
 */
#ifndef SP11_FRONT_CHANNEL_GAIN_H
#define SP11_FRONT_CHANNEL_GAIN_H

#include "sp11-front-cold-fields.h"

#define SP11_FRONT_CHANNEL_GAIN_CONFIG_BYTES 56U

struct sp11_front_channel_gain_state {
	u32 gain_q10[4];
	/* Public channel register order: CH0 even, CH0 odd, CH1, CH2. */
	u32 black_in14[4];
	u32 black_out14[4];
};

static inline int
sp11_front_channel_gain_config(u8 *out, size_t capacity,
			       const struct sp11_front_cold_policy *policy,
			       const struct sp11_front_channel_gain_state *state)
{
	u32 words[12];
	u8 checked[SP11_FRONT_COLD_BYTES];
	u8 tmp[SP11_FRONT_CHANNEL_GAIN_CONFIG_BYTES];
	unsigned int i;
	int ret;

	if (!out || !policy || !state)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), state, sizeof(*state)))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	for (i = 0; i < 4; i++) {
		/* Same admitted nonzero Q10 domain as the native typed bridge. */
		if (!state->gain_q10[i] || state->gain_q10[i] > 0x7fffU ||
		    state->black_in14[i] > 0x3fffU ||
		    state->black_out14[i] > 0x3fffU)
			return -ERANGE;
	}
	/* Source common calculation's Bayer2 normal-slot patterns. The public
	 * register names differ from the common input's even/odd naming:
	 * CFG0 receives0xca, CFG1 receives0x9c. Do not swap them.
	 */
	words[0] = 0xcaU;
	words[1] = 0x9cU;
	words[2] = (state->gain_q10[0] << 16) | state->gain_q10[1];
	words[3] = (state->gain_q10[3] << 16) | state->gain_q10[2];
	for (i = 0; i < 4; i++) {
		words[4 + i] = state->black_in14[i] << 18;
		words[8 + i] = state->black_out14[i] << 18;
	}
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), 0x3b68U, words, 12);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* Linux-owned unity gains and zero channel offsets; own BLS is separate.
 * This is an independent candidate policy, not equivalence with vendor BLS.
 * Original timing/precision/colour domain and physical parity remain gates.
 */
static inline int
sp11_front_channel_gain_cold_config(u8 *out, size_t capacity,
				    const struct sp11_front_cold_policy *policy)
{
	const struct sp11_front_channel_gain_state state = {
		.gain_q10 = { 1024, 1024, 1024, 1024 },
		.black_in14 = { 0, 0, 0, 0 },
		.black_out14 = { 0, 0, 0, 0 },
	};

	return sp11_front_channel_gain_config(out, capacity, policy, &state);
}
#endif
