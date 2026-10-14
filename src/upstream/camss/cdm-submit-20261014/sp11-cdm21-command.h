/* SPDX-License-Identifier: GPL-2.0-only */
/* Single owned REG_CONT program. No userspace ABI or DMA retirement claim. */
#ifndef SP11_CDM21_COMMAND_H
#define SP11_CDM21_COMMAND_H
#include "sp11-cdm.h"

struct sp11_cdm21_command {
	const u8 *cpu;
	u64 dma;
	size_t capacity;
	size_t bytes;
	u64 owner;
	u64 request;
};

struct sp11_cdm21_receipt {
	u64 owner;
	u64 request;
	u64 sequence;
	u32 dma;
	u32 bytes;
	u32 status;
};

static inline u32 sp11_cdm21_get32(const u8 *p)
{
	return (u32)p[0] | ((u32)p[1] << 8) |
	       ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

/* Arithmetic and opcode admission only. The parent must independently own
 * this coherent allocation and retain it immutable through hardware exposure.
 * DMI, indirect programs, jumps and generated IRQ payloads are not admitted.
 * Typed compilers retain responsibility for their allowed register fields.
 */
static inline int sp11_cdm21_command_validate(
	const struct sp11_cdm21_command *cmd)
{
	size_t pos = 0, count, need;
	u32 word, reg;

	if (!cmd || !cmd->cpu || !cmd->owner || !cmd->request ||
	    !cmd->dma || !cmd->bytes || !cmd->capacity)
		return -EINVAL;
	if ((cmd->dma & 3) || (cmd->bytes & 3) ||
	    cmd->dma > 0xffffffffULL ||
	    cmd->capacity > 0x100000000ULL - cmd->dma ||
	    cmd->bytes > cmd->capacity || cmd->bytes > 0x100000U)
		return -ERANGE;
	while (pos < cmd->bytes) {
		if (cmd->bytes - pos < 12)
			return -EINVAL;
		word = sp11_cdm21_get32(cmd->cpu + pos);
		count = word & 0xffffU;
		if ((word & 0xffff0000U) != (3U << 24) || !count)
			return -EINVAL;
		reg = sp11_cdm21_get32(cmd->cpu + pos + 4);
		if ((reg & 3) || reg > 0x00ffffffU ||
		    (count - 1) * 4 > 0x00ffffffU - reg)
			return -ERANGE;
		need = 8 + count * 4;
		if (need > cmd->bytes - pos)
			return -EINVAL;
		pos += need;
	}
	return 0;
}

/* Same FIFO0 byte-count-minus-one and ARB bit as the retained native recipe;
 * independently corroborated by pinned Qualcomm CDM2.1 GPL definitions.
 */
static inline u32 sp11_cdm21_command_length(size_t bytes)
{
	return (u32)(bytes - 1) | (1U << 20);
}

static inline bool sp11_cdm21_command_status_valid(u32 status)
{
	return (status & 4U) && !(status & ~6U);
}
#endif
