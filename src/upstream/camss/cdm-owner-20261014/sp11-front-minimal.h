/* SPDX-License-Identifier: GPL-2.0-only */
/* Independent minimal front pixel-processing program, not a bootable provider.
 * No firmware reader, legacy carrier, table input, DMI address or MMIO.
 * Public register names: pinned VFE680 GPL header. The four demosaic words
 * are the posted GPL IFE RFC's bring-up parameters, with attribution and
 * qualification limits in FRONT-MINIMAL-PROVENANCE-20261011.md.
 */
#ifndef SP11_OPEN_FRONT_MINIMAL_H
#define SP11_OPEN_FRONT_MINIMAL_H
#include "sp11-geometry-stats.h"
#include "sp11-cst-stats.h"

enum sp11_front_bayer {
	SP11_FRONT_RGGB, SP11_FRONT_GRBG, SP11_FRONT_GBRG, SP11_FRONT_BGGR
};

struct sp11_front_minimal {
	struct sp11_geometry geometry;
	unsigned int input_bits;
	enum sp11_front_bayer bayer;
};

/* Exclusive, stopped full VFE pixel path is an integration prerequisite.
 * Zero every listed module before programming: optional IQ, LUT consumers,
 * statistics and unused pixel outputs cannot inherit prior settings.
 * This does not stop bus clients or prove DMA retirement.
 */
static const u32 sp11_front_minimal_module_regs[] = {
	0x3960, /* DEMUX */
	0x3b60, /* CHANNEL_GAIN */
	0x3d60, /* BPC_PDPC */
	0x3f60, /* BINCORRECT */
	0x4160, /* COMPDECOMP */
	0x4360, /* LSC */
	0x4560, /* WB_GAIN */
	0x4760, /* GIC */
	0x4960, /* BPC_ABF */
	0x4b60, /* BLS */
	0x4d60, /* BAYER_GTM */
	0x5260, /* BAYER_LTM */
	0x5460, /* LCAC */
	0x5660, /* DEMOSAIC */
	0x5860, /* COLOR_CORRECT */
	0x5a60, /* GTM */
	0x5f60, /* GLUT */
	0x6160, /* COLOR_XFORM */
	0x6360, /* UVG */
	0x6560, /* PREPROCESSOR */
	0x6760, /* CHROMA_UP */
	0x6960, /* SPARSE_PD_EXT */
	0x6b60, /* LCR */
	0x6d60, /* COMPDECOMP_HVX_TX */
	0x6f60, /* COMPDECOMP_HVX_RX */
	0x7160, /* GTM_FD_OUT */
	0x7660, /* CROP_RND_CLAMP_PIXEL_RAW_OUT */
	0x7860, /* DOWNSCALE_MN_Y_FD_OUT */
	0x7a60, /* DOWNSCALE_MN_C_FD_OUT */
	0x7c60, /* CROP_RND_CLAMP_POST_DOWNSCALE_MN_Y_FD_OUT */
	0x7e60, /* CROP_RND_CLAMP_POST_DOWNSCALE_MN_C_FD_OUT */
	0x8060, /* DOWNSCALE_MN_Y_DISP_OUT */
	0x8260, /* DOWNSCALE_MN_C_DISP_OUT */
	0x8460, /* CROP_RND_CLAMP_POST_DOWNSCALE_MN_Y_DISP_OUT */
	0x8660, /* CROP_RND_CLAMP_POST_DOWNSCALE_MN_C_DISP_OUT */
	0x8860, /* DOWNSCALE_4TO1_Y_DISP_DS4_OUT */
	0x8a60, /* DOWNSCALE_4TO1_C_DISP_DS4_OUT */
	0x8c60, /* CROP_RND_CLAMP_POST_DOWNSCALE_4TO1_Y_DISP_DS4_OUT */
	0x8e60, /* CROP_RND_CLAMP_POST_DOWNSCALE_4TO1_C_DISP_DS4_OUT */
	0x9060, /* DOWNSCALE_4TO1_Y_DISP_DS16_OUT */
	0x9260, /* DOWNSCALE_4TO1_C_DISP_DS16_OUT */
	0x9460, /* CROP_RND_CLAMP_POST_DOWNSCALE_4TO1_Y_DISP_DS16_OUT */
	0x9660, /* CROP_RND_CLAMP_POST_DOWNSCALE_4TO1_C_DISP_DS16_OUT */
	0x9860, /* DOWNSCALE_MN_Y_VID_OUT */
	0x9a60, /* DOWNSCALE_MN_C_VID_OUT */
	0x9c60, /* CROP_RND_CLAMP_POST_DOWNSCALE_MN_Y_VID_OUT */
	0x9e60, /* CROP_RND_CLAMP_POST_DOWNSCALE_MN_C_VID_OUT */
	0xa060, /* DSX_Y_VID_OUT */
	0xa260, /* DSX_C_VID_OUT */
	0xa460, /* CROP_RND_CLAMP_POST_DSX_Y_VID_OUT */
	0xa660, /* CROP_RND_CLAMP_POST_DSX_C_VID_OUT */
	0xa860, /* DOWNSCALE_4TO1_Y_VID_DS16_OUT */
	0xaa60, /* DOWNSCALE_4TO1_C_VID_DS16_OUT */
	0xac60, /* CROP_RND_CLAMP_POST_DOWNSCALE_4TO1_Y_VID_DS16_OUT */
	0xae60, /* CROP_RND_CLAMP_POST_DOWNSCALE_4TO1_C_VID_DS16_OUT */
	0xb060, /* STATS_AEC_BE */
	0xb260, /* STATS_AEC_BHIST */
	0xb460, /* STATS_BHIST */
	0xb660, /* STATS_TINTLESS_BG */
	0xb860, /* STATS_AWB_BG */
	0xba60, /* STATS_BFW */
	0xbc60, /* STATS_BAF */
	0xbe60, /* STATS_RS */
	0xc060, /* STATS_IHIST */
};

