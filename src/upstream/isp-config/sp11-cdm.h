/* SPDX-License-Identifier: GPL-2.0-only */
/* Independently written, bounded CDM serialization helpers.
 * Wire definitions: Qualcomm cam_cdm_util.c (GPL-2.0-only), pinned in
 * cdm-reference-20261011.json. This is a driver-internal compiler, not a
 * userspace register programming API. No MMIO, allocation or submission.
 */
#ifndef SP11_OPEN_CDM_H
#define SP11_OPEN_CDM_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
#include <linux/string.h>
#else
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <errno.h>
#include <string.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int16_t s16;
#endif

static inline void sp11_cdm_put32(u8 *p, u32 value)
{
	p[0] = value;
	p[1] = value >> 8;
	p[2] = value >> 16;
	p[3] = value >> 24;
}

static inline bool sp11_cdm_overlap(const void *a, size_t na,
				    const void *b, size_t nb)
{
	unsigned long aa = (unsigned long)a, bb = (unsigned long)b;

	if (!na || !nb)
		return false;
	return aa <= bb ? bb - aa < na : aa - bb < nb;
}

/* Caller owns the source and output extents. Validate every condition before
 * changing the output. Only the serialized extent is written; tail is retained.
 * The calling typed block compiler must restrict registers to its own fields.
 */
static inline int sp11_cdm_reg_cont(u8 *out, size_t capacity, u32 reg,
				   const u32 *values, size_t count)
{
	size_t need, i;

	if (!out || !values || !count)
		return -EINVAL;
	if (count > 0xffffU || (reg & 3U) || reg > 0x00ffffffU ||
	    (count - 1) * 4 > 0x00ffffffU - reg)
		return -ERANGE;
	need = 8 + count * 4;
	if (capacity < need)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, need, values, count * sizeof(*values)))
		return -EINVAL;
	sp11_cdm_put32(out, (3U << 24) | (u32)count);
	sp11_cdm_put32(out + 4, reg);
	for (i = 0; i < count; i++)
		sp11_cdm_put32(out + 8 + 4 * i, values[i]);
	return 0;
}

/* Encode a DMI transfer within a caller-declared DMA allocation. The kernel
 * provider must independently prove allocation ownership, live mapping, bank
 * selection and completion lifetime. Arithmetic checks are not that proof.
 * Accept real byte counts; CDM stores byte_count - 1. No recorded addresses.
 */
static inline int sp11_cdm_dmi(u8 *out, size_t capacity, u32 dmi_reg,
			       unsigned int selector, u64 dma_base,
			       size_t allocation_bytes, size_t offset,
			       size_t byte_count)
{
	u64 address;

	if (!out || !allocation_bytes || !byte_count)
		return -EINVAL;
	if ((dmi_reg & 3U) || dmi_reg > 0x00ffffffU || selector > 255U ||
	    (dma_base & 3U) || dma_base > 0xffffffffULL ||
	    allocation_bytes > 0x100000000ULL - dma_base ||
	    (offset & 3U) || (byte_count & 3U) || byte_count > 0x10000U ||
	    offset > allocation_bytes || byte_count > allocation_bytes - offset)
		return -ERANGE;
	if (capacity < 12)
		return -ENOSPC;
	address = dma_base + offset;
	sp11_cdm_put32(out, (1U << 24) | (u32)(byte_count - 1));
	sp11_cdm_put32(out + 4, (u32)address);
	sp11_cdm_put32(out + 8, dmi_reg | ((u32)selector << 24));
	return 0;
}
#endif
