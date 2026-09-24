/* SPDX-License-Identifier: MIT
 * E004pj OFFLINE design-only: SP11 rear BF stats cannot take RDI/PIX
 * camss_buf_done() shortcut. For some Titan Gen3 generations bus-done
 * is delivered by CSID rather than a separate VFE IRQ. This design
 * allows either independently proven domain but never self-attests a
 * CSID BF bit7 snapshot as WM16 buffer retirement.
 * No CAMSS include, DMA operations, real IRQ callback or runtime arm.
 */
#ifndef E004PJ_CSID_BF_STATS_BRIDGE_H
#define E004PJ_CSID_BF_STATS_BRIDGE_H
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

enum e004pj_source {
	E004PJ_NO_SOURCE = 0,
	E004PJ_VFE_WM16_BUS_IRQ = 1,
	E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED = 2,
	E004PJ_CSID_RDI_DONE = 3,
	E004PJ_CSID_BF_STATUS_UNVERIFIED = 4,
};

struct e004pj_route {
	uint8_t rdi_done_mask; /* logical RDI0..3, not BF/PIX output mapping */
	bool bf_stats_bit7;
	bool video_bit0;
};
/* SP11 accepted full CSID680: RDI0..3 are bits14..17; bit7 is BF
 * candidate, bit0 video and NEITHER is an RDI camss_buf_done event.
 */
static struct e004pj_route e004pj_decode_full_csid(uint32_t latched_status)
{
	unsigned int i;
	struct e004pj_route r = { 0 };

	for (i = 0; i < 4; i++)
		if (latched_status & (UINT32_C(1) << (14u + i)))
			r.rdi_done_mask |= (uint8_t)(1u << i);
	r.bf_stats_bit7 = !!(latched_status & (1u << 7));
	r.video_bit0 = !!(latched_status & 1u);
	return r;
}
struct e004pj_bf_input {
	uint64_t owner_epoch, frame_generation, fifo8_identity, wm16_buffer_identity;
	uint32_t csid1_buf_done_status, csid1_buf_done_mask;
	bool source_is_csid1;
	bool rear_4k_selected_mode0_and_bf_handler_verified;
	bool original_type1_same_fifo8_entry_verified;
};
struct e004pj_wm16_completion {
	enum e004pj_source source;
	uint64_t owner_epoch, frame_generation, fifo8_identity, wm16_buffer_identity;
	bool exact_hw_wm16_bit7_meaning_proven_for_this_generation;
	bool independent_buffer_identity_and_completion_proven;
	bool irq_latched_once_and_ack_source_owned;
	bool bus_group8_queue_entry_matches;
	bool dma_and_iommu_quiescent_for_this_buffer;
};
struct e004pj_owner_fence {
	uint64_t owner_epoch, frame_generation, fifo8_identity, wm16_buffer_identity;
	bool shared_vfe1_rear_exclusive_owner;
	bool all_six_groups_this_frame_completed;
	bool no_earlier_frame_buffer_reuse;
	bool stop_requested;
	bool input_quiesced;
	bool irq_masked_acknowledged_and_drained;
	bool all_WMs_idle_and_DMA_IOMMU_safe;
};
/* Pure hypothetical validation of a future trusted event attestation.
 * A VFE IRQ is NOT unconditionally mandatory on Titan Gen3, but the
 * CSID stats bit7 MUST NOT stand in for its OWN independent per-buffer
 * WM16 completion proof merely because the snapshot bit was set.
 * No current accepted native BF producer provides this attestation.
 */
static int e004pj_offline_bf_complete(
	const struct e004pj_bf_input *bf,
	const struct e004pj_wm16_completion *wm,
	const struct e004pj_owner_fence *owner,
	bool teardown)
{
	if (!bf || !wm || !owner)
		return -EINVAL;
	if (!bf->owner_epoch || !bf->frame_generation || !bf->fifo8_identity ||
	    !bf->wm16_buffer_identity || !bf->source_is_csid1 ||
	    !(bf->csid1_buf_done_status & bf->csid1_buf_done_mask & (1u << 7)) ||
	    !bf->rear_4k_selected_mode0_and_bf_handler_verified ||
	    !bf->original_type1_same_fifo8_entry_verified)
		return -EAGAIN;
	if (wm->owner_epoch != bf->owner_epoch ||
	    wm->frame_generation != bf->frame_generation ||
	    wm->fifo8_identity != bf->fifo8_identity ||
	    wm->wm16_buffer_identity != bf->wm16_buffer_identity ||
	    owner->owner_epoch != bf->owner_epoch ||
	    owner->frame_generation != bf->frame_generation ||
	    owner->fifo8_identity != bf->fifo8_identity ||
	    owner->wm16_buffer_identity != bf->wm16_buffer_identity)
		return -ESTALE;
	if (wm->source != E004PJ_VFE_WM16_BUS_IRQ &&
	    wm->source != E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED)
		return -EPERM;
	if (!wm->exact_hw_wm16_bit7_meaning_proven_for_this_generation ||
	    !wm->independent_buffer_identity_and_completion_proven ||
	    !wm->irq_latched_once_and_ack_source_owned ||
	    !wm->bus_group8_queue_entry_matches ||
	    !wm->dma_and_iommu_quiescent_for_this_buffer ||
	    !owner->shared_vfe1_rear_exclusive_owner ||
	    !owner->all_six_groups_this_frame_completed ||
	    !owner->no_earlier_frame_buffer_reuse)
		return -EAGAIN;
	if (teardown && (!owner->stop_requested || !owner->input_quiesced ||
			 !owner->irq_masked_acknowledged_and_drained ||
			 !owner->all_WMs_idle_and_DMA_IOMMU_safe))
		return -EBUSY;
	return 0; /* offline all-trusted-inputs simulation ONLY */
}
/* Not linked to any hardware path: no source can request rear arm. */
static int e004pj_native_bf_runtime_authorize(void)
{
	return -EOPNOTSUPP;
}
#endif
