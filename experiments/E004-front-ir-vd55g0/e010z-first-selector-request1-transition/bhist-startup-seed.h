/* SPDX-License-Identifier: MIT */
/*
 * E010z detached BHist startup/default seed lifecycle.
 *
 * Source/live evidence:
 *   cold/default seed = crop - floor(crop / 10)
 *   first selector consumes that seed
 *   caller-owned per-request config later replaces it.
 *
 * No MMIO, DMA or runtime camera wiring belongs here.
 */
#ifndef E010Z_BHIST_STARTUP_SEED_H
#define E010Z_BHIST_STARTUP_SEED_H

#include <linux/errno.h>
#include <linux/types.h>

struct e010z_bhist_roi {
	u32 left;
	u32 top;
	u32 width;
	u32 height;
};

struct e010z_bhist_startup_state {
	struct e010z_bhist_roi cold;
	struct e010z_bhist_roi live;
	u64 first_request_id;
	bool cold_ready;
	bool first_selected;
	bool live_ready;
};

static int e010z_bhist_make_cold_seed(struct e010z_bhist_startup_state *s,
				     u32 crop_width, u32 crop_height)
{
	if (!s || !crop_width || !crop_height || s->cold_ready)
		return -EINVAL;

	s->cold.left = 0;
	s->cold.top = 0;
	s->cold.width = crop_width - crop_width / 10;
	s->cold.height = crop_height - crop_height / 10;
	if (!s->cold.width || !s->cold.height)
		return -ERANGE;

	s->cold_ready = true;
	return 0;
}

static int e010z_bhist_first_select(struct e010z_bhist_startup_state *s,
				   u64 request_id,
				   struct e010z_bhist_roi *roi)
{
	if (!s || !roi || !s->cold_ready || s->first_selected)
		return -EINVAL;

	s->first_request_id = request_id;
	s->first_selected = true;
	*roi = s->cold;
	return 0;
}

static int e010z_bhist_replace_live(struct e010z_bhist_startup_state *s,
				   u64 request_id,
				   const struct e010z_bhist_roi *roi)
{
	if (!s || !roi || !s->first_selected || s->live_ready ||
	    request_id != s->first_request_id ||
	    !roi->width || !roi->height)
		return -EINVAL;

	s->live = *roi;
	s->live_ready = true;
	return 0;
}

static int e010z_bhist_live_select(const struct e010z_bhist_startup_state *s,
				  u64 request_id,
				  struct e010z_bhist_roi *roi)
{
	if (!s || !roi || !s->live_ready ||
	    request_id != s->first_request_id)
		return -EINVAL;

	*roi = s->live;
	return 0;
}

#endif
