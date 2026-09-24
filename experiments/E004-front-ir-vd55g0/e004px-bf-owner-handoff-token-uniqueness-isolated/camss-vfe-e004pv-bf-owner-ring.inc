/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E004pv: NATIVE kernel-compiled, C11-offline-testable queue design.
 * Isolated CAMSS copy ONLY. NO active ISR, VB2, DMA, MMIO, stream or arm caller.
 * Caller-supplied "verified" flags are DESIGN INPUTS, NOT hardware proof.
 * 4 slots; each queue token is opaque software ownership, not DMA address.
 */
#ifndef E004PV_NATIVE_BF_OWNER_RING_INC
#define E004PV_NATIVE_BF_OWNER_RING_INC

#ifdef __KERNEL__
#include <linux/errno.h>
#include <linux/spinlock.h>
#include <linux/string.h>
typedef u64 e004pv_u64;
typedef u16 e004pv_u16;
#define E004PV_LOCK_DECL unsigned long e004pv_irq_flags
#define E004PV_LOCK(q) spin_lock_irqsave(&(q)->lock, e004pv_irq_flags)
#define E004PV_UNLOCK(q) spin_unlock_irqrestore(&(q)->lock, e004pv_irq_flags)
#define E004PV_RETAIN __used
#else
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
typedef uint64_t e004pv_u64;
typedef uint16_t e004pv_u16;
#define E004PV_LOCK_DECL
#define E004PV_LOCK(q) ((void)(q))
#define E004PV_UNLOCK(q) ((void)(q))
#define E004PV_RETAIN
#endif

#define E004PV_BF_FIFO_INDEX 8u
#define E004PV_BF_EVENT_ID 0x0fu
#define E004PV_BF_WM_ID 16u
#define E004PV_DEPTH 4u

struct e004pv_bf_entry {
	e004pv_u64 owner_epoch;
	e004pv_u64 frame_epoch;
	e004pv_u64 queue_token;
	e004pv_u16 wm16_tag;
};

struct e004pv_bf_ring {
#ifdef __KERNEL__
	spinlock_t lock;
#endif
	struct e004pv_bf_entry entry[E004PV_DEPTH];
	e004pv_u64 owner_epoch;
	e004pv_u64 last_owner_epoch;
	e004pv_u64 last_frame_epoch;
	unsigned int head, tail, count;
	bool active, stop_requested;
};

struct e004pv_bf_completion {
	e004pv_u64 owner_epoch, frame_epoch, fifo8_queue_token;
	e004pv_u64 outstanding_wm16_queue_token;
	e004pv_u16 wm16_tag;
	unsigned int fifo_index, event_id, wm_id;
	bool fifo8_entry_verified;
	bool outstanding_wm16_match_nonnull;
	bool same_owner_and_frame_verified;
	bool independently_trusted_wm16_irq_and_ack;
	bool dma_iommu_safe_for_exact_buffer;
	bool all_other_five_groups_completed;
};

struct e004pv_bf_stop_fence {
	e004pv_u64 owner_epoch;
	bool source_input_quiescent;
	bool all_wms_bus_stopped;
	bool irq_masked_acknowledged_drained;
	bool all_generation_dma_complete;
	bool iommu_surface_safe;
	bool independent_same_owner_hw_evidence;
};

static void E004PV_RETAIN e004pv_bf_ring_init(struct e004pv_bf_ring *r)
{
	if (!r)
		return;
	memset(r, 0, sizeof(*r));
#ifdef __KERNEL__
	spin_lock_init(&r->lock);
#endif
}

/* New owner epoch must increase AFTER full safe stop. Frame epochs are
 * scoped to that owner: a new owner may legitimately start at frame 1.
 * INITIALIZE exactly once on a newly allocated object, never during reuse.
 */
static int E004PV_RETAIN
e004pv_bf_owner_begin(struct e004pv_bf_ring *r, e004pv_u64 owner_epoch,
		      bool independent_owner_grant)
{
	int ret = 0;
	E004PV_LOCK_DECL;

	if (!r || !owner_epoch)
		return -EINVAL;
	E004PV_LOCK(r);
	if (r->active || r->count)
		ret = -EBUSY;
	else if (!independent_owner_grant)
		ret = -EAGAIN;
	else if (owner_epoch <= r->last_owner_epoch)
		ret = -ESTALE;
	else {
		r->owner_epoch = r->last_owner_epoch = owner_epoch;
		/* last_owner_epoch (NOT last_frame_epoch) rejects old-owner replay. */
		r->last_frame_epoch = 0;
		r->active = true;
		r->stop_requested = false;
	}
	E004PV_UNLOCK(r);
	return ret;
}

/* Verifies producer return BEFORE increasing count; rejects missing owner,
 * invalid entry, stale/duplicate frame and full ring. An entered token is
 * opaque native software data, never a validated hardware/DMA address.
 */
