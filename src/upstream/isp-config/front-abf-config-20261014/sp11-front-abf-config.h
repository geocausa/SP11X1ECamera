/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Complete ABF configuration from existing own run93 register replacements.
 * No new filter math, vendor default, profile, bank or DMI address.
 * Activation is separate and requires the parent's owned table/lifetime proof.
 */
#ifndef SP11_FRONT_ABF_CONFIG_H
#define SP11_FRONT_ABF_CONFIG_H

#include "native-front-gamma.h"
#include "sp11-front-cold-fields.h"
#include "sp11-front-abf-measured.h"

#define SP11_FRONT_ABF_CONFIG_WORDS 23U
#define SP11_FRONT_ABF_CONFIG_BYTES 124U
#define SP11_FRONT_ABF_ACTIVATE_BYTES 12U

/* Reuse the actual old measured compiler and group its complete owned words
 * according to the original four fixed command blocks. BLS is not included.
 * No alternate geometry or raw register/value input is exposed to the caller.
 */
static inline int
sp11_front_abf_config(u8 *out, size_t capacity,
		      const struct sp11_front_cold_policy *policy)
{
	const u32 bases[] = { 0x4968, 0x4980, 0x49a0, 0x49c8 };
	const unsigned int counts[] = { 2, 4, 8, 9 };
	u8 full[SP11_FRONT_MEASURED_CONFIG_BYTES];
	u8 tmp[SP11_FRONT_ABF_CONFIG_BYTES];
	u8 checked[SP11_FRONT_COLD_BYTES];
	u32 values[9];
	unsigned int block, j, k;
	size_t position = 0;
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	ret = sp11_front_measured_config(full, sizeof(full), &policy->domain);
	if (ret)
		return ret;
	for (block = 0; block < 4; block++) {
		for (j = 0; j < counts[block]; j++) {
			unsigned int found = 0;

			for (k = 0; k < SP11_FRONT_MEASURED_CONFIG_WORDS; k++) {
				const u8 *word = full + k * 12;

				if (nf_gamma_get32(word) != 0x03000001U)
					return -EINVAL;
				if (nf_gamma_get32(word + 4) != bases[block] + j * 4)
					continue;
				values[j] = nf_gamma_get32(word + 8);
				found++;
			}
			if (found != 1)
				return -EINVAL;
		}
		ret = sp11_cdm_reg_cont(tmp + position, sizeof(tmp) - position,
					bases[block], values, counts[block]);
		if (ret)
			return ret;
		position += 8 + counts[block] * 4;
	}
	if (position != sizeof(tmp))
		return -EINVAL;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* Own complete measured control word, not inherited bits. No runtime caller.
 * Parent must establish complete configuration, live immutable ABF DMI,
 * correct banks and ordered activation before submitting this command.
 */
static inline int
sp11_front_abf_activate(u8 *out, size_t capacity,
			const struct sp11_front_cold_policy *policy)
{
	u8 tmp[SP11_FRONT_ABF_ACTIVATE_BYTES];
	u8 checked[SP11_FRONT_COLD_BYTES];
	const u32 module = SP11_FRONT_ABF_MEASURED_MODULE;
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), 0x4960, &module, 1);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
