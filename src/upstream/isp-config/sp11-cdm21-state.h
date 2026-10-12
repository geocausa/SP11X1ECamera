/* SPDX-License-Identifier: GPL-2.0-only */
/* Driver-internal CDM 2.1 observations. No MMIO, submission or DMA release.
 * Public definitions: ../camss/cdm-lifetime-reference-20261012.json.
 * An epoch labels software ownership; it cannot date a hardware IRQ.
 */
#ifndef SP11_CDM21_STATE_H
#define SP11_CDM21_STATE_H
#include "sp11-cdm.h"

#define SP11_CDM21_VERSION 0x20010000U
#define SP11_CDM21_FIFO_COUNT 4U

struct sp11_cdm21_pending {
	u32 count[SP11_CDM21_FIFO_COUNT];
};

/* Two readbacks are observations, not an atomic snapshot or AXI drain proof.
 * Caller must check hardware version from the owned device, stop submissions,
 * and establish MMIO ordering and exclusive access independently.
 */
static inline int sp11_cdm21_decode_pending(u32 version,
					  const u32 raw[2],
					  struct sp11_cdm21_pending *out)
{
	struct sp11_cdm21_pending next;
	unsigned int i;

	if (!raw || !out ||
	    sp11_cdm_overlap(raw, 2 * sizeof(*raw), out, sizeof(*out)))
		return -EINVAL;
	if (version != SP11_CDM21_VERSION)
		return -ENODEV;
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		next.count[i] = (raw[i / 2] >> (16 * (i % 2))) & 0x1ffU;
	*out = next;
	return 0;
}

struct sp11_cdm21_reset_observation {
	u64 epoch;
	u32 seen;
	bool armed;
	bool fault;
};

/* Zero-initialized state, serialized by the provider's ownership lock.
 * Before begin: mask all four IRQ banks, read back, drain the handler, clear
 * old status and verify clear; then arm the fresh reset transaction.
 * This function neither performs nor certifies those hardware operations.
 */
static inline int sp11_cdm21_reset_begin(
	struct sp11_cdm21_reset_observation *state, u32 version, u64 epoch)
{
	if (!state || !epoch)
		return -EINVAL;
	if (version != SP11_CDM21_VERSION)
		return -ENODEV;
	if (state->armed)
		return -EBUSY;
	if (epoch <= state->epoch)
		return -ESTALE;
	state->epoch = epoch;
	state->seen = 0;
	state->fault = false;
	state->armed = true;
	return 0;
}

/* Caller supplies a bank number and serialized epoch. Duplicate reset bits
 * do not advance progress. Only reset/inline/BL_DONE bits are tolerated;
 * any other status fails this reset observation closed, including errors.
 */
static inline int sp11_cdm21_reset_note(
	struct sp11_cdm21_reset_observation *state, u64 epoch,
	unsigned int bank, u32 status)
{
	if (!state || !epoch)
		return -EINVAL;
	if (!state->armed || epoch != state->epoch)
		return -ESTALE;
	if (state->fault)
		return -EIO;
	if (bank >= SP11_CDM21_FIFO_COUNT || (status & ~7U)) {
		state->fault = true;
		return -EIO;
	}
	if (status & 1U)
		state->seen |= 1U << bank;
	return 0;
}

/* All four acknowledgments observed without a fault. This does not certify
 * pending work, bus idleness, handler retirement or DMA allocation lifetime.
 */
static inline bool sp11_cdm21_reset_ack_complete(
	const struct sp11_cdm21_reset_observation *state, u64 epoch)
{
	return state && epoch && state->armed && !state->fault &&
	       state->epoch == epoch && state->seen == 0xfU;
}

/* Call only after the provider drains IRQ work; closes software observation.
 * The retained epoch prevents reuse. Hardware failure requires quarantine.
 */
static inline int sp11_cdm21_reset_close(
	struct sp11_cdm21_reset_observation *state, u64 epoch)
{
	if (!state || !epoch)
		return -EINVAL;
	if (!state->armed || epoch != state->epoch)
		return -ESTALE;
	state->armed = false;
	return 0;
}
#endif
