/* SPDX-License-Identifier: MIT */
/*
 * E006p compile-only Titan680 Crop12 + RoundClamp12 packers.
 *
 * Inputs are semantic Linux-owned geometry/format state. No captured Windows
 * register values, command bytes, addresses or private payloads are embedded.
 */

struct e006p_crop_info {
	u16 first_pixel;
	u16 first_line;
	u16 last_pixel;
	u16 last_line;
};

struct e006p_output_path {
	struct e006p_crop_info luma;
	struct e006p_crop_info chroma;
	u8 bit_width;
	bool enabled;
};

struct e006p_rear_geometry {
	struct e006p_output_path full;
	struct e006p_output_path ds4;
	struct e006p_output_path ds16;
};

static int e006p_crop12_pack(const struct e006p_crop_info *crop,
			     bool pixel_word, u32 *value)
{
	if (!crop || !value)
		return -EINVAL;
	if (crop->first_pixel > 0x3fff || crop->last_pixel > 0x3fff ||
	    crop->first_line > 0x3fff || crop->last_line > 0x3fff ||
	    crop->first_pixel > crop->last_pixel ||
	    crop->first_line > crop->last_line)
		return -ERANGE;

	if (pixel_word)
		*value = ((u32)crop->first_pixel << 16) | crop->last_pixel;
	else
		*value = ((u32)crop->first_line << 16) | crop->last_line;
	return 0;
}

static int e006p_crop12_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006p_rear_geometry *g = ctx;
	const struct e006p_crop_info *crop;
	u16 base;
	bool pixel_word;

	if (!g || !value)
		return -EINVAL;

	switch (reg) {
	case 0x9c68: case 0x9c6c:
		crop = &g->full.luma; base = 0x9c68; break;
	case 0x9e68: case 0x9e6c:
		crop = &g->full.chroma; base = 0x9e68; break;
	case 0xa468: case 0xa46c:
		crop = &g->ds4.luma; base = 0xa468; break;
	case 0xa668: case 0xa66c:
		crop = &g->ds4.chroma; base = 0xa668; break;
	case 0xac68: case 0xac6c:
		crop = &g->ds16.luma; base = 0xac68; break;
	case 0xae68: case 0xae6c:
		crop = &g->ds16.chroma; base = 0xae68; break;
	default:
		return -ENOENT;
	}

	pixel_word = reg == base + 4;
	return e006p_crop12_pack(crop, pixel_word, value);
}

static int e006p_roundclamp_word(const struct e006p_output_path *path,
				 bool chroma, u8 index, u32 *value)
{
	u32 max_value;
	u32 round_bits;

	if (!path || !value)
		return -EINVAL;

	switch (path->bit_width) {
	case 8:
		max_value = 0xff;
		break;
	case 10:
		max_value = 0x3ff;
		break;
	case 14:
		max_value = 0x3fff;
		break;
	default:
		return -EINVAL;
	}

	round_bits = path->bit_width < 11 ? 10 - path->bit_width : 0;

	if (index == 0) {
		*value = (chroma ? 0x3c01 : 0x0c01) |
			 (path->enabled ? 0x200 : 0);
		return 0;
	}
	if (index > 10)
		return -EINVAL;

	if (!chroma) {
		switch (index) {
		case 2:
			*value = 0x6 | (round_bits << 3);
			return 0;
		case 7:
			*value = max_value;
			return 0;
		default:
			*value = 0;
			return 0;
		}
	}

	switch (index) {
	case 2:
	case 4:
		*value = 0x7 | (round_bits << 3);
		break;
	case 7:
	case 8:
		*value = max_value;
		break;
	default:
		*value = 0;
		break;
	}
	return 0;
}

static int e006p_roundclamp12_lookup(void *ctx, u16 reg, u32 *value)
{
	const struct e006p_rear_geometry *g = ctx;
	const struct e006p_output_path *path;
	u16 base;
	bool chroma;
	u8 index;

	if (!g || !value)
		return -EINVAL;

	if (reg >= 0x9c60 && reg <= 0x9c94) {
		path = &g->full; base = 0x9c60; chroma = false;
	} else if (reg >= 0x9e60 && reg <= 0x9e94) {
		path = &g->full; base = 0x9e60; chroma = true;
	} else if (reg >= 0xa460 && reg <= 0xa494) {
		path = &g->ds4; base = 0xa460; chroma = false;
	} else if (reg >= 0xa660 && reg <= 0xa694) {
		path = &g->ds4; base = 0xa660; chroma = true;
	} else if (reg >= 0xac60 && reg <= 0xac94) {
		path = &g->ds16; base = 0xac60; chroma = false;
	} else if (reg >= 0xae60 && reg <= 0xae94) {
		path = &g->ds16; base = 0xae60; chroma = true;
	} else {
		return -ENOENT;
	}

	if (reg == base)
		index = 0;
	else {
		if (reg < base + 0x10 || ((reg - (base + 0x10)) & 3))
			return -ENOENT;
		index = 1 + (reg - (base + 0x10)) / 4;
	}
	return e006p_roundclamp_word(path, chroma, index, value);
}

/* Compile/link type checks against E006m callback signature. */
static e006m_scalar_fn e006p_crop12_recipe __used = e006p_crop12_lookup;
static e006m_scalar_fn e006p_roundclamp12_recipe __used =
	e006p_roundclamp12_lookup;
