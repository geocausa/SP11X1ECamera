/* SPDX-License-Identifier: MIT */
/*
 * E007e compile-only BFStats25 DMI encoding boundary.
 *
 * Inputs are adjusted/sorted semantic AF BF state. This provider implements
 * only the exact Titan680 selector-1 ROI record encoding and selector-2 gamma
 * LUT encoding. AF policy, ROI validation/adjustment/sorting and gamma
 * rescaling remain upstream responsibilities.
 */

#define E007E_BF_ROI_COUNT 25
#define E007E_BF_ROI_BYTES 300
#define E007E_BF_GAMMA_COUNT 32
#define E007E_BF_GAMMA_BYTES 128

struct e007e_bf_roi {
	u16 left;
	u16 top;
	u16 width;
	u16 height;
	u8 rid;
	u8 oid;
	bool merge;
	bool type;
};

struct e007e_bf_dmi_state {
	struct e007e_bf_roi roi[E007E_BF_ROI_COUNT];
	u8 roi_count;
	u16 gamma[E007E_BF_GAMMA_COUNT];
	bool gamma_valid;
};

static int e007e_bf_roi_validate(const struct e007e_bf_roi *r)
{
	if (!r)
		return -EINVAL;
	if (r->left > 0x1fff || r->top > 0x3fff ||
	    r->width > 0x0fff || r->height > 0x1fff)
		return -ERANGE;
	return 0;
}

static int
e007e_bf_pack_roi(const struct e007e_bf_roi *r, bool eob, u8 *dst)
{
	u32 word0, word1, word2;
	int ret;

	if (!dst)
		return -EINVAL;
	ret = e007e_bf_roi_validate(r);
	if (ret)
		return ret;

	word0 = (u32)r->height |
		((u32)r->width << 14) |
		((u32)(r->top & 0x1f) << 27);
	word1 = ((u32)r->top >> 5) |
		((u32)r->left << 9) |
		((u32)r->rid << 23) |
		((u32)(r->oid & 0x1) << 31);
	word2 = ((u32)r->oid >> 1) |
		((u32)r->merge << 7) |
		((u32)eob << 8) |
		((u32)r->type << 9);

	put_unaligned_le32(word0, dst + 0);
	put_unaligned_le32(word1, dst + 4);
	put_unaligned_le32(word2, dst + 8);
	return 0;
}

static s32 e007e_bf_clamp_delta(s32 delta)
{
	if (delta < -8192)
		return -8192;
	if (delta > 8191)
		return 8191;
	return delta;
}

static int
e007e_bf_pack_gamma(const struct e007e_bf_dmi_state *s, u8 *dst)
{
	unsigned int i;

	if (!s || !dst)
		return -EINVAL;
	if (!s->gamma_valid)
		return -EOPNOTSUPP;

	for (i = 0; i < E007E_BF_GAMMA_COUNT; i++) {
		s32 next = i + 1 < E007E_BF_GAMMA_COUNT ?
			s->gamma[i + 1] : 0x4000;
		s32 delta;
		u32 word;

		if (s->gamma[i] > 0x3fff ||
		    (i + 1 < E007E_BF_GAMMA_COUNT &&
		     s->gamma[i + 1] > 0x3fff))
			return -ERANGE;

		delta = e007e_bf_clamp_delta(next - (s32)s->gamma[i]);
		word = (u32)s->gamma[i] + ((u32)delta << 14);
		put_unaligned_le32(word, dst + i * sizeof(word));
	}

	return 0;
}

static int
e007e_bfstats25_dmi(void *ctx, u8 selector, u8 *dst, size_t bytes)
{
	const struct e007e_bf_dmi_state *s = ctx;
	unsigned int i;
	int ret;

	if (!s || !dst)
		return -EINVAL;

	switch (selector) {
	case 1:
		if (bytes != E007E_BF_ROI_BYTES ||
		    s->roi_count != E007E_BF_ROI_COUNT)
			return -EINVAL;
		for (i = 0; i < s->roi_count; i++) {
			ret = e007e_bf_pack_roi(&s->roi[i],
					       i + 1 == s->roi_count,
					       dst + i * 12);
			if (ret)
				return ret;
		}
		return 0;
	case 2:
		if (bytes != E007E_BF_GAMMA_BYTES)
			return -EINVAL;
		return e007e_bf_pack_gamma(s, dst);
	default:
		return -ENOENT;
	}
}

static const struct {
	int (*produce)(void *ctx, u8 selector, u8 *dst, size_t bytes);
} e007e_bfstats25_dmi_recipe __used = {
	.produce = e007e_bfstats25_dmi,
};
