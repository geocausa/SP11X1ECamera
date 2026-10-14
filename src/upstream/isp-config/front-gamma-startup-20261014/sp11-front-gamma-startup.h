/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Independent startup data using the existing native tone conversion.
 * Own semantic RGB points are10-bit; the existing bridge emits12-bit Gamma.
 * No private default curve, profile, DMI address/selector or runtime caller.
 * Caller owns workspace; immutable points/policy and disjoint output extents.
 */
#ifndef SP11_FRONT_GAMMA_STARTUP_H
#define SP11_FRONT_GAMMA_STARTUP_H

#include "native-front-isp-params.h"
#include "sp11-front-cold-fields.h"

struct sp11_front_gamma_workspace {
	nf_gamma_u8 packet[NF_ISP_MAX_BYTES];
	nf_gamma_u32 words[NF_GAMMA_WORD_COUNT];
};

/* This reuses both actual codecs, not a second Gamma algorithm or public ABI.
 * Workspace is scratch and may change on failure; output never does.
 * A kernel caller must allocate/own the workspace outside its small stack.
 * Geometry/tag admission does not prove processing precision or optical parity.
 */
static inline int
sp11_front_gamma_startup(u8 *out, size_t capacity,
			 const struct sp11_front_cold_policy *policy,
			 const nf_gamma_u16 *points, size_t count,
			 struct sp11_front_gamma_workspace *workspace)
{
	u8 checked[SP11_FRONT_COLD_BYTES];
	int ret, update = 0;

	if (!out || !policy || !points || !workspace ||
	    count != NF_GAMMA_POINT_COUNT)
		return -EINVAL;
	if (capacity < NF_GAMMA_BYTES)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, NF_GAMMA_BYTES, policy, sizeof(*policy)) ||
	    sp11_cdm_overlap(out, NF_GAMMA_BYTES, points,
			     count * sizeof(*points)) ||
	    sp11_cdm_overlap(out, NF_GAMMA_BYTES, workspace,
			     sizeof(*workspace)) ||
	    sp11_cdm_overlap(workspace, sizeof(*workspace), points,
			     count * sizeof(*points)) ||
	    sp11_cdm_overlap(workspace, sizeof(*workspace), policy,
			     sizeof(*policy)))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	ret = native_front_isp_encode(points, count, workspace->packet,
				      sizeof(workspace->packet));
	if (ret)
		return ret;
	return native_front_isp_decode(workspace->packet,
				       sizeof(workspace->packet), workspace->words,
				       NF_GAMMA_WORD_COUNT, out, NF_GAMMA_BYTES,
				       &update);
}
#endif
