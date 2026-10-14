/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * CAMSS acquired-stage lifecycle, adapted from the retained native runner.
 * The caller retains DMA, graph, PM and module ownership after any stop fault.
 */
#ifndef CAMSS_VIDEO_LIFECYCLE_H
#define CAMSS_VIDEO_LIFECYCLE_H

#include <linux/errno.h>
#include <linux/types.h>

#define CAMSS_VIDEO_MAX_SUBDEVS 16

struct camss_video_stage {
	void *device;
	bool owned;
};

struct camss_video_lifecycle {
	struct camss_video_stage stages[CAMSS_VIDEO_MAX_SUBDEVS];
	unsigned int count;
	bool fault;
};

typedef int (*camss_video_stage_call)(void *context, void *device, bool on);

static inline int
camss_video_unwind(struct camss_video_lifecycle *state, void *context,
		   camss_video_stage_call call)
{
	unsigned int i = state->count;
	int first = 0;
	int ret;

	while (i--) {
		if (!state->stages[i].owned)
			continue;

		ret = call(context, state->stages[i].device, false);
		if (ret < 0 && ret != -ENOIOCTLCMD) {
			if (!first)
				first = ret;
			state->fault = true;
		} else {
			state->stages[i].owned = false;
		}
	}

	if (!state->fault)
		state->count = 0;

	return first;
}

static inline int
camss_video_start_owned(struct camss_video_lifecycle *state,
			void *const *devices, unsigned int count,
			void *context, camss_video_stage_call call)
{
	unsigned int i;
	int ret;

	if (state->fault)
		return -EIO;
	if (state->count)
		return -EBUSY;
	if (!count || count > CAMSS_VIDEO_MAX_SUBDEVS)
		return -EINVAL;

	state->count = count;
	for (i = 0; i < count; i++) {
		state->stages[i].device = devices[i];
		state->stages[i].owned = false;
	}

	for (i = 0; i < count; i++) {
		ret = call(context, devices[i], true);
		if (ret == -ENOIOCTLCMD)
			continue;
		if (ret < 0) {
			/* Preserve the start error even if acquired-stage unwind fails. */
			camss_video_unwind(state, context, call);
			return ret;
		}

		state->stages[i].owned = true;
	}

	return 0;
}

static inline int
camss_video_stop_owned(struct camss_video_lifecycle *state,
		       const unsigned int *order, void *context,
		       camss_video_stage_call call)
{
	unsigned int seen = 0;
	unsigned int i, index;
	int first = 0;
	int ret;

	if (state->fault)
		return -EIO;

	/* Reject malformed order before any hardware callback or release. */
	for (i = 0; i < state->count; i++) {
		index = order[i];
		if (index >= state->count || (seen & (1U << index))) {
			state->fault = true;
			return -EINVAL;
		}
		seen |= 1U << index;
	}

	for (i = 0; i < state->count; i++) {
		index = order[i];
		if (!state->stages[index].owned)
			continue;

		ret = call(context, state->stages[index].device, false);
		if (ret < 0 && ret != -ENOIOCTLCMD) {
			if (!first)
				first = ret;
			state->fault = true;
		} else {
			state->stages[index].owned = false;
		}
	}

	if (!state->fault)
		state->count = 0;

	return first;
}

#endif /* CAMSS_VIDEO_LIFECYCLE_H */
