/* SPDX-License-Identifier: GPL-2.0-only */
/* Generated from our existing measured register overrides, not a vendor file.
 * Source, native baseline and exact extraction: baseline-audit.json.
 * Configuration only: no activation, DMI, private carrier, MMIO or ownership.
 * Parent must establish the actual calibrated native processing domain and
 * complete surrounding BLS/ABF setup. Geometry/tag alone are not that proof.
 */
#ifndef SP11_FRONT_MEASURED_CONFIG_H
#define SP11_FRONT_MEASURED_CONFIG_H
#include "sp11-cdm.h"

#define SP11_FRONT_MEASURED_CONFIG_WORDS 24U
#define SP11_FRONT_MEASURED_CONFIG_BYTES (12U * SP11_FRONT_MEASURED_CONFIG_WORDS)
#define SP11_FRONT_MEASURED_NATIVE_AE74_93 1U

struct sp11_front_measured_domain {
	u32 calibration;
	u32 sensor_width;
	u32 sensor_height;
	u32 output_width;
	u32 output_height;
};

static const struct {
	u32 reg;
	u32 value;
} sp11_front_measured_words[SP11_FRONT_MEASURED_CONFIG_WORDS] = {
	{ 0x4b6cU, 0x00000835U },
	{ 0x496cU, 0x00000000U },
	{ 0x4980U, 0x00000000U },
	{ 0x4984U, 0x00000000U },
	{ 0x498cU, 0x00000000U },
	{ 0x49a0U, 0x00000000U },
	{ 0x49a4U, 0x00000000U },
	{ 0x49a8U, 0x00000000U },
	{ 0x49acU, 0x00000000U },
	{ 0x49b0U, 0x00000000U },
	{ 0x49b4U, 0x00000000U },
	{ 0x49b8U, 0x00000000U },
	{ 0x49bcU, 0x00000000U },
	{ 0x49c8U, 0x00000000U },
	{ 0x49ccU, 0x00000000U },
	{ 0x49d8U, 0x00000000U },
	{ 0x49dcU, 0x00000000U },
	{ 0x49e4U, 0x00000000U },
	{ 0x49e8U, 0x00000000U },
	{ 0x49d0U, 0xffffffffU },
	{ 0x49d4U, 0xffffffffU },
	{ 0x49e0U, 0xffffffffU },
	{ 0x4968U, 0x00000004U },
	{ 0x4988U, 0x003c0044U },
};

/* Reuse exactly the native 2160 -> 1440 domain; reject the newer 2640 mode.
 * Unknown preserved bits and the ABF activation are deliberately absent.
 * Immutable caller domain/output extents; publish atomically after validation.
 */
static inline int sp11_front_measured_config(
	u8 *out, size_t capacity, const struct sp11_front_measured_domain *domain)
{
	u8 tmp[SP11_FRONT_MEASURED_CONFIG_BYTES];
	unsigned int i;
	int ret;

	if (!out || !domain)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), domain, sizeof(*domain)))
		return -EINVAL;
	if (domain->calibration != SP11_FRONT_MEASURED_NATIVE_AE74_93 ||
	    domain->sensor_width != 3840 || domain->sensor_height != 2160 ||
	    domain->output_width != 2560 || domain->output_height != 1440)
		return -EOPNOTSUPP;
	for (i = 0; i < SP11_FRONT_MEASURED_CONFIG_WORDS; i++) {
		ret = sp11_cdm_reg_cont(tmp + 12 * i, 12,
					sp11_front_measured_words[i].reg,
					&sp11_front_measured_words[i].value, 1);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
