/* SPDX-License-Identifier: MIT
 * SP11 E004pi OFFLINE C11 DESIGN test. No device, mmio, camss or DMA calls.
 */
#include "bf-wm16-domain-gate.h"
#include <assert.h>
#include <stdio.h>

static unsigned long checks;
#define CHECK(test) do { assert((test)); ++checks; } while (0)
static struct e004pi_csid_observation csid_original_live(void)
{
	return (struct e004pi_csid_observation){
		.domain = E004PI_DOMAIN_CSID_BUF_DONE,
		.owner_epoch = 13, .frame_generation = 89,
		.group8_fifo_identity = 0x81,
		.buf_done_status = 0x000002f1,
		.buf_done_irq_mask = 0x0001ffff,
		.same_session_source_verified = true,
	};
}
static struct e004pi_wm16_evidence hypothetical_wm(void)
{
	return (struct e004pi_wm16_evidence){
		.domain = E004PI_DOMAIN_VFE_WM16_BUS_DMA,
		.owner_epoch = 13, .frame_generation = 89,
		.group8_fifo_identity = 0x81,
		.vfe_wm16_irq_source_verified = true,
		.vfe_wm16_irq_mask_and_ack_verified = true,
		.vfe_wm16_bus_quiescent = true,
		.vfe_wm16_dma_generation_finished = true,
		.iommu_buffer_ownership_safe = true,
	};
}
static struct e004pi_owner_fence hypothetical_owner(void)
{
	return (struct e004pi_owner_fence){
		.owner_epoch = 13, .frame_generation = 89,
		.group8_fifo_identity = 0x81,
		.exclusive_shared_vfe1_owner_granted = true,
		.original_fifo8_same_frame_verified = true,
		.source_input_quiescent = true,
		.all_six_wm_groups_completed = true,
		.stop_requested = true,
		.irq_sources_masked_acknowledged_and_drained = true,
	};
}

int main(void)
{
	struct e004pi_csid_observation c = csid_original_live();
	struct e004pi_wm16_evidence w = hypothetical_wm();
	struct e004pi_owner_fence o = hypothetical_owner();
	int i;
	CHECK(e004pi_rear_runtime_authorization() == -EOPNOTSUPP);
	CHECK(e004pi_offline_bf_retirement_predicate(NULL, &w, &o) == -EINVAL);
	CHECK(e004pi_offline_bf_retirement_predicate(&c, NULL, &o) == -EINVAL);
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, NULL) == -EINVAL);
	/* Same original Windows physical snapshots LIVE1 and LIVE2:
	 * observed CSID BUF_DONE+mask bit7 and WM16 CFG0/enabled, but
	 * zero observed VFE BUS status and no independent WM16 completion
	 * producer. In both snapshots release MUST FAIL.
	 */
	for (i = 0; i != 2; ++i) {
		w.vfe_wm16_irq_source_verified = false;
		w.vfe_wm16_irq_mask_and_ack_verified = false;
		w.vfe_wm16_bus_quiescent = false;
		w.vfe_wm16_dma_generation_finished = false;
		w.iommu_buffer_ownership_safe = false;
		CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o)
		      == -EAGAIN);
	}
	w = hypothetical_wm();
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == 0);
	/* Domain substitution is forbidden even with every claimed
	 * independent boolean set. CSID bit7 is not a VFE WM16 IRQ.
	 */
	w.domain = E004PI_DOMAIN_CSID_BUF_DONE;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EPERM);
	w = hypothetical_wm();
	c.domain = E004PI_DOMAIN_VFE_WM16_BUS_DMA;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EPERM);
	c = csid_original_live();
	c.buf_done_status &= ~(1u << 7);
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EAGAIN);
	c = csid_original_live();
	c.buf_done_irq_mask &= ~(1u << 7);
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EAGAIN);
	c = csid_original_live();
	c.same_session_source_verified = false;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EAGAIN);
	c = csid_original_live();
	c.owner_epoch = 0;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EAGAIN);
	c = csid_original_live();
	c.group8_fifo_identity = 0;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -EAGAIN);
	c = csid_original_live();
	c.frame_generation = 90;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -ESTALE);
	c = csid_original_live();
	w.owner_epoch++;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -ESTALE);
	w = hypothetical_wm();
	w.group8_fifo_identity++;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -ESTALE);
	w = hypothetical_wm();
	o.owner_epoch++;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -ESTALE);
	o = hypothetical_owner();
	o.frame_generation++;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -ESTALE);
	o = hypothetical_owner();
	o.group8_fifo_identity++;
	CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o) == -ESTALE);
	o = hypothetical_owner();

	/* Every omitted independent WM16/owner/fence predicate fails. */
	for (i = 0; i != 5; ++i) {
		w = hypothetical_wm();
		switch (i) {
		case 0: w.vfe_wm16_irq_source_verified = false; break;
		case 1: w.vfe_wm16_irq_mask_and_ack_verified = false; break;
		case 2: w.vfe_wm16_bus_quiescent = false; break;
		case 3: w.vfe_wm16_dma_generation_finished = false; break;
		case 4: w.iommu_buffer_ownership_safe = false; break;
		}
		CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o)
		      == -EAGAIN);
	}
	w = hypothetical_wm();
	for (i = 0; i != 6; ++i) {
		o = hypothetical_owner();
		switch (i) {
		case 0: o.exclusive_shared_vfe1_owner_granted = false; break;
		case 1: o.original_fifo8_same_frame_verified = false; break;
		case 2: o.source_input_quiescent = false; break;
		case 3: o.all_six_wm_groups_completed = false; break;
		case 4: o.stop_requested = false; break;
		case 5: o.irq_sources_masked_acknowledged_and_drained = false; break;
		}
		CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o)
		      == -EAGAIN);
	}
	o = hypothetical_owner();
	/* Exhaustively remove every subset of five hypothetical WM16
	 * independent predicates: only 0x1f (all five) may pass.
	 * The actual native runtime authorization ALWAYS remains DENIED.
	 */
	for (i = 0; i != 32; ++i) {
		w = hypothetical_wm();
		w.vfe_wm16_irq_source_verified = !!(i & 1);
		w.vfe_wm16_irq_mask_and_ack_verified = !!(i & 2);
		w.vfe_wm16_bus_quiescent = !!(i & 4);
		w.vfe_wm16_dma_generation_finished = !!(i & 8);
		w.iommu_buffer_ownership_safe = !!(i & 16);
		CHECK(e004pi_offline_bf_retirement_predicate(&c, &w, &o)
		      == (i == 31 ? 0 : -EAGAIN));
		CHECK(e004pi_rear_runtime_authorization() == -EOPNOTSUPP);
	}
	printf("PASS_E004PI_C11_DOMAIN_SEPARATION_ASSERTIONS_%lu_TWO_WINDOWS_LIVE_CSID_BIT7_OBSERVATIONS_NOT_WM16_DMA_FENCE_REAR_RUNTIME_DENIED\n", checks);
	return 0;
}
