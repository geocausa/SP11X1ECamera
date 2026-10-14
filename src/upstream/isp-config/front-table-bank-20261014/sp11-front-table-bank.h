/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Source-bound LSC411/BPCABF411 bank pairs. No activation or scheduling.
 * Parent supplies banks from retained startup/steady request ownership.
 * Existing table generation, calibration, mapping and lifetime are unchanged.
 */
#ifndef SP11_FRONT_TABLE_BANK_H
#define SP11_FRONT_TABLE_BANK_H

#include "sp11-front-cold-fields.h"

#define SP11_FRONT_TABLE_BANK_BYTES 32U

struct sp11_front_table_bank_state {
	u32 lsc;
	u32 abf;
};

/* Whole zero-reserved software words are own cold policy, not hardware reset.
 * Full LSC/ABF configuration, table preparation and retirement remain required.
 * This does not decide a bank from request parity or grant queue admission.
 */
static inline int
sp11_front_table_bank_config(u8 *out, size_t capacity,
			     const struct sp11_front_cold_policy *policy,
			     const struct sp11_front_table_bank_state *state)
{
	u8 tmp[SP11_FRONT_TABLE_BANK_BYTES];
	u8 checked[SP11_FRONT_COLD_BYTES];
	u32 pair[2];
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
	if (state->lsc > 1 || state->abf > 1)
		return -ERANGE;
	pair[0] = state->lsc;
	pair[1] = state->lsc;
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), 0x4358, pair, 2);
	if (ret)
		return ret;
	pair[0] = state->abf;
	pair[1] = state->abf;
	ret = sp11_cdm_reg_cont(tmp + 16, sizeof(tmp) - 16, 0x4958, pair, 2);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
