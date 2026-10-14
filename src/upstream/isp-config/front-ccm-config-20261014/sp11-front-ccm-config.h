/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Complete configuration around the retained Q7 coefficient encoder.
 * Canonicalize its thirteen-bit sign-fill to actual CC131 twelve-bit fields.
 * Source common calculation uses fractional bits = scale control + seven.
 * Own zero offsets and Q7/control-zero policy; no inherited defaults.
 * No module control, DMI, MMIO, allocation or runtime caller.
 */
#ifndef SP11_FRONT_CCM_CONFIG_H
#define SP11_FRONT_CCM_CONFIG_H

#include "sp11-front-fields.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_CCM_CONFIG_BYTES 48U

struct sp11_front_ccm_state {
	s16 matrix[9];
	s16 offset[3];
	u32 fractional_bits;
};

static inline int
sp11_front_ccm_config(u8 *out, size_t capacity,
		      const struct sp11_front_cold_policy *policy,
		      const struct sp11_front_ccm_state *state)
{
	u8 checked[SP11_FRONT_COLD_BYTES];
	u8 coefficients[SP11_FRONT_CCM_COMMAND_BYTES];
	u8 tmp[SP11_FRONT_CCM_CONFIG_BYTES] = { 0 };
	unsigned int i;
	int ret;

	if (!out || !policy || !state)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), state, sizeof(*state)))
		return -EINVAL;
	if (state->fractional_bits != 7)
		return -EOPNOTSUPP;
	for (i = 0; i < 3; i++)
		if (state->offset[i])
			return -EOPNOTSUPP;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	ret = sp11_front_ccm_commands(coefficients, sizeof(coefficients),
				      state->matrix);
	if (ret)
		return ret;
	sp11_cdm_put32(tmp, 0x0300000aU);
	sp11_cdm_put32(tmp + 4, 0x5868U);
	memcpy(tmp + 8, coefficients + 8, 24);
	/* Retained signed values fit twelve bits; discard extra sign-fill. */
	for (i = 0; i < 6; i++) {
		tmp[8 + 4 * i + 1] &= 0x0fU;
		tmp[8 + 4 * i + 3] &= 0x0fU;
	}
	/* Three offsets and scale control remain own explicit zero policy. */
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
