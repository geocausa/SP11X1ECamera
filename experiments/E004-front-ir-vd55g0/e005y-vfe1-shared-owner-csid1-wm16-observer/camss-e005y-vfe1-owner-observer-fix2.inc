/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E005y: shared X1E VFE1 FRONT/REAR owner and non-retiring CSID1 BF/WM16
 * observer. Isolated candidate only.
 */
#ifndef E005Y_VFE1_OWNER_OBSERVER_INC
#define E005Y_VFE1_OWNER_OBSERVER_INC

#include <linux/errno.h>
#include <linux/spinlock.h>
#include <linux/string.h>
#include <linux/types.h>

#define E005Y_CSID1_BF_BIT BIT(7)

enum e005y_vfe1_owner_id {
	E005Y_VFE1_OWNER_NONE = 0,
	E005Y_VFE1_OWNER_FRONT = 1,
	E005Y_VFE1_OWNER_REAR = 2,
};

enum e005y_bf_observation {
	E005Y_BF_NONE = 0,
	E005Y_BF_FRONT = 1,
	E005Y_BF_REAR = 2,
	E005Y_BF_UNATTRIBUTED = 3,
};

struct e005y_vfe1_owner {
	spinlock_t lock;
	u64 last_epoch;
	u64 active_epoch;
	enum e005y_vfe1_owner_id active_owner;
	bool unsafe_stop_pinned;

	u64 front_bf_count;
	u64 rear_bf_count;
	u64 unattributed_bf_count;
	u64 rear_wm16_nonzero_count;
	u64 rear_wm16_changed_count;
	u32 last_bf_status;
	u32 last_rear_wm16_addr_status0;
};

static inline void e005y_vfe1_owner_init(struct e005y_vfe1_owner *o)
{
	if (!o)
		return;
	memset(o, 0, sizeof(*o));
	spin_lock_init(&o->lock);
}

static inline int e005y_vfe1_owner_acquire(struct e005y_vfe1_owner *o,
				    enum e005y_vfe1_owner_id who,
				    bool exact_route_validated,
				    u64 *epoch)
{
	unsigned long flags;
	int ret = 0;

	if (!o || !epoch || !exact_route_validated ||
	    (who != E005Y_VFE1_OWNER_FRONT && who != E005Y_VFE1_OWNER_REAR))
		return -EINVAL;

	*epoch = 0;
	spin_lock_irqsave(&o->lock, flags);
	if (o->unsafe_stop_pinned)
		ret = -ESHUTDOWN;
	else if (o->active_owner != E005Y_VFE1_OWNER_NONE || o->active_epoch)
		ret = -EBUSY;
	else if (o->last_epoch == U64_MAX)
		ret = -EOVERFLOW;
	else {
		o->last_epoch++;
		o->active_epoch = o->last_epoch;
		o->active_owner = who;
		*epoch = o->active_epoch;
	}
	spin_unlock_irqrestore(&o->lock, flags);

	return ret;
}

static inline int e005y_vfe1_owner_release(struct e005y_vfe1_owner *o,
				    enum e005y_vfe1_owner_id who,
				    u64 epoch,
				    bool hardware_teardown_safe)
{
	unsigned long flags;
	int ret = 0;

	if (!o || !epoch ||
	    (who != E005Y_VFE1_OWNER_FRONT && who != E005Y_VFE1_OWNER_REAR))
		return -EINVAL;

	spin_lock_irqsave(&o->lock, flags);
	if (o->active_owner != who || o->active_epoch != epoch)
		ret = -ESTALE;
	else if (!hardware_teardown_safe) {
		o->unsafe_stop_pinned = true;
		ret = -EIO;
	} else if (o->unsafe_stop_pinned) {
		ret = -ESHUTDOWN;
	} else {
		o->active_owner = E005Y_VFE1_OWNER_NONE;
		o->active_epoch = 0;
	}
	spin_unlock_irqrestore(&o->lock, flags);

	return ret;
}

/*
 * First half of a rear observation: establish a stable owner epoch before
 * doing the read-only WM16 MMIO sample. The second half rechecks the same
 * epoch, so a concurrent handoff cannot misattribute the sample.
 */
static inline bool e005y_vfe1_rear_sample_begin(struct e005y_vfe1_owner *o,
					 bool exact_rear_route_now,
					 u64 *epoch)
{
	unsigned long flags;
	bool ok = false;

	if (!o || !epoch || !exact_rear_route_now)
		return false;

	*epoch = 0;
	spin_lock_irqsave(&o->lock, flags);
	if (!o->unsafe_stop_pinned &&
	    o->active_owner == E005Y_VFE1_OWNER_REAR &&
	    o->active_epoch) {
		*epoch = o->active_epoch;
		ok = true;
	}
	spin_unlock_irqrestore(&o->lock, flags);
	return ok;
}

static enum e005y_bf_observation
e005y_vfe1_observe_bf(struct e005y_vfe1_owner *o,
		      bool exact_front_route_now,
		      bool exact_rear_route_now,
		      u32 already_latched_status,
		      u64 rear_sample_epoch,
		      bool rear_wm16_sample_valid,
		      u32 rear_wm16_addr_status0)
{
	unsigned long flags;
	enum e005y_bf_observation result = E005Y_BF_UNATTRIBUTED;

	if (!o || !(already_latched_status & E005Y_CSID1_BF_BIT))
		return E005Y_BF_NONE;

	spin_lock_irqsave(&o->lock, flags);
	o->last_bf_status = already_latched_status;

	if (!o->unsafe_stop_pinned &&
	    o->active_owner == E005Y_VFE1_OWNER_FRONT &&
	    o->active_epoch && exact_front_route_now) {
		o->front_bf_count++;
		result = E005Y_BF_FRONT;
	} else if (!o->unsafe_stop_pinned &&
		   o->active_owner == E005Y_VFE1_OWNER_REAR &&
		   o->active_epoch == rear_sample_epoch &&
		   rear_sample_epoch && exact_rear_route_now &&
		   rear_wm16_sample_valid) {
		o->rear_bf_count++;
		if (rear_wm16_addr_status0)
			o->rear_wm16_nonzero_count++;
		if (o->last_rear_wm16_addr_status0 &&
		    o->last_rear_wm16_addr_status0 != rear_wm16_addr_status0)
			o->rear_wm16_changed_count++;
		o->last_rear_wm16_addr_status0 = rear_wm16_addr_status0;
		result = E005Y_BF_REAR;
	} else {
		o->unattributed_bf_count++;
	}
	spin_unlock_irqrestore(&o->lock, flags);

	return result;
}

/* Deliberately no rear runtime caller in E005y build-only stage. */
static int __maybe_unused e005y_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif /* E005Y_VFE1_OWNER_OBSERVER_INC */