static int E004PV_RETAIN
e004pv_bf_enqueue(struct e004pv_bf_ring *r, e004pv_u64 owner_epoch,
		  e004pv_u64 frame_epoch, e004pv_u64 queue_token,
		  e004pv_u16 tag, bool source_entry_copy_validated)
{
	int ret = 0;
	unsigned int i;
	E004PV_LOCK_DECL;

	if (!r || !owner_epoch || !frame_epoch || !queue_token)
		return -EINVAL;
	E004PV_LOCK(r);
	if (!r->active || r->owner_epoch != owner_epoch)
		ret = -ESTALE;
	else if (r->stop_requested)
		ret = -ESHUTDOWN;
	else if (!source_entry_copy_validated)
		ret = -EIO;
	else if (frame_epoch <= r->last_frame_epoch)
		ret = -ESTALE;
	else if (r->count >= E004PV_DEPTH)
		ret = -ENOSPC;
	else {
		/* One outstanding opaque token per owner. If the native source
		 * cannot disambiguate a repeated token, refuse the second insert.
		 */
		for (i = 0; i < r->count; i++) {
			const struct e004pv_bf_entry *e =
				&r->entry[(r->head + i) % E004PV_DEPTH];
			if (e->queue_token == queue_token) {
				ret = -EEXIST;
				break;
			}
		}
		if (!ret) {
			r->entry[r->tail] = (struct e004pv_bf_entry){
			.owner_epoch = owner_epoch,
			.frame_epoch = frame_epoch,
			.queue_token = queue_token,
			.wm16_tag = tag,
		};
		r->tail = (r->tail + 1u) % E004PV_DEPTH;
		r->count++;
			r->last_frame_epoch = frame_epoch;
		}
	}
	E004PV_UNLOCK(r);
	return ret;
}

/* This only removes an OPAQUE SOFTWARE ENTRY from the isolated model.
 * No vb2_buffer_done(), DMA unmap, CSID/VFE IRQ ACK, IOMMU call or free.
 * NO authentic proof producers exist yet. Never call from real ISR/stream.
 */
static int E004PV_RETAIN
e004pv_bf_confirm_and_pop(struct e004pv_bf_ring *r,
			  const struct e004pv_bf_completion *p)
{
	struct e004pv_bf_entry *e;
	int ret = 0;
	E004PV_LOCK_DECL;

	if (!r || !p)
		return -EINVAL;
	E004PV_LOCK(r);
	if (!r->active || !r->count)
		ret = -ENOENT;
	else if (p->owner_epoch != r->owner_epoch ||
		 p->owner_epoch != r->entry[r->head].owner_epoch ||
		 p->frame_epoch != r->entry[r->head].frame_epoch ||
		 p->fifo8_queue_token != r->entry[r->head].queue_token ||
		 p->outstanding_wm16_queue_token != r->entry[r->head].queue_token ||
		 p->wm16_tag != r->entry[r->head].wm16_tag)
		ret = -ESTALE;
	else if (p->fifo_index != E004PV_BF_FIFO_INDEX ||
		 p->event_id != E004PV_BF_EVENT_ID ||
		 p->wm_id != E004PV_BF_WM_ID)
		ret = -EINVAL;
	else if (!p->fifo8_entry_verified ||
		 !p->outstanding_wm16_match_nonnull ||
		 !p->same_owner_and_frame_verified ||
		 !p->independently_trusted_wm16_irq_and_ack ||
		 !p->dma_iommu_safe_for_exact_buffer ||
		 !p->all_other_five_groups_completed)
		ret = -EAGAIN;
	else {
		e = &r->entry[r->head];
		memset(e, 0, sizeof(*e));
		r->head = (r->head + 1u) % E004PV_DEPTH;
		r->count--;
	}
	E004PV_UNLOCK(r);
	return ret;
}

/* Stop request changes only software state: cannot retire buffers. */
static int E004PV_RETAIN
e004pv_bf_request_stop(struct e004pv_bf_ring *r, e004pv_u64 owner_epoch)
{
	int ret = 0;
	E004PV_LOCK_DECL;

	if (!r || !owner_epoch)
		return -EINVAL;
	E004PV_LOCK(r);
	if (!r->active || r->owner_epoch != owner_epoch)
		ret = -ESTALE;
	else if (r->stop_requested)
		ret = -EALREADY;
	else
		r->stop_requested = true;
	E004PV_UNLOCK(r);
	return ret;
}

static int E004PV_RETAIN
e004pv_bf_finish_stop(struct e004pv_bf_ring *r,
		       const struct e004pv_bf_stop_fence *f)
{
	int ret = 0;
	E004PV_LOCK_DECL;

	if (!r || !f)
		return -EINVAL;
	E004PV_LOCK(r);
	if (!r->active || f->owner_epoch != r->owner_epoch)
		ret = -ESTALE;
	else if (!r->stop_requested || r->count)
		ret = -EBUSY;
	else if (!f->source_input_quiescent || !f->all_wms_bus_stopped ||
		 !f->irq_masked_acknowledged_drained ||
		 !f->all_generation_dma_complete || !f->iommu_surface_safe ||
		 !f->independent_same_owner_hw_evidence)
		ret = -EAGAIN;
	else {
		r->active = false;
		r->stop_requested = false;
		r->owner_epoch = 0;
		/* Monotonic last epochs intentionally persist across handoff. */
	}
	E004PV_UNLOCK(r);
	return ret;
}

/* Compiled but unconditionally DENIED. No callers in original CAMSS.
 * Future physically proven producers and owner serialization require
 * a SEPARATE reviewed and opt-in integration, not boolean self-attestation.
 */
static int E004PV_RETAIN e004pv_rear_isp_runtime_authorize(void)
{
	return -EOPNOTSUPP;
}
#endif /* E004PV_NATIVE_BF_OWNER_RING_INC */
