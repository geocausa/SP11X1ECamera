/* SPDX-License-Identifier: GPL-2.0-only */
/* Existing own run93 measured GBR Q7 matrix, unchanged; no private tuning. */
#ifndef SP11_FRONT_CCM_MEASURED_H
#define SP11_FRONT_CCM_MEASURED_H

#include "sp11-front-ccm-config.h"

static const struct sp11_front_ccm_state sp11_front_ccm_run93 = {
	.matrix = { 216, -26, -61, -72, 205, -5, -92, -5, 224 },
	.offset = { 0, 0, 0 },
	.fractional_bits = 7,
};

static inline int
sp11_front_ccm_measured_config(u8 *out, size_t capacity,
			       const struct sp11_front_cold_policy *policy)
{
	return sp11_front_ccm_config(out, capacity, policy,
				     &sp11_front_ccm_run93);
}
#endif
