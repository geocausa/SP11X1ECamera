/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E004pz: front-runner-scoped CSID1 status observation, isolated CAMSS only.
 * This is NOT a global VFE1 owner, not a rear authorization, and not an
 * exact WM16/FIFO8/DMA/IOMMU completion fence. No additional MMIO or IRQ ACK.
 *
 * The front grant MUST be issued only by an already-validated exclusive
 * custom front runner BEFORE it starts hardware. Stop/unsafe pin is paired
 * with the SAME runner's existing source/hardware teardown. Unrelated V4L2
 * paths remain unprotected until a future reviewed shared-owner integration.
 */
#ifndef E004PZ_FRONT_OWNER_BF_OBSERVER_INC
#define E004PZ_FRONT_OWNER_BF_OBSERVER_INC

#ifdef __KERNEL__
#include <linux/errno.h>
#include <linux/spinlock.h>
#include <linux/string.h>
#include <linux/types.h>
typedef u64 e004pz_u64;
typedef u32 e004pz_u32;
#define E004PZ_LOCK_DECL unsigned long e004pz_irqflags
#define E004PZ_LOCK(x) spin_lock_irqsave(&(x)->lock, e004pz_irqflags)
#define E004PZ_UNLOCK(x) spin_unlock_irqrestore(&(x)->lock, e004pz_irqflags)
#define E004PZ_MAX_EPOCH U64_MAX
#define E004PZ_KEEP __maybe_unused
#else
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
typedef uint64_t e004pz_u64;
typedef uint32_t e004pz_u32;
#define E004PZ_LOCK_DECL
#define E004PZ_LOCK(x) ((void)(x))
#define E004PZ_UNLOCK(x) ((void)(x))
#define E004PZ_MAX_EPOCH UINT64_MAX
#define E004PZ_KEEP
#endif

#define E004PZ_CSID1_BF_STATUS_BIT (1u << 7)

enum e004pz_irq_result {
	E004PZ_IRQ_NO_BF = 0,
	E004PZ_IRQ_FRONT_ROUTE_SCOPED = 1,
	E004PZ_IRQ_UNATTRIBUTED = 2,
};

struct e004pz_front_observer {
#ifdef __KERNEL__
	spinlock_t lock;
#endif
	e004pz_u64 last_owner_epoch;
	e004pz_u64 active_owner_epoch;
	e004pz_u64 last_front_bf_epoch;
	e004pz_u64 session_front_bf_count;
	e004pz_u64 lifetime_front_bf_count;
	e004pz_u64 lifetime_unattributed_bf_count;
	e004pz_u32 last_front_bf_status;
	bool front_runner_active;
	bool unsafe_stop_pinned;
};

static void E004PZ_KEEP
e004pz_front_observer_init(struct e004pz_front_observer *o)
{
	if (!o)
		return;
	memset(o, 0, sizeof(*o));
#ifdef __KERNEL__
	spin_lock_init(&o->lock);
#endif
}

/* Graph validation is performed by camss_x1e_pix_runner_validate().
 * This caller gate is a RUNNER scope only, not a global shared-VFE1 grant.
 */
static int E004PZ_KEEP
e004pz_front_runner_begin(struct e004pz_front_observer *o,
			  bool validated_exact_front_graph,
			  e004pz_u64 *new_epoch)
{
	int ret = 0;
	E004PZ_LOCK_DECL;

	if (!o || !new_epoch || !validated_exact_front_graph)
		return -EINVAL;
	*new_epoch = 0;
	E004PZ_LOCK(o);
	if (o->unsafe_stop_pinned)
		ret = -ESHUTDOWN;
	else if (o->front_runner_active)
		ret = -EBUSY;
	else if (o->last_owner_epoch == E004PZ_MAX_EPOCH)
		ret = -EOVERFLOW;
	else {
		o->last_owner_epoch++;
		o->active_owner_epoch = o->last_owner_epoch;
		o->session_front_bf_count = 0;
		o->front_runner_active = true;
		*new_epoch = o->active_owner_epoch;
	}
	E004PZ_UNLOCK(o);
	return ret;
}

/* Already-latched CSID1 BUF_DONE status, AFTER its existing ACK.
 * The caller must establish the CURRENT CONFIGURED front route from actual
 * CSID1 PHY+format state; a name/bit7 alone cannot identify sensor/owner.
 * No pointer/tag/callback/buffer-completion or hardware writes are here.
 */
static enum e004pz_irq_result E004PZ_KEEP
e004pz_observe_csid1_status(struct e004pz_front_observer *o,
			    bool exact_front_route_now,
			    e004pz_u32 already_latched_buf_done)
{
	enum e004pz_irq_result result = E004PZ_IRQ_UNATTRIBUTED;
	E004PZ_LOCK_DECL;

	if (!o || !(already_latched_buf_done & E004PZ_CSID1_BF_STATUS_BIT))
		return E004PZ_IRQ_NO_BF;

	E004PZ_LOCK(o);
	if (o->front_runner_active && !o->unsafe_stop_pinned &&
	    exact_front_route_now && o->active_owner_epoch) {
		o->session_front_bf_count++;
		o->lifetime_front_bf_count++;
		o->last_front_bf_epoch = o->active_owner_epoch;
		o->last_front_bf_status = already_latched_buf_done;
		result = E004PZ_IRQ_FRONT_ROUTE_SCOPED;
	} else {
		o->lifetime_unattributed_bf_count++;
	}
	E004PZ_UNLOCK(o);
	return result;
}

/* A failed real hardware stop PINS the front owner indefinitely until a
 * physically separate reboot; never claim the shared core was released.
 */
static int E004PZ_KEEP
e004pz_front_runner_end(struct e004pz_front_observer *o,
			e004pz_u64 expected_epoch,
			bool existing_hardware_teardown_safe)
{
	int ret = 0;
	E004PZ_LOCK_DECL;

	if (!o || !expected_epoch)
		return -EINVAL;
	E004PZ_LOCK(o);
	if (!o->front_runner_active || expected_epoch != o->active_owner_epoch)
		ret = -ESTALE;
	else if (!existing_hardware_teardown_safe) {
		o->unsafe_stop_pinned = true;
		ret = -EIO;
	} else if (o->unsafe_stop_pinned) {
		ret = -ESHUTDOWN;
	} else {
		o->active_owner_epoch = 0;
		o->front_runner_active = false;
		/* last_owner_epoch and lifetime counters survive safe handoff. */
	}
	E004PZ_UNLOCK(o);
	return ret;
}

/* Rear processed ISP is not connected to this front-only source proof. */
static int E004PZ_KEEP e004pz_rear_processed_isp_authorize(void)
{
	return -EOPNOTSUPP;
}
#endif /* E004PZ_FRONT_OWNER_BF_OBSERVER_INC */
