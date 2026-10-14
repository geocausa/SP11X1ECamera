/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Own measured front LSC/ABF table admission and source-bound DMI commands.
 * Data generators, calibration, allocator and queue remain unchanged.
 * No module activation, bank programming, mapping, copy or submission.
 */
#ifndef SP11_FRONT_TABLE_HANDOFF_H
#define SP11_FRONT_TABLE_HANDOFF_H

#include "native-front-gamma.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_LSC_SELECTOR_BYTES 884U
#define SP11_FRONT_LSC_BYTES (3U * SP11_FRONT_LSC_SELECTOR_BYTES)
#define SP11_FRONT_ABF_BYTES 256U
#define SP11_FRONT_TABLE_COMMAND_BYTES 48U

struct sp11_front_table_mapping {
	u64 request_id;
	u64 dma_base;
	size_t allocation_bytes;
	size_t lsc_offset;
	size_t abf_offset;
};

/* Admit exactly the retained own generators' prepared data semantics.
 * LSC has two13-bit Q10 gains separated by one reserved bit; both green
 * lanes agree, and selector3 is zero. ABF is nonzero inverse-noise9-bit
 * values with exact nonnegative9-bit decrements and a zero final decrement.
 * This does not establish optical channel order, mesh geometry or IQ quality.
 */
static inline int sp11_front_tables_validate(const u8 *lsc, size_t lsc_bytes,
					     const u8 *abf, size_t abf_bytes)
{
	unsigned int i;

	if (!lsc || !abf || lsc_bytes != SP11_FRONT_LSC_BYTES ||
	    abf_bytes != SP11_FRONT_ABF_BYTES)
		return -EINVAL;
	for (i = 0; i < SP11_FRONT_LSC_SELECTOR_BYTES; i += 4) {
		u32 first = nf_gamma_get32(lsc + i);
		u32 second = nf_gamma_get32(lsc + SP11_FRONT_LSC_SELECTOR_BYTES + i);
		u32 third = nf_gamma_get32(lsc + 2 * SP11_FRONT_LSC_SELECTOR_BYTES + i);

		if ((first | second) & ~0x07ffdfffU || third ||
		    (first >> 14) != (second >> 14))
			return -EINVAL;
	}
	for (i = 0; i < SP11_FRONT_ABF_BYTES; i += 4) {
		u32 word = nf_gamma_get32(abf + i);
		u32 value = word & 511U;
		u32 decrement = word >> 9;

		if (word & ~0x3ffffU)
			return -EINVAL;
		if (!value)
			return -ERANGE;
		if (i + 4 == SP11_FRONT_ABF_BYTES) {
			if (decrement)
				return -EINVAL;
		} else {
			u32 next = nf_gamma_get32(abf + i + 4) & 511U;

			if (next > value || decrement != value - next)
				return -EINVAL;
		}
	}
	return 0;
}

/*
 * CPU buffers describe bytes at the corresponding offsets in one caller-owned
 * immutable DMA allocation. Only extent arithmetic and encoding are checked.
 * Parent must prove CPU/DMA correspondence, active banks, stopped/exclusive
 * startup, request eligibility and completion lifetime before calling.
 * expected_request_id comes from that parent, never from an untrusted table.
 */
static inline int
sp11_front_tables_prepare(u8 *out, size_t capacity,
			  const struct sp11_front_cold_policy *policy,
			  const struct sp11_front_table_mapping *mapping,
			  u64 expected_request_id,
			  const u8 *lsc, size_t lsc_bytes,
			  const u8 *abf, size_t abf_bytes)
{
	u8 tmp[SP11_FRONT_TABLE_COMMAND_BYTES];
	u8 checked[SP11_FRONT_COLD_BYTES];
	unsigned int i;
	int ret;

	if (!out || !policy || !mapping || !lsc || !abf ||
	    !expected_request_id || !mapping->request_id)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (mapping->request_id != expected_request_id)
		return -EPROTO;
	if (lsc_bytes != SP11_FRONT_LSC_BYTES || abf_bytes != SP11_FRONT_ABF_BYTES)
		return -EINVAL;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), mapping, sizeof(*mapping)) ||
	    sp11_cdm_overlap(out, sizeof(tmp), lsc, lsc_bytes) ||
	    sp11_cdm_overlap(out, sizeof(tmp), abf, abf_bytes) ||
	    sp11_cdm_overlap(lsc, lsc_bytes, abf, abf_bytes))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	if (mapping->lsc_offset > mapping->allocation_bytes ||
	    mapping->allocation_bytes - mapping->lsc_offset < lsc_bytes ||
	    mapping->abf_offset > mapping->allocation_bytes ||
	    mapping->allocation_bytes - mapping->abf_offset < abf_bytes)
		return -ERANGE;
	if (mapping->lsc_offset <= mapping->abf_offset ?
	    mapping->abf_offset - mapping->lsc_offset < lsc_bytes :
	    mapping->lsc_offset - mapping->abf_offset < abf_bytes)
		return -EINVAL;
	ret = sp11_front_tables_validate(lsc, lsc_bytes, abf, abf_bytes);
	if (ret)
		return ret;
	for (i = 0; i < 3; i++) {
		ret = sp11_cdm_dmi(tmp + i * 12, sizeof(tmp) - i * 12,
				   0x4308, i + 1, mapping->dma_base,
				   mapping->allocation_bytes,
				   mapping->lsc_offset + i * SP11_FRONT_LSC_SELECTOR_BYTES,
				   SP11_FRONT_LSC_SELECTOR_BYTES);
		if (ret)
			return ret;
	}
	ret = sp11_cdm_dmi(tmp + 36, sizeof(tmp) - 36, 0x4908, 1,
			   mapping->dma_base, mapping->allocation_bytes,
			   mapping->abf_offset, SP11_FRONT_ABF_BYTES);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
