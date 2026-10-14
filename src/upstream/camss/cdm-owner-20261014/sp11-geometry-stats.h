/* SPDX-License-Identifier: GPL-2.0-only */
/* Internal typed Titan680 fragments. No private carrier, DMA or submission.
 * Functional definitions: retained E006p/q/w/x/y semantic packers; see
 * GEOMETRY-STATS-PROVENANCE-20261011.md for provenance and hardware gates.
 */
#ifndef SP11_OPEN_GEOMETRY_STATS_H
#define SP11_OPEN_GEOMETRY_STATS_H
#include "sp11-cdm.h"

#define SP11_GEOMETRY_COMMAND_BYTES 128U
#define SP11_BG_COMMAND_BYTES 80U
#define SP11_BG_SET_COMMAND_BYTES 240U

/* Full-frame, origin-zero, single-stripe 4:2:0 downscale only. */
struct sp11_geometry {
	u32 input_width, input_height;
	u32 output_width, output_height;
};

struct sp11_bg_config {
	u32 left, top, width, height;
	u32 columns, rows;
	u32 threshold_r, threshold_b, threshold_gr, threshold_gb;
	u32 black_level;
	u8 y_weight_q4[3];
	bool quad_sync, enabled;
};

enum sp11_bg_kind {
	SP11_BG_AEC, SP11_BG_TINTLESS, SP11_BG_AWB
};

static inline u32 sp11_geometry_round(u64 numerator, u32 denominator)
{
	return (u32)((numerator + denominator / 2U) / denominator);
}

static inline int sp11_geometry_validate(const struct sp11_geometry *s)
{
	u32 iw, ih, ow, oh;

	if (!s)
		return -EINVAL;
	iw = s->input_width; ih = s->input_height;
	ow = s->output_width; oh = s->output_height;
	if (!iw || !ih || !ow || !oh || ((iw | ih | ow | oh) & 1U))
		return -EINVAL;
	if (iw > 0x4000 || ih > 0x4000 || ow > iw || oh > ih ||
	    (u64)iw > (u64)(ow / 2) * 128U ||
	    (u64)ih > (u64)(oh / 2) * 128U)
		return -ERANGE;
	return 0;
}

static inline u32 sp11_geometry_phase(u32 input, u32 output)
{
	u32 interp = input > output * 64U ? 0U :
		     input > output * 32U ? 1U :
		     input > output * 16U ? 2U : 3U;
	return interp << 30 | sp11_geometry_round((u64)input << 21, output);
}

static inline void sp11_geometry_axis(u32 input, u32 output,
				    u32 *phase, u32 *initial, u32 *frac)
{
	*phase = sp11_geometry_phase(input, output);
	*initial = 0; *frac = 0;
	if (input > output && input < output * 2U) {
		u64 residual = (u64)output * 2U - input;
		*initial = (0U - sp11_geometry_round(residual << 20, output)) & 0x1fffffffU;
		*frac = sp11_geometry_round(residual * 16U, output) & 0xfU;
	}
}

