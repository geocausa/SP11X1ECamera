/* SPDX-License-Identifier: MIT
 * E004pi offline ONLY: two independent physical domains must be evidenced.
 * The original Windows CSID BUF_DONE bit7 snapshot is CSID evidence, never
 * a VFE WM16 bus-IRQ, DMA/IOMMU quiescence or frame-ownership fence.
 * NO real source currently populates a verified VFE WM16 evidence record.
 * This file is not included or called by CAMSS, and runtime arm is DENIED.
 */
#ifndef E004PI_BF_WM16_DOMAIN_GATE_H
#define E004PI_BF_WM16_DOMAIN_GATE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <errno.h>

enum e004pi_domain {
	E004PI_DOMAIN_INVALID = 0,
	E004PI_DOMAIN_CSID_BUF_DONE = 1,
	E004PI_DOMAIN_VFE_WM16_BUS_DMA = 2,
};
struct e004pi_csid_observation {
	enum e004pi_domain domain;
	uint64_t owner_epoch, frame_generation, group8_fifo_identity;
	uint32_t buf_done_status, buf_done_irq_mask;
	bool same_session_source_verified;
};
struct e004pi_wm16_evidence {
	enum e004pi_domain domain;
	uint64_t owner_epoch, frame_generation, group8_fifo_identity;
	/* Independent VFE1 BUS/IRQ/frame DMA evidence from a source that
	 * does not currently exist in the accepted native CAMSS ISR. */
	bool vfe_wm16_irq_source_verified;
	bool vfe_wm16_irq_mask_and_ack_verified;
	bool vfe_wm16_bus_quiescent;
	bool vfe_wm16_dma_generation_finished;
	bool iommu_buffer_ownership_safe;
};
struct e004pi_owner_fence {
	uint64_t owner_epoch, frame_generation, group8_fifo_identity;
	bool exclusive_shared_vfe1_owner_granted;
	bool original_fifo8_same_frame_verified;
	bool source_input_quiescent;
	bool all_six_wm_groups_completed;
	bool stop_requested;
	bool irq_sources_masked_acknowledged_and_drained;
};
/* Conceptual synthetic gate only: never interpret an E004pi return of 0
 * as real hardware authorization; the trusted native producer does not exist.
 */
static int e004pi_offline_bf_retirement_predicate(
	const struct e004pi_csid_observation *csid,
	const struct e004pi_wm16_evidence *wm,
	const struct e004pi_owner_fence *owner)
{
	if (!csid || !wm || !owner)
		return -EINVAL;
	if (csid->domain != E004PI_DOMAIN_CSID_BUF_DONE ||
	    wm->domain != E004PI_DOMAIN_VFE_WM16_BUS_DMA)
		return -EPERM;
	if (!csid->owner_epoch || !csid->frame_generation ||
	    !csid->group8_fifo_identity || !csid->same_session_source_verified ||
	    !(csid->buf_done_status & csid->buf_done_irq_mask & (1u << 7)))
		return -EAGAIN;
	if (csid->owner_epoch != wm->owner_epoch ||
	    csid->frame_generation != wm->frame_generation ||
	    csid->group8_fifo_identity != wm->group8_fifo_identity ||
	    csid->owner_epoch != owner->owner_epoch ||
	    csid->frame_generation != owner->frame_generation ||
	    csid->group8_fifo_identity != owner->group8_fifo_identity)
		return -ESTALE;
	if (!wm->vfe_wm16_irq_source_verified ||
	    !wm->vfe_wm16_irq_mask_and_ack_verified ||
	    !wm->vfe_wm16_bus_quiescent ||
	    !wm->vfe_wm16_dma_generation_finished ||
	    !wm->iommu_buffer_ownership_safe ||
	    !owner->exclusive_shared_vfe1_owner_granted ||
	    !owner->original_fifo8_same_frame_verified ||
	    !owner->source_input_quiescent ||
	    !owner->all_six_wm_groups_completed ||
	    !owner->stop_requested ||
	    !owner->irq_sources_masked_acknowledged_and_drained)
		return -EAGAIN;
	return 0; /* hypothetical offline fully evidenced future state ONLY */
}
/* Actual current release gate: offline proofs never enable rear HW ISP. */
static int e004pi_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}
#endif
