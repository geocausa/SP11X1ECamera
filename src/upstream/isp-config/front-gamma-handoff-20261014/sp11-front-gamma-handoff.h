/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Source-bound Gamma151 banks and DMI plan; no mapping or submission.
 * Reuses the native RGB validator and bounded CDM serializer unchanged.
 * Caller must own one immutable RGB table allocation through completion,
 * enforce the existing request/bank lifetime, and keep activation separate.
 */
#ifndef SP11_FRONT_GAMMA_HANDOFF_H
#define SP11_FRONT_GAMMA_HANDOFF_H

#include "native-front-gamma.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_GAMMA_PREPARE_BYTES 52U
#define SP11_FRONT_GAMMA_ENABLE_BYTES 12U

struct sp11_front_gamma_mapping {
	u64 dma_base;
	size_t allocation_bytes;
	size_t offset;
	u32 bank;
};

/*
 * gamma describes semantic R/G/B bytes at mapping->offset. This function
 * validates encoding and arithmetic, not the CPU-to-DMA correspondence.
 * Both source bank fields use bit0. Reject wider values instead of masking.
 * G/B/R selectors1/2/3 reuse retained binding; optical order is unqualified.
 * Caller must independently prove a stopped/exclusive path for startup.
 */
static inline int
sp11_front_gamma_prepare(u8 *out, size_t capacity,
			 const struct sp11_front_cold_policy *policy,
			 const struct sp11_front_gamma_mapping *mapping,
			 const u8 *gamma, size_t gamma_bytes)
{
	const unsigned int channels[] = { 1, 2, 0 };
	u8 tmp[SP11_FRONT_GAMMA_PREPARE_BYTES];
	u8 checked[SP11_FRONT_COLD_BYTES];
	u32 banks[2];
	unsigned int i;
	int ret;

	if (!out || !policy || !mapping || !gamma)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (gamma_bytes != NF_GAMMA_BYTES)
		return -EINVAL;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), mapping, sizeof(*mapping)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), gamma, gamma_bytes))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	if (mapping->bank > 1)
		return -ERANGE;
	/* Bound the whole RGB extent before computing any channel offset. */
	if (mapping->offset > mapping->allocation_bytes ||
	    mapping->allocation_bytes - mapping->offset < NF_GAMMA_BYTES)
		return -ERANGE;
	ret = native_front_gamma12_validate(gamma, gamma_bytes);
	if (ret)
		return ret;
	banks[0] = mapping->bank;
	banks[1] = mapping->bank;
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), 0x5f58, banks, 2);
	if (ret)
		return ret;
	for (i = 0; i < NF_GAMMA_CHANNELS; i++) {
		ret = sp11_cdm_dmi(tmp + 16 + i * 12, sizeof(tmp) - 16 - i * 12,
				   0x5f08, i + 1, mapping->dma_base,
				   mapping->allocation_bytes,
				   mapping->offset + channels[i] * 1024U, 1024);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* A separate command, never emitted by prepare. No runtime caller exists.
 * The future provider must order this after successful table preparation.
 * Source configuration alone does not prove that hardware ordering/lifetime.
 */
static inline int sp11_front_gamma_enable(u8 *out, size_t capacity)
{
	const u32 enabled = 1;

	return sp11_cdm_reg_cont(out, capacity, 0x5f60, &enabled, 1);
}
#endif
