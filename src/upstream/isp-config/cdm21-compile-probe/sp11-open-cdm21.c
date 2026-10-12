// SPDX-License-Identifier: GPL-2.0-only
/* Compile-only object; never load. No MMIO or release operation. */
#include <linux/module.h>
#include "sp11-cdm21-state.h"

int sp11_cdm21_compile_pending(u32 version, const u32 raw[2],
			      struct sp11_cdm21_pending *out);
int sp11_cdm21_compile_pending(u32 version, const u32 raw[2],
			      struct sp11_cdm21_pending *out)
{
	return sp11_cdm21_decode_pending(version, raw, out);
}

int sp11_cdm21_compile_reset(struct sp11_cdm21_reset_observation *state,
			   u32 version, u64 epoch, unsigned int bank,
			   u32 status, bool *ack);
int sp11_cdm21_compile_reset(struct sp11_cdm21_reset_observation *state,
			   u32 version, u64 epoch, unsigned int bank,
			   u32 status, bool *ack)
{
	int ret;

	ret = sp11_cdm21_reset_begin(state, version, epoch);
	if (ret)
		return ret;
	ret = sp11_cdm21_reset_note(state, epoch, bank, status);
	if (ret)
		return ret;
	*ack = sp11_cdm21_reset_ack_complete(state, epoch);
	return sp11_cdm21_reset_close(state, epoch);
}
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Compile-only CDM 2.1 observations; never load");
