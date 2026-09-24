/* SPDX-License-Identifier: MIT
 * E004pj OFFLINE C11 only. Synthetic owner/frame IDs are NOT observed
 * original Windows runtime IDs and never authorize Linux rear hardware.
 */
#include "bf-csid-to-wm16-offline.h"
#include <stdio.h>
#include <assert.h>

static unsigned long assertions;
#define CHECK(expr) do { assert((expr)); ++assertions; } while (0)
static struct e004pj_bf_input hypothetical_bf(void)
{
	return (struct e004pj_bf_input){
		.owner_epoch = 4, .frame_generation = 8,
		.fifo8_identity = 42, .wm16_buffer_identity = 77,
		.csid1_buf_done_status = 0x000002f1,
		.csid1_buf_done_mask = 0x0001ffff,
		.source_is_csid1 = true,
		.rear_4k_selected_mode0_and_bf_handler_verified = true,
		.original_type1_same_fifo8_entry_verified = true,
	};
}
static struct e004pj_wm16_completion hypothetical_wm(enum e004pj_source s)
{
	return (struct e004pj_wm16_completion){
		.source = s,
		.owner_epoch = 4, .frame_generation = 8,
		.fifo8_identity = 42, .wm16_buffer_identity = 77,
		.exact_hw_wm16_bit7_meaning_proven_for_this_generation = true,
		.independent_buffer_identity_and_completion_proven = true,
		.irq_latched_once_and_ack_source_owned = true,
		.bus_group8_queue_entry_matches = true,
		.dma_and_iommu_quiescent_for_this_buffer = true,
	};
}
static struct e004pj_owner_fence hypothetical_owner(void)
{
	return (struct e004pj_owner_fence){
		.owner_epoch = 4, .frame_generation = 8,
		.fifo8_identity = 42, .wm16_buffer_identity = 77,
		.shared_vfe1_rear_exclusive_owner = true,
		.all_six_groups_this_frame_completed = true,
		.no_earlier_frame_buffer_reuse = true,
		.stop_requested = true,
		.input_quiesced = true,
		.irq_masked_acknowledged_and_drained = true,
		.all_WMs_idle_and_DMA_IOMMU_safe = true,
	};
}
int main(void)
{
	unsigned int i;
	struct e004pj_bf_input bf = hypothetical_bf();
	struct e004pj_owner_fence own = hypothetical_owner();
	struct e004pj_wm16_completion wm =
		hypothetical_wm(E004PJ_VFE_WM16_BUS_IRQ);
	struct e004pj_route route;
	CHECK(e004pj_native_bf_runtime_authorize() == -EOPNOTSUPP);
	CHECK(e004pj_offline_bf_complete(NULL, &wm, &own, false) == -EINVAL);
	CHECK(e004pj_offline_bf_complete(&bf, NULL, &own, false) == -EINVAL);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, NULL, false) == -EINVAL);
	/* Exhaustively verify all combinations of bits0..15, including
	 * CSID BF bit7 combined with RDI0/1 bits14/15. Statistics/PIX
	 * must NEVER be routed as RDI camss_buf_done.
	 */
	for (i = 0; i < 65536u; ++i) {
		route = e004pj_decode_full_csid(i);
		CHECK(route.rdi_done_mask == (uint8_t)((i >> 14) & 3u));
		CHECK(route.bf_stats_bit7 == !!(i & (1u << 7)));
		CHECK(route.video_bit0 == !!(i & 1u));
		CHECK(e004pj_native_bf_runtime_authorize() == -EOPNOTSUPP);
	}
	for (i = 0; i < 4u; ++i) {
		route = e004pj_decode_full_csid(UINT32_C(1) << (14u + i));
		CHECK(route.rdi_done_mask == (uint8_t)(1u << i));
		CHECK(!route.bf_stats_bit7 && !route.video_bit0);
		route = e004pj_decode_full_csid((1u << 7) |
					       (UINT32_C(1) << (14u + i)));
		CHECK(route.rdi_done_mask == (uint8_t)(1u << i));
		CHECK(route.bf_stats_bit7 && !route.video_bit0);
	}
	route = e004pj_decode_full_csid(0x000002f1);
	CHECK(route.bf_stats_bit7 && route.video_bit0);
	CHECK(route.rdi_done_mask == 0);
	route = e004pj_decode_full_csid(0x0003c081);
	CHECK(route.rdi_done_mask == 0x0f && route.bf_stats_bit7 &&
	      route.video_bit0);

	/* All-positive synthetic sources check the MODEL only. Current
	 * Linux runtime authorization is hard-disabled even in this case.
	 * VFE IRQ is not universally required on Titan Gen3 if a future
	 * trusted CSID statistics WM16 bus-done bridge proves matching
	 * hardware meaning, buffer identity and DMA/IOMMU completion.
	 */
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == 0);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, true) == 0);
	wm = hypothetical_wm(E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == 0);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, true) == 0);
	CHECK(e004pj_native_bf_runtime_authorize() == -EOPNOTSUPP);
	/* Merely relabeling the same CSID stats bit7 or RDI as a
	 * completion is a prohibited self-attestation. */
	for (i = E004PJ_NO_SOURCE; i <= E004PJ_CSID_BF_STATUS_UNVERIFIED; i++) {
		wm = hypothetical_wm((enum e004pj_source)i);
		CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) ==
		      ((i == E004PJ_VFE_WM16_BUS_IRQ ||
			i == E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED)
		       ? 0 : -EPERM));
	}
	wm = hypothetical_wm(E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED);
	bf.csid1_buf_done_mask &= ~(1u << 7);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	bf.csid1_buf_done_status &= ~(1u << 7);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	bf.source_is_csid1 = false;
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	bf.rear_4k_selected_mode0_and_bf_handler_verified = false;
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	bf.original_type1_same_fifo8_entry_verified = false;
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	bf.frame_generation = 0;
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	bf.wm16_buffer_identity = 0;
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == -EAGAIN);
	bf = hypothetical_bf();
	for (i = 0; i < 4u; i++) {
		wm = hypothetical_wm(E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED);
		switch (i) {
		case 0: wm.owner_epoch++; break;
		case 1: wm.frame_generation++; break;
		case 2: wm.fifo8_identity++; break;
		case 3: wm.wm16_buffer_identity++; break;
		}
		CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) ==
		      -ESTALE);
	}
	wm = hypothetical_wm(E004PJ_VFE_WM16_BUS_IRQ);
	for (i = 0; i < 4u; i++) {
		own = hypothetical_owner();
		switch (i) {
		case 0: own.owner_epoch++; break;
		case 1: own.frame_generation++; break;
		case 2: own.fifo8_identity++; break;
		case 3: own.wm16_buffer_identity++; break;
		}
		CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) ==
		      -ESTALE);
	}
	own = hypothetical_owner();
	/* Exhaustively remove any combination of five independently
	 * required WM16 completion attributes: only all five true
	 * can pass a purely hypothetical offline frame predicate. */
	for (i = 0; i < 32u; i++) {
		wm = hypothetical_wm(E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED);
		wm.exact_hw_wm16_bit7_meaning_proven_for_this_generation = !!(i & 1u);
		wm.independent_buffer_identity_and_completion_proven = !!(i & 2u);
		wm.irq_latched_once_and_ack_source_owned = !!(i & 4u);
		wm.bus_group8_queue_entry_matches = !!(i & 8u);
		wm.dma_and_iommu_quiescent_for_this_buffer = !!(i & 16u);
		CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) ==
		      (i == 31u ? 0 : -EAGAIN));
		CHECK(e004pj_native_bf_runtime_authorize() == -EOPNOTSUPP);
	}
	wm = hypothetical_wm(E004PJ_CSID_STATS_WM16_BUS_DONE_VERIFIED);
	own = hypothetical_owner();
	for (i = 0; i < 8u; i++) {
		struct e004pj_owner_fence test = own;
		switch (i) {
		case 0: test.shared_vfe1_rear_exclusive_owner = false; break;
		case 1: test.all_six_groups_this_frame_completed = false; break;
		case 2: test.no_earlier_frame_buffer_reuse = false; break;
		case 3: test.stop_requested = false; break;
		case 4: test.input_quiesced = false; break;
		case 5: test.irq_masked_acknowledged_and_drained = false; break;
		case 6: test.all_WMs_idle_and_DMA_IOMMU_safe = false; break;
		case 7: test.fifo8_identity++; break;
		}
		CHECK(e004pj_offline_bf_complete(&bf, &wm, &test, true) ==
		      (i < 3 ? -EAGAIN : i < 7 ? -EBUSY : -ESTALE));
	}
	/* A frame in a continuing stream and a stop transaction have
	 * DISTINCT gates: stop-only state must not accidentally be used
	 * as proof of a frame's DMA completion, or vice versa.
	 */
	own = hypothetical_owner();
	own.stop_requested = false;
	own.input_quiesced = false;
	own.irq_masked_acknowledged_and_drained = false;
	own.all_WMs_idle_and_DMA_IOMMU_safe = false;
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, false) == 0);
	CHECK(e004pj_offline_bf_complete(&bf, &wm, &own, true) == -EBUSY);
	CHECK(e004pj_native_bf_runtime_authorize() == -EOPNOTSUPP);
	printf("PASS_E004PJ_%lu_OFFLINE_C11_ASSERTIONS_CSID_BF7_STATS_NOT_GENERIC_RDI_DONE_TWO_POSSIBLE_TRUSTED_WM16_SOURCES_NEITHER_PROVEN_ON_SP11_RUNTIME_DENIED\n",
	       assertions);
	return 0;
}
