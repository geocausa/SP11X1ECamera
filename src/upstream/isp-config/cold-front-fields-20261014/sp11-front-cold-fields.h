/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Independent cold-state fragment, from retained exact Titan680 field work.
 * No private profile, activation, DMI, allocation, MMIO or runtime caller.
 * This selects zero cold module images and zero BLS fractional offset bits;
 * it is not byte-equivalent to every old private-dependent mask result.
 * Parent must qualify the IFE18 selector and original calibration domain.
 */
#ifndef SP11_FRONT_COLD_FIELDS_H
#define SP11_FRONT_COLD_FIELDS_H
#include "sp11-front-measured-config.h"

#define SP11_FRONT_COLD_WORDS 5U
#define SP11_FRONT_COLD_BYTES (12U * SP11_FRONT_COLD_WORDS)
#define SP11_BLS121_IFE18_SELECTOR 13U

struct sp11_front_cold_policy {
	struct sp11_front_measured_domain domain;
	u32 bls_selector;
	u32 bls_fraction;
};

/* Exact IFE18 packing from the SHA-pinned BLS121 Titan680 packer.
 * Linux owns the whole word: the remaining low14 bits are zero.
 * The other native selector,199, uses a different12-bit layout.
 */
static inline int sp11_bls121_ife18_offset(u32 offset18, u32 *word)
{
	if (!word)
		return -EINVAL;
	if (offset18 > 0x3ffffU)
		return -ERANGE;
	*word = offset18 << 14;
	return 0;
}

/* Only independently chosen cold disabled images and integer black offset.
 * Fractional low2 offset bits previously survived the calibration mask.
 * Their zero policy needs physical validation; accepting a tag is not proof.
 */
static inline int sp11_front_cold_fields(u8 *out, size_t capacity,
					 const struct sp11_front_cold_policy *policy)
{
	static const u32 registers[SP11_FRONT_COLD_WORDS] = {
		0x3d60U, 0x4760U, 0x5460U, 0x5a60U, 0x4b68U
	};
	u32 values[SP11_FRONT_COLD_WORDS] = { 0 };
	u8 tmp[SP11_FRONT_COLD_BYTES];
	const struct sp11_front_measured_domain *d;
	unsigned int i;
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)))
		return -EINVAL;
	d = &policy->domain;
	if (d->calibration != SP11_FRONT_MEASURED_NATIVE_AE74_93 ||
	    d->sensor_width != 3840 || d->sensor_height != 2160 ||
	    d->output_width != 2560 || d->output_height != 1440 ||
	    policy->bls_selector != SP11_BLS121_IFE18_SELECTOR ||
	    policy->bls_fraction != 0)
		return -EOPNOTSUPP;
	/* Reuse the own measured integer1649, in the mask's16-bit units. */
	ret = sp11_bls121_ife18_offset(1649U << 2, &values[4]);
	if (ret)
		return ret;
	for (i = 0; i < SP11_FRONT_COLD_WORDS; i++) {
		ret = sp11_cdm_reg_cont(tmp + 12 * i, 12, registers[i],
					&values[i], 1);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
