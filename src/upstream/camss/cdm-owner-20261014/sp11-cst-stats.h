/* SPDX-License-Identifier: GPL-2.0-only */
/* Typed source fragments; no tuning presets, private input, MMIO or DMA.
 * CST auxiliary-lane meaning still requires review; not a public ABI.
 * See CST-STATS-PROVENANCE-20261011.md for field provenance and limits.
 */
#ifndef SP11_OPEN_CST_STATS_H
#define SP11_OPEN_CST_STATS_H
#include "sp11-front-fields.h"

#define SP11_CST_COMMAND_BYTES 92U
#define SP11_RS_COMMAND_BYTES 32U
#define SP11_BHIST_GEOMETRY_BYTES 12U

struct sp11_cst_config {
	s16 matrix[9];
	s16 offset[3], auxiliary[3];
	u32 minimum[3], maximum[3];
	bool enabled;
};

struct sp11_rs_config {
	u32 left, top, width, height;
	u32 columns, rows;
	bool color_conversion;
};

/* Region-count field only; origin zero. No channel/enable/offset or DMI reset. */
struct sp11_bhist_geometry {
	u32 width, height;
};

static inline int sp11_cst_validate(const struct sp11_cst_config *s)
{
	unsigned int i;

	if (!s)
		return -EINVAL;
	for (i = 0; i < 9; i++)
		if (s->matrix[i] < -4096 || s->matrix[i] > 4095)
			return -ERANGE;
	for (i = 0; i < 3; i++)
		if (s->offset[i] < -4096 || s->offset[i] > 4095 ||
		    s->auxiliary[i] < -4096 || s->auxiliary[i] > 4095 ||
		    s->minimum[i] > s->maximum[i] || s->maximum[i] > 4095)
			return -ERANGE;
	return 0;
}

static inline int sp11_cst_commands(u8 *out, size_t capacity,
				   const struct sp11_cst_config *s)
{
	u8 tmp[SP11_CST_COMMAND_BYTES];
	u32 w[18], enable;
	unsigned int i;

	int ret;

	if (!out || !s)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
	ret = sp11_cst_validate(s);
	if (ret)
		return ret;
	for (i = 0; i < 3; i++) {
		w[6 * i] = sp11_front_pair(s->matrix[3 * i], s->matrix[3 * i + 1]);
		w[6 * i + 1] = sp11_front_pair(s->matrix[3 * i + 2], 0);
		w[6 * i + 2] = ((u32)s->offset[i] & 0x1fffU) << 19;
		w[6 * i + 3] = ((u32)s->auxiliary[i] & 0x1fffU) << 19;
		w[6 * i + 4] = s->minimum[i] << 20;
		w[6 * i + 5] = s->maximum[i] << 20;
	}
	enable = s->enabled ? 1U : 0U;
	ret = sp11_cdm_reg_cont(tmp, 12, 0x6160, &enable, 1);
	if (ret)
		return ret;
	ret = sp11_cdm_reg_cont(tmp + 12, sizeof(tmp) - 12, 0x6168, w, 18);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

static inline unsigned int sp11_rs_shift(u32 width, u32 height)
{
	u32 area = width * height;
	unsigned int bits = 0;

	while (area) {
		bits++;
		area >>= 1;
	}
	return bits > 4 ? bits - 4 : 0;
}

static inline int sp11_rs_validate(const struct sp11_rs_config *s,
				  u32 active_width, u32 active_height)
{
	u32 cw, ch;

	if (!s || !active_width || !active_height || !s->width || !s->height ||
	    !s->columns || !s->rows)
		return -EINVAL;
	if (active_width > 16384 || active_height > 16384 ||
	    s->left > 0x1fff || s->top > 0x3fff || ((s->left | s->top) & 1U) ||
	    s->left >= active_width || s->top >= active_height ||
	    s->width > active_width - s->left || s->height > active_height - s->top ||
	    s->columns > 16 || s->rows > 1024)
		return -ERANGE;
	cw = s->width / s->columns;
	ch = (s->height / s->rows) & ~1U;
	if (cw < 2 || cw > 8192 || ch < 2 || ch > 16 || sp11_rs_shift(cw, ch) > 15)
		return -ERANGE;
	return 0;
}

/* Enabled single-stripe row-sum fragment. Cell floor leaves explicit margins.
 * Does not establish statistic DMA size, parser layout or anti-flicker policy.
 */
static inline int sp11_rs_commands(u8 *out, size_t capacity,
				  u32 active_width, u32 active_height,
				  const struct sp11_rs_config *s)
{
	u8 tmp[SP11_RS_COMMAND_BYTES];
	u32 cfg, w[3], cw, ch;
	int ret;

	if (!out || !s)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
	ret = sp11_rs_validate(s, active_width, active_height);
	if (ret)
		return ret;
	cw = s->width / s->columns;
	ch = (s->height / s->rows) & ~1U;
	cfg = 1U | (s->color_conversion ? 0x10U : 0U) | sp11_rs_shift(cw, ch) << 8;
	w[0] = s->top << 16 | s->left;
	w[1] = (s->rows - 1) << 16 | (s->columns - 1);
	w[2] = (ch - 1) << 16 | (cw - 1);
	ret = sp11_cdm_reg_cont(tmp, 12, 0xbe60, &cfg, 1);
	if (ret)
		return ret;
	ret = sp11_cdm_reg_cont(tmp + 12, sizeof(tmp) - 12, 0xbe68, w, 3);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

static inline int sp11_bhist_geometry_commands(u8 *out, size_t capacity,
					      u32 active_width, u32 active_height,
					      const struct sp11_bhist_geometry *s)
{
	u32 word;

	if (!out || !s)
		return -EINVAL;
	if (capacity < SP11_BHIST_GEOMETRY_BYTES)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, SP11_BHIST_GEOMETRY_BYTES, s, sizeof(*s)))
		return -EINVAL;
	if (!active_width || !active_height || active_width > 16384 || active_height > 16384 ||
	    s->width < 4 || s->height < 2 || ((s->width | s->height) & 1U) ||
	    s->width > active_width || s->height > active_height)
		return -ERANGE;
	word = (s->width / 2 - 1) | (s->height / 2 - 1) << 16;
	return sp11_cdm_reg_cont(out, capacity, 0xb26c, &word, 1);
}
#endif
