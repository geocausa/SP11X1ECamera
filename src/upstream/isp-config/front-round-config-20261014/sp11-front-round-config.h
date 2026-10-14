/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Configuration-only reuse of the retained FULL video RoundClamp encoder.
 * Caller must establish the ten-bit video input domain independently.
 * Gamma table precision and a CST clamp tag are not that evidence.
 * No module control, crop, scaler, bus configuration or runtime caller.
 */
#ifndef SP11_FRONT_ROUND_CONFIG_H
#define SP11_FRONT_ROUND_CONFIG_H

#include "sp11-front-fields.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_ROUND_CONFIG_BYTES 96U

static inline int
sp11_front_round_config(u8 *out, size_t capacity,
			const struct sp11_front_cold_policy *policy,
			unsigned int input_bits, unsigned int output_bits)
{
	u8 checked[SP11_FRONT_COLD_BYTES];
	u8 tmp[SP11_FRONT_ROUND_COMMAND_BYTES];
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < SP11_FRONT_ROUND_CONFIG_BYTES)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, SP11_FRONT_ROUND_CONFIG_BYTES, policy,
			     sizeof(*policy)))
		return -EINVAL;
	if (input_bits != 10 || (output_bits != 8 && output_bits != 10))
		return -EOPNOTSUPP;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	ret = sp11_front_round_commands_state(tmp, sizeof(tmp), output_bits,
					      false);
	if (ret)
		return ret;
	/* Each retained plane starts with twelve bytes of module control. */
	memcpy(out, tmp + 12, 48);
	memcpy(out + 48, tmp + 72, 48);
	return 0;
}
#endif