static inline int sp11_geometry_commands_state(u8 *out, size_t capacity,
					      const struct sp11_geometry *s,
					      bool enabled)
{
	u8 tmp[SP11_GEOMETRY_COMMAND_BYTES];
	u32 words[10], fx, fy, crop[2];
	unsigned int ch;
	int ret;

	if (!out || !s)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
	ret = sp11_geometry_validate(s);
	if (ret)
		return ret;
	for (ch = 0; ch < 2; ch++) {
		u32 divisor = ch ? 2U : 1U;

		words[0] = enabled ? 1U : 0U;
		words[1] = 0x600;
		words[2] = (s->input_width - 1) << 16 | (s->input_height - 1);
		sp11_geometry_axis(s->input_width, s->output_width / divisor,
				   &words[3], &words[4], &fx);
		sp11_geometry_axis(s->input_height, s->output_height / divisor,
				   &words[5], &words[6], &fy);
		words[7] = s->input_height - 1;
		words[8] = s->input_width - 1;
		words[9] = fx << 16 | fy;
		ret = sp11_cdm_reg_cont(tmp + 48 * ch, 48,
					ch ? 0x9a60 : 0x9860, words, 10);
		if (ret)
			return ret;
		crop[0] = s->output_height / divisor - 1;
		crop[1] = s->output_width / divisor - 1;
		ret = sp11_cdm_reg_cont(tmp + 96 + 16 * ch, 16,
					ch ? 0x9e68 : 0x9c68, crop, 2);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

static inline int sp11_geometry_commands(u8 *out, size_t capacity,
					const struct sp11_geometry *s)
{
	return sp11_geometry_commands_state(out, capacity, s, true);
}

/* Validate ROI against the actual active sensor region, not just field fit.
 * Floor each cell to an even Bayer extent; unmetered right/bottom edges remain
 * explicit policy. Sample count is geometric, not a DMA allocation size.
 */
static inline int sp11_bg_validate(const struct sp11_bg_config *s,
				  u32 active_width, u32 active_height)
{
	u32 cw, ch;

	unsigned int i;

	if (!s || !active_width || !active_height ||
	    !s->width || !s->height || !s->columns || !s->rows)
		return -EINVAL;
	if (active_width > 0x4000 || active_height > 0x4000 ||
	    s->left >= active_width || s->top >= active_height ||
	    s->width > active_width - s->left || s->height > active_height - s->top ||
	    ((s->left | s->top) & 1U) || s->columns > 64 || s->rows > 64)
		return -ERANGE;
	cw = (s->width / s->columns) & ~1U;
	ch = (s->height / s->rows) & ~1U;
	if (cw < 16 || cw > 512 || ch < 16 || ch > 512 ||
	    s->threshold_r > 0x3ffff || s->threshold_b > 0x3ffff ||
	    s->threshold_gr > 0x3ffff || s->threshold_gb > 0x3ffff ||
	    s->black_level > 0x3ffff)
		return -ERANGE;
	for (i = 0; i < 3; i++)
		if (s->y_weight_q4[i] > 0x7f)
			return -ERANGE;
	return 0;
}

static inline int sp11_bg_commands(u8 *out, size_t capacity,
				  enum sp11_bg_kind kind,
				  u32 active_width, u32 active_height,
				  const struct sp11_bg_config *s)
{
	u8 tmp[SP11_BG_COMMAND_BYTES];
	u32 w[18], base;
	unsigned int i;

	int ret;

	if (!out || !s || (kind != SP11_BG_AEC && kind != SP11_BG_TINTLESS && kind != SP11_BG_AWB))
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
	ret = sp11_bg_validate(s, active_width, active_height);
	if (ret)
		return ret;
	w[0] = 0xffff0000U | (s->quad_sync ? 1U << 9 : 0U) | (s->enabled ? 1U : 0U);
	w[1] = s->black_level << 14;
	w[2] = (u32)s->y_weight_q4[0] << 9 |
	       (u32)s->y_weight_q4[1] << 17 |
	       (u32)s->y_weight_q4[2] << 25;
	w[3] = (s->columns - 1) << 16 | s->left;
	w[4] = ((s->width / s->columns) & ~1U) - 1;
	w[5] = (s->rows - 1) << 16 | s->top;
	w[6] = ((s->height / s->rows) & ~1U) - 1;
	w[7] = 0;
	w[8] = s->threshold_gr << 14; w[9] = s->threshold_r << 14;
	w[10] = s->threshold_gb << 14; w[11] = s->threshold_b << 14;
	w[12] = s->threshold_gb << 14;
	for (i = 13; i < 18; i++)
		w[i] = 0U - (s->black_level << 13);
	base = kind == SP11_BG_AEC ? 0xb060 : kind == SP11_BG_TINTLESS ? 0xb660 : 0xb860;
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), base, w, 18);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* AEC, tintless, AWB are explicit independent caller-owned inputs. No presets. */
static inline int sp11_bg_set_commands(u8 *out, size_t capacity,
				      u32 active_width, u32 active_height,
				      const struct sp11_bg_config config[3])
{
	u8 tmp[SP11_BG_SET_COMMAND_BYTES];
	unsigned int i;

	int ret;

	if (!out || !config)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), config, 3 * sizeof(*config)))
		return -EINVAL;
	for (i = 0; i < 3; i++) {
		ret = sp11_bg_commands(tmp + i * SP11_BG_COMMAND_BYTES,
			SP11_BG_COMMAND_BYTES, (enum sp11_bg_kind)i,
			active_width, active_height, &config[i]);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
