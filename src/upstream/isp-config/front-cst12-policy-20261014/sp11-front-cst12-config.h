/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Front12-bit CST configuration policy around the existing complete encoder.
 * Zero suboffsets; independent full-range output policy. No private default.
 * Parent must qualify real Gamma/CST/core precision and optical compatibility.
 * Configuration only: no module command, DMI, MMIO or runtime caller.
 */
#ifndef SP11_FRONT_CST12_CONFIG_H
#define SP11_FRONT_CST12_CONFIG_H

#include "sp11-cst-stats.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_CST12_CONFIG_BYTES 80U
#define SP11_FRONT_CST12_BITS 12U

static inline int
sp11_front_cst12_config(u8 *out, size_t capacity,
			const struct sp11_front_cold_policy *policy,
			const struct sp11_cst_config *state,
			unsigned int gamma_bits)
{
	u8 checked[SP11_FRONT_COLD_BYTES];
	u8 tmp[SP11_CST_COMMAND_BYTES];
	unsigned int i;
	int ret;

	if (!out || !policy || !state)
		return -EINVAL;
	if (capacity < SP11_FRONT_CST12_CONFIG_BYTES)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, SP11_FRONT_CST12_CONFIG_BYTES, policy,
			     sizeof(*policy)) ||
	    sp11_cdm_overlap(out, SP11_FRONT_CST12_CONFIG_BYTES, state,
			     sizeof(*state)))
		return -EINVAL;
	if (gamma_bits != SP11_FRONT_CST12_BITS || state->enabled)
		return -EOPNOTSUPP;
	ret = sp11_cst_validate(state);
	if (ret)
		return ret;
	for (i = 0; i < 3; i++)
		if (state->auxiliary[i] || state->minimum[i] ||
		    state->maximum[i] != (1U << SP11_FRONT_CST12_BITS) - 1 ||
		    state->offset[i] != (i ? 1 << (SP11_FRONT_CST12_BITS - 1) : 0))
			return -EOPNOTSUPP;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	ret = sp11_cst_commands(tmp, sizeof(tmp), state);
	if (ret)
		return ret;
	/* The existing first12-byte command is module control; omit it. */
	memcpy(out, tmp + 12, SP11_FRONT_CST12_CONFIG_BYTES);
	return 0;
}
#endif
