/* SPDX-License-Identifier: MIT */
/* Detached per-request AEC BHist ROI to Titan680 region-count handoff. */
#ifndef E009G_BHIST_REQUEST_H
#define E009G_BHIST_REQUEST_H
#include <linux/errno.h>
#include <linux/types.h>

struct e009g_bhist_roi {
	u32 left, top, width, height;
};

struct e009g_bhist_request {
	u64 request_id;
	u32 crop_width, crop_height;
	struct e009g_bhist_roi aec_roi;
	bool aec_roi_valid;
};

struct e009g_bhist_word {
	u64 request_id;
	u32 region_word;
	bool ready;
	bool consumed;
};

/* The caller must supply its own AEC ROI for this request. */
static int e009g_bhist_prepare(struct e009g_bhist_word *dst,
				const struct e009g_bhist_request *request)
{
	struct e006u_bhist16_state geometry;
	u32 candidate;
	int ret;

	if (!dst || !request || !request->aec_roi_valid ||
	    !request->crop_width || !request->crop_height ||
	    !request->aec_roi.width || !request->aec_roi.height)
		return -EINVAL;
	if (dst->ready || dst->consumed)
		return -EBUSY;
	if (request->aec_roi.left >= request->crop_width ||
	    request->aec_roi.top >= request->crop_height ||
	    request->aec_roi.width > request->crop_width - request->aec_roi.left ||
	    request->aec_roi.height > request->crop_height - request->aec_roi.top)
		return -ERANGE;
	geometry.roi_width = request->aec_roi.width;
	geometry.roi_height = request->aec_roi.height;
	/* Avoid silently truncating a larger count to Titan680's 13-bit field. */
	if ((geometry.roi_width >> 1) > 8192 ||
	    (geometry.roi_height >> 1) > 8192)
		return -ERANGE;
	ret = e006u_bhist16_region_word(&geometry, &candidate);
	if (ret)
		return ret;
	dst->region_word = candidate;
	dst->request_id = request->request_id;
	dst->ready = true;
	return 0;
}

static int e009g_bhist_consume(struct e009g_bhist_word *state,
			      u64 request_id, u32 *word)
{
	if (!state || !word || !state->ready || state->consumed ||
	    state->request_id != request_id)
		return -EINVAL;
	*word = state->region_word;
	state->consumed = true;
	return 0;
}
#endif
