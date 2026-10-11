/* SPDX-License-Identifier: GPL-2.0-only */
/* Source-only atomic fragment composition. This is NOT startup sequencing:
 * no module graph, output bus, complete histogram/AF, DMI or submission.
 */
#ifndef SP11_OPEN_FRAME_FIELDS_H
#define SP11_OPEN_FRAME_FIELDS_H
#include "sp11-front-fields.h"
#include "sp11-geometry-stats.h"
#include "sp11-cst-stats.h"

#define SP11_FRAME_FIELDS_BYTES (SP11_CST_COMMAND_BYTES + \
	SP11_FRONT_CCM_COMMAND_BYTES + SP11_FRONT_ROUND_COMMAND_BYTES + \
	SP11_GEOMETRY_COMMAND_BYTES + SP11_BG_SET_COMMAND_BYTES + \
	SP11_RS_COMMAND_BYTES + SP11_BHIST_GEOMETRY_BYTES)

struct sp11_frame_fields {
	struct sp11_geometry geometry;
	struct sp11_bg_config bg[3];
	struct sp11_cst_config cst;
	struct sp11_rs_config rs;
	struct sp11_bhist_geometry bhist;
	s16 ccm[9];
	unsigned int output_bits;
};

static inline int sp11_frame_fields_commands(u8 *out, size_t capacity,
					    const struct sp11_frame_fields *s)
{
	u8 tmp[SP11_FRAME_FIELDS_BYTES];
	size_t pos = 0;
	int ret;
	if (!out || !s)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
#define SP11_APPEND(call, bytes) do { \
	ret = (call); if (ret) return ret; pos += (bytes); \
} while (0)
	SP11_APPEND(sp11_cst_commands(tmp + pos, sizeof(tmp) - pos, &s->cst), SP11_CST_COMMAND_BYTES);
	SP11_APPEND(sp11_front_ccm_commands(tmp + pos, sizeof(tmp) - pos, s->ccm), SP11_FRONT_CCM_COMMAND_BYTES);
	SP11_APPEND(sp11_front_round_commands(tmp + pos, sizeof(tmp) - pos, s->output_bits), SP11_FRONT_ROUND_COMMAND_BYTES);
	SP11_APPEND(sp11_geometry_commands(tmp + pos, sizeof(tmp) - pos, &s->geometry), SP11_GEOMETRY_COMMAND_BYTES);
	SP11_APPEND(sp11_bg_set_commands(tmp + pos, sizeof(tmp) - pos,
		s->geometry.input_width, s->geometry.input_height, s->bg), SP11_BG_SET_COMMAND_BYTES);
	SP11_APPEND(sp11_rs_commands(tmp + pos, sizeof(tmp) - pos,
		s->geometry.input_width, s->geometry.input_height, &s->rs), SP11_RS_COMMAND_BYTES);
	SP11_APPEND(sp11_bhist_geometry_commands(tmp + pos, sizeof(tmp) - pos,
		s->geometry.input_width, s->geometry.input_height, &s->bhist), SP11_BHIST_GEOMETRY_BYTES);
#undef SP11_APPEND
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
