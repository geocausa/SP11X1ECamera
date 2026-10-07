/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_OWNER_H
#define NATIVE_FRONT_OWNER_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
#include <linux/string.h>
typedef u32 native_owner_u32;
typedef u64 native_owner_u64;
#else
#include <stdint.h>
#include <errno.h>
#include <string.h>
typedef uint32_t native_owner_u32;
typedef uint64_t native_owner_u64;
#endif

#define NATIVE_OWNER_GROUPS 5
#define NATIVE_OWNER_WMS 9
#define NATIVE_OWNER_HISTORY 8

/* Order: WM0/1/2/3, WM11/12/13/14/16. Front video is one four-WM group. */
static const native_owner_u32 native_owner_group_masks[NATIVE_OWNER_GROUPS] = {
	0x00f, 0x030, 0x040, 0x080, 0x100,
};
struct native_owner_event {
	native_owner_u64 epoch;
	native_owner_u32 sequence;
	native_owner_u32 mask;
	native_owner_u32 consumed[NATIVE_OWNER_WMS];
};
struct native_owner_history {
	native_owner_u64 epoch;
	native_owner_u32 last[NATIVE_OWNER_GROUPS];
	native_owner_u32 errors;
	struct native_owner_event event[NATIVE_OWNER_GROUPS][NATIVE_OWNER_HISTORY];
};

/* The caller serializes producer, reader and reset (kernel IRQ spinlock). */
static inline int native_owner_reset(struct native_owner_history *h,
				    native_owner_u64 epoch)
{
	if (!h || !epoch)
		return -EINVAL;
	memset(h, 0, sizeof(*h));
	h->epoch = epoch;
	return 0;
}
static inline int native_owner_publish(struct native_owner_history *h,
				      unsigned int group,
				      native_owner_u32 sequence,
				      native_owner_u32 mask,
				      const native_owner_u32 consumed[NATIVE_OWNER_WMS])
{
	struct native_owner_event *e;
	if (!h || !h->epoch || !consumed || group >= NATIVE_OWNER_GROUPS)
		return -EINVAL;
	if (!sequence || h->last[group] == (native_owner_u32)-1 ||
	    sequence != h->last[group] + 1 ||
	    mask != native_owner_group_masks[group]) {
		h->errors++;
		return -EPROTO;
	}
	e = &h->event[group][sequence % NATIVE_OWNER_HISTORY];
	e->epoch = h->epoch;
	e->sequence = sequence;
	e->mask = mask;
	memcpy(e->consumed, consumed, sizeof(e->consumed));
	h->last[group] = sequence;
	return 0;
}
static inline int native_owner_check(const struct native_owner_history *h,
				    native_owner_u64 epoch, unsigned int group,
				    native_owner_u32 sequence,
				    const native_owner_u32 expected[NATIVE_OWNER_WMS])
{
	const struct native_owner_event *e;
	unsigned int i;
	if (!h || !epoch || !expected || !sequence || group >= NATIVE_OWNER_GROUPS)
		return -EINVAL;
	if (h->epoch != epoch)
		return -ESTALE;
	if (h->errors)
		return -EPROTO;
	e = &h->event[group][sequence % NATIVE_OWNER_HISTORY];
	if (e->epoch != epoch || e->sequence != sequence)
		return -ESTALE;
	if (e->mask != native_owner_group_masks[group])
		return -EPROTO;
	for (i = 0; i < NATIVE_OWNER_WMS; i++)
		if ((e->mask & (1u << i)) && (!expected[i] ||
		    e->consumed[i] != expected[i]))
			return -EPROTO;
	return 0;
}
#endif
