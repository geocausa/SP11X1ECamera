/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Independent BLS121 IFE18 configuration compiler.
 * Exact constructor -> packer -> command boundary proof: README.md.
 * Linux owns every configuration bit; no prior profile or tuning input.
 * Configuration only: no module-enable command, DMI, MMIO or runtime caller.
 */
#ifndef SP11_FRONT_BLS121_H
#define SP11_FRONT_BLS121_H

#include "sp11-front-cold-fields.h"

#define SP11_BLS121_IFE18_CONFIG_BYTES 32U

struct sp11_bls121_ife18_config {
	u32 offset18;
	u32 gain17;
	/* Hardware THRESHOLD_CFG_0..3 order; no inferred colour names. */
	u32 threshold18[4];
};

/* Fixed IFE18 block. The other selector uses a separate12-bit domain.
 * Bounds and overlap are checked before publishing the complete command.
 */
static inline int
sp11_bls121_ife18_config_encode(u8 *out, size_t capacity,
				const struct sp11_bls121_ife18_config *state)
{
	u8 tmp[SP11_BLS121_IFE18_CONFIG_BYTES];
	u32 words[6];
	unsigned int i;
	int ret;

	if (!out || !state)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), state, sizeof(*state)))
		return -EINVAL;
	if (state->gain17 > 0x1ffffU)
		return -ERANGE;
	ret = sp11_bls121_ife18_offset(state->offset18, &words[0]);
	if (ret)
		return ret;
	words[1] = state->gain17;
	for (i = 0; i < 4; i++) {
		ret = sp11_bls121_ife18_offset(state->threshold18[i],
					       &words[2 + i]);
		if (ret)
			return ret;
	}
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), 0x4b68U, words, 6);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* Reuse the measured integer/gain and independently selected cold thresholds.
 * Fraction0 and native2160->1440 policy remain physically unqualified.
 * Generic field encoding above is not admission to camera hardware.
 */
static inline int
sp11_front_measured_bls121_config(u8 *out, size_t capacity,
				  const struct sp11_front_cold_policy *policy)
{
	const struct sp11_bls121_ife18_config state = {
		.offset18 = 1649U << 2,
		.gain17 = 0x835U,
		.threshold18 = { 0, 0, 0, 0 },
	};
	u8 checked[SP11_FRONT_COLD_BYTES];
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < SP11_BLS121_IFE18_CONFIG_BYTES)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, SP11_BLS121_IFE18_CONFIG_BYTES,
			     policy, sizeof(*policy)))
		return -EINVAL;
	/* Reuse the existing calibrated policy validation; emit only BLS. */
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	return sp11_bls121_ife18_config_encode(out, capacity, &state);
}
#endif