#define SP11_FRONT_MINIMAL_MODULES 64U
#define SP11_FRONT_MINIMAL_BYTES (SP11_FRONT_MINIMAL_MODULES * 12U + \
	24U + SP11_CST_COMMAND_BYTES + SP11_GEOMETRY_COMMAND_BYTES + \
	SP11_FRONT_ROUND_COMMAND_BYTES + 6U * 12U)

static inline int sp11_front_minimal_validate(const struct sp11_front_minimal *s)
{
	if (!s)
		return -EINVAL;
	/* Domain and Bayer routing are deliberately not guessed for other modes. */
	if (s->input_bits != 10 || s->bayer != SP11_FRONT_RGGB)
		return -EOPNOTSUPP;
	return sp11_geometry_validate(&s->geometry);
}

/* Mathematical full-range BT.601 for a hypothesised identity 10-bit path.
 * Hardware domain, channel order, bypass behavior and demosaic interpretation
 * are explicit qualification gates. This does not grant hardware admission.
 */
static inline int sp11_front_minimal_commands(u8 *out, size_t capacity,
					    const struct sp11_front_minimal *s)
{
	u8 tmp[SP11_FRONT_MINIMAL_BYTES];
	const struct sp11_cst_config cst = {
		.matrix = {601, 117, 306, -339, 512, -173, -429, -83, 512},
		.offset = {0, 512, 512},
		.maximum = {1023, 1023, 1023},
	};
	/* GPL RFC vfe_setup_demosaic() parameters, not a Windows profile read. */
	const u32 demosaic[4] = {0x80, 0, 0x40, 0x66};
	const u32 enable_regs[6] = {0x5660, 0x6160, 0x9860, 0x9a60, 0x9c60, 0x9e60};
	const u32 enable_values[6] = {1, 1, 1, 1, 0x0e01, 0x3e01};
	u32 disabled = 0;
	size_t pos = 0;
	unsigned int i;
	int ret;

	if (!out || !s)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
	ret = sp11_front_minimal_validate(s);
	if (ret)
		return ret;
	for (i = 0; i < SP11_FRONT_MINIMAL_MODULES; i++) {
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
					sp11_front_minimal_module_regs[i], &disabled, 1);
		if (ret)
			return ret;
		pos += 12;
	}
	ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos, 0x5668, demosaic, 4);
	if (ret)
		return ret;
	pos += 24;
	ret = sp11_cst_commands(tmp + pos, sizeof(tmp) - pos, &cst);
	if (ret)
		return ret;
	pos += SP11_CST_COMMAND_BYTES;
	ret = sp11_geometry_commands_state(tmp + pos, sizeof(tmp) - pos,
					  &s->geometry, false);
	if (ret)
		return ret;
	pos += SP11_GEOMETRY_COMMAND_BYTES;
	ret = sp11_front_round_commands_state(tmp + pos, sizeof(tmp) - pos, 8, false);
	if (ret)
		return ret;
	pos += SP11_FRONT_ROUND_COMMAND_BYTES;
	/* Only enable the minimal image graph after all its configuration words. */
	for (i = 0; i < 6; i++) {
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
					enable_regs[i], &enable_values[i], 1);
		if (ret)
			return ret;
		pos += 12;
	}
	if (pos != sizeof(tmp))
		return -EINVAL;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
