/* SPDX-License-Identifier: MIT
 * E004ov standalone C11 offline DESIGN contract, never included by CAMSS.
 * All true hardware-evidence flags are externally supplied by a future,
 * source-verified native IRQ/bus/IOMMU path that DOES NOT YET EXIST.
 * This file is not an ISP runtime authorization or a DMA hardware driver.
 */
#ifndef E004OV_REAR_STOP_OWNERSHIP_H
#define E004OV_REAR_STOP_OWNERSHIP_H
#include <stdbool.h>
#include <stdint.h>
#include <errno.h>
#include <stddef.h>

enum { E004OV_GROUPS = 6, E004OV_ALL_GROUPS = 0x3f };
struct e004ov_group {
	uint8_t event_id;
	uint8_t fifo_index;
	uint16_t wm_mask;
};
static const struct e004ov_group e004ov_groups[E004OV_GROUPS] = {
	{ 0x03, 0, 0x000f }, /* FULL Y/C + DS4/DS16 */
	{ 0x0d, 5, 0x0030 }, /* AEC_BE/BHIST */
	{ 0x0e, 6, 0x0040 }, /* TINTLESS */
	{ 0x10, 7, 0x0080 }, /* AWB */
	{ 0x0f, 8, 0x0100 }, /* BF/WM16, static OEM link, no live BF proof */
	{ 0x12, 9, 0x0200 }, /* RS */
};

struct e004ov_state {
	uint64_t owner_epoch, frame_epoch;
	uint64_t last_owner_epoch, last_frame_epoch;
	uint64_t group_queue_identity[E004OV_GROUPS];
	uint8_t pending_groups;
	bool active;
	bool stop_requested;
	bool surface_in_flight;
};

/* A model of proposed Linux evidence, NOT a token that Windows/IRQ
 * hardware has been proven to produce. Event type-2 software counters,
 * KeSetEvent and WM CFG0 zero are expressly NOT evidence for this API.
 */
struct e004ov_completion {
	uint64_t owner_epoch, frame_epoch, queue_identity;
	uint8_t event_id, fifo_index;
	bool hw_irq_status_verified;
	bool group_fifo_entry_verified;
	bool dma_generation_verified;
};
struct e004ov_stop_fence {
	uint64_t owner_epoch, frame_epoch;
	bool source_input_quiescent;
	bool all_active_wm_bus_stopped;
	bool irq_masked_acknowledged_and_drained;
	bool all_generation_dma_finished;
	bool iommu_buffer_ownership_safe;
	bool same_generation_hardware_evidence;
};
static int e004ov_group_for_event(uint8_t event_id)
{
	unsigned int i;

	for (i = 0; i < E004OV_GROUPS; ++i)
		if (e004ov_groups[i].event_id == event_id)
			return (int)i;
	return -ENOENT;
}

/* Fail closed: one ownership epoch / one frame generation per stop
 * transaction. Later per-frame streaming API would be a separate design.
 */
static int e004ov_begin(struct e004ov_state *s,
			uint64_t owner_epoch, uint64_t frame_epoch,
			const uint64_t group_queue_identity[E004OV_GROUPS],
			bool independent_owner_grant_verified)
{
	unsigned int i;

	if (!s || !group_queue_identity || !owner_epoch || !frame_epoch)
		return -EINVAL;
	if (s->active || s->surface_in_flight || s->pending_groups)
		return -EBUSY;
	if (!independent_owner_grant_verified)
		return -EAGAIN;
	if (owner_epoch <= s->last_owner_epoch ||
	    frame_epoch <= s->last_frame_epoch)
		return -ESTALE;
	for (i = 0; i < E004OV_GROUPS; ++i)
		if (!group_queue_identity[i])
			return -EINVAL;

	for (i = 0; i < E004OV_GROUPS; ++i)
		s->group_queue_identity[i] = group_queue_identity[i];
	s->owner_epoch = s->last_owner_epoch = owner_epoch;
	s->frame_epoch = s->last_frame_epoch = frame_epoch;
	s->pending_groups = E004OV_ALL_GROUPS;
	s->active = s->surface_in_flight = true;
	s->stop_requested = false;
	return 0;
}

/* Stop REQUEST changes software state only; never retires a buffer. */
static int e004ov_request_stop(struct e004ov_state *s,
			       uint64_t owner_epoch, uint64_t frame_epoch)
{
	if (!s || !s->active || !s->surface_in_flight)
		return -EINVAL;
	if (s->owner_epoch != owner_epoch || s->frame_epoch != frame_epoch)
		return -ESTALE;
	if (s->stop_requested)
		return -EALREADY;
	s->stop_requested = true;
	return 0;
}

/* A verified GROUP completion, not six fabricated per-WM interrupts.
 * The BF event needs FIFO8's own generation-matched queued entry.
 */
static int e004ov_ack(struct e004ov_state *s,
		      const struct e004ov_completion *p)
{
	int group;
	uint8_t bit;

	if (!s || !p || !s->active || !s->surface_in_flight)
		return -EINVAL;
	if (p->owner_epoch != s->owner_epoch ||
	    p->frame_epoch != s->frame_epoch)
		return -ESTALE;
	group = e004ov_group_for_event(p->event_id);
	if (group < 0 || p->fifo_index != e004ov_groups[group].fifo_index)
		return -EINVAL;
	if (p->queue_identity != s->group_queue_identity[group])
		return -ESTALE;
	if (!p->hw_irq_status_verified || !p->group_fifo_entry_verified ||
	    !p->dma_generation_verified)
		return -EAGAIN;
	bit = (uint8_t)(1u << group);
	if (!(s->pending_groups & bit))
		return -EALREADY;
	s->pending_groups &= (uint8_t)~bit;
	return 0;
}

/* The caller must SOURCE-VERIFY and independently OBSERVE all five
 * hardware safety predicates for this exact owner/frame generation.
 * This DESIGN contract does not implement, invent, or obtain that proof.
 */
static int e004ov_retire_after_stop(struct e004ov_state *s,
				   const struct e004ov_stop_fence *f)
{
	if (!s || !f || !s->active || !s->surface_in_flight)
		return -EINVAL;
	if (s->owner_epoch != f->owner_epoch ||
	    s->frame_epoch != f->frame_epoch)
		return -ESTALE;
	if (!s->stop_requested || s->pending_groups)
		return -EBUSY;
	if (!f->source_input_quiescent ||
	    !f->all_active_wm_bus_stopped ||
	    !f->irq_masked_acknowledged_and_drained ||
	    !f->all_generation_dma_finished ||
	    !f->iommu_buffer_ownership_safe ||
	    !f->same_generation_hardware_evidence)
		return -EAGAIN;

	s->surface_in_flight = false;
	s->active = false;
	s->stop_requested = false;
	s->pending_groups = 0;
	/* last_* persist to reject replay and owner/frame reuse. */
	return 0;
}

/* No mainline module, no CAMSS include, no installed kernel callback,
 * and no Linux rear ISP runtime arm path exists for this proposal.
 */
#endif
