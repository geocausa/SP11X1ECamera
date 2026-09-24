/* SPDX-License-Identifier: MIT
 * E004ov offline-only C11 test of DESIGN state machine. No camera access.
 */
#include "rear-stop-ownership.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static unsigned long tests;
static unsigned long permutations;

#define CHECK_EQ(expr, want) do { \
	int rc_ = (expr); \
	assert(rc_ == (want)); \
	++tests; \
} while (0)

static struct e004ov_completion proof(unsigned int i, uint64_t owner,
				     uint64_t frame)
{
	struct e004ov_completion p = {
		.owner_epoch = owner,
		.frame_epoch = frame,
		.queue_identity = 1000u + i,
		.event_id = e004ov_groups[i].event_id,
		.fifo_index = e004ov_groups[i].fifo_index,
		.hw_irq_status_verified = true,
		.group_fifo_entry_verified = true,
		.dma_generation_verified = true,
	};
	return p;
}
static struct e004ov_stop_fence fence(uint64_t owner, uint64_t frame)
{
	struct e004ov_stop_fence f = {
		.owner_epoch = owner,
		.frame_epoch = frame,
		.source_input_quiescent = true,
		.all_active_wm_bus_stopped = true,
		.irq_masked_acknowledged_and_drained = true,
		.all_generation_dma_finished = true,
		.iommu_buffer_ownership_safe = true,
		.same_generation_hardware_evidence = true,
	};
	return f;
}
static void run_order(const unsigned int idx[E004OV_GROUPS])
{
	struct e004ov_state s = { 0 };
	uint64_t ids[E004OV_GROUPS];
	struct e004ov_stop_fence f = fence(7, 42);
	unsigned int j;

	for (j = 0; j < E004OV_GROUPS; j++)
		ids[j] = 1000u + j;
	CHECK_EQ(e004ov_begin(&s, 7, 42, ids, true), 0);
	CHECK_EQ(e004ov_begin(&s, 8, 43, ids, true), -EBUSY);
	CHECK_EQ(e004ov_retire_after_stop(&s, &f), -EBUSY);
	CHECK_EQ(e004ov_request_stop(&s, 7, 41), -ESTALE);
	CHECK_EQ(e004ov_request_stop(&s, 7, 42), 0);
	CHECK_EQ(e004ov_request_stop(&s, 7, 42), -EALREADY);
	CHECK_EQ(e004ov_retire_after_stop(&s, &f), -EBUSY);
	for (j = 0; j < E004OV_GROUPS; ++j) {
		struct e004ov_completion p = proof(idx[j], 7, 42);
		struct e004ov_completion bad = p;

		bad.frame_epoch--;
		CHECK_EQ(e004ov_ack(&s, &bad), -ESTALE);
		bad = p;
		bad.owner_epoch--;
		CHECK_EQ(e004ov_ack(&s, &bad), -ESTALE);
		bad = p;
		bad.queue_identity++;
		CHECK_EQ(e004ov_ack(&s, &bad), -ESTALE);
		bad = p;
		bad.fifo_index ^= 0x1;
		CHECK_EQ(e004ov_ack(&s, &bad), -EINVAL);
		bad = p;
		bad.hw_irq_status_verified = false;
		CHECK_EQ(e004ov_ack(&s, &bad), -EAGAIN);
		bad = p;
		bad.group_fifo_entry_verified = false;
		CHECK_EQ(e004ov_ack(&s, &bad), -EAGAIN);
		bad = p;
		bad.dma_generation_verified = false;
		CHECK_EQ(e004ov_ack(&s, &bad), -EAGAIN);
		CHECK_EQ(e004ov_ack(&s, &p), 0);
		CHECK_EQ(e004ov_ack(&s, &p), -EALREADY);
		if (j + 1 < E004OV_GROUPS)
			CHECK_EQ(e004ov_retire_after_stop(&s, &f), -EBUSY);
	}
	assert(s.pending_groups == 0 && s.surface_in_flight && s.active);
	++tests;
	{
		struct e004ov_stop_fence bad = f;

		bad.owner_epoch--;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -ESTALE);
		bad = f;
		bad.frame_epoch--;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -ESTALE);
		bad = f;
		bad.source_input_quiescent = false;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -EAGAIN);
		bad = f;
		bad.all_active_wm_bus_stopped = false;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -EAGAIN);
		bad = f;
		bad.irq_masked_acknowledged_and_drained = false;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -EAGAIN);
		bad = f;
		bad.all_generation_dma_finished = false;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -EAGAIN);
		bad = f;
		bad.iommu_buffer_ownership_safe = false;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -EAGAIN);
		bad = f;
		bad.same_generation_hardware_evidence = false;
		CHECK_EQ(e004ov_retire_after_stop(&s, &bad), -EAGAIN);
	}
	CHECK_EQ(e004ov_retire_after_stop(&s, &f), 0);
	assert(!s.surface_in_flight && !s.active && !s.pending_groups &&
	       s.last_owner_epoch == 7 && s.last_frame_epoch == 42);
	++tests;
	CHECK_EQ(e004ov_retire_after_stop(&s, &f), -EINVAL);
	CHECK_EQ(e004ov_ack(&s, &(struct e004ov_completion){0}), -EINVAL);
	CHECK_EQ(e004ov_begin(&s, 7, 43, ids, true), -ESTALE);
	CHECK_EQ(e004ov_begin(&s, 8, 42, ids, true), -ESTALE);
	CHECK_EQ(e004ov_begin(&s, 8, 43, ids, false), -EAGAIN);
	CHECK_EQ(e004ov_begin(&s, 8, 43, ids, true), 0);
	CHECK_EQ(e004ov_request_stop(&s, 7, 42), -ESTALE);
	{
		struct e004ov_completion stale = proof(4, 7, 42);
		struct e004ov_completion wrong = proof(4, 8, 43);

		CHECK_EQ(e004ov_ack(&s, &stale), -ESTALE);
		wrong.event_id = 0x02; /* type-2 is not BF */
		CHECK_EQ(e004ov_ack(&s, &wrong), -EINVAL);
		wrong = proof(4, 8, 43);
		CHECK_EQ(e004ov_ack(&s, &wrong), 0);
	}
	++permutations;
}
static void enumerate(unsigned int order[E004OV_GROUPS],
		      bool used[E004OV_GROUPS], unsigned int depth)
{
	unsigned int i;

	if (depth == E004OV_GROUPS) {
		run_order(order);
		return;
	}
	for (i = 0; i < E004OV_GROUPS; ++i) {
		if (used[i])
			continue;
		used[i] = true;
		order[depth] = i;
		enumerate(order, used, depth + 1);
		used[i] = false;
	}
}
int main(void)
{
	unsigned int order[E004OV_GROUPS] = { 0 };
	bool used[E004OV_GROUPS] = { false };
	struct e004ov_state s = { 0 };
	uint64_t ids[E004OV_GROUPS] = { 1000,1001,1002,1003,1004,1005 };
	unsigned int i, masks = 0;

	CHECK_EQ(e004ov_begin(NULL, 1, 1, ids, true), -EINVAL);
	CHECK_EQ(e004ov_begin(&s, 0, 1, ids, true), -EINVAL);
	CHECK_EQ(e004ov_begin(&s, 1, 0, ids, true), -EINVAL);
	CHECK_EQ(e004ov_begin(&s, 1, 1, NULL, true), -EINVAL);
	CHECK_EQ(e004ov_begin(&s, 1, 1, ids, false), -EAGAIN);
	for (i = 0; i < E004OV_GROUPS; ++i) {
		assert(e004ov_group_for_event(e004ov_groups[i].event_id) == (int)i);
		assert(e004ov_groups[i].wm_mask);
		assert(!(masks & e004ov_groups[i].wm_mask));
		masks |= e004ov_groups[i].wm_mask;
		++tests;
	}
	assert(masks == 0x03ff);
	++tests;
	assert(e004ov_group_for_event(0x02) == -ENOENT);
	++tests;
	ids[4] = 0;
	CHECK_EQ(e004ov_begin(&s, 1, 1, ids, true), -EINVAL);
	assert(!s.active && !s.surface_in_flight && !s.last_frame_epoch);
	++tests;
	enumerate(order, used, 0);
	assert(permutations == 720);
	printf("PASS_E004OV_OFFLINE_C11_%lu_PERMUTATIONS_%lu_ASSERTIONS_NO_CAMERA_HARDWARE_NO_RUNTIME_ARM\n",
	       permutations, tests);
	return 0;
}
