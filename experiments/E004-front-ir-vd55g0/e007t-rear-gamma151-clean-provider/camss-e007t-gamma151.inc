/* SPDX-License-Identifier: MIT */
/*
 * E007t compile-only rear Gamma151 clean provider.
 *
 * Semantic authority: 257 integral 12-bit samples derived from the selected
 * OV13858 Gamma1.5 tuning region. These are tuning semantics, not captured
 * Windows DMI words.
 */
#define E007T_GAMMA_DMI_REG 0x5f08
#define E007T_GAMMA_BYTES   1024
#define E007T_GAMMA_SAMPLES 257

static const u16 e007t_gamma_curve[E007T_GAMMA_SAMPLES] = {
	0, 64, 128, 192, 256, 300, 344, 388, 432, 468, 504, 541,
	577, 609, 641, 673, 705, 734, 763, 792, 821, 848, 875, 902,
	929, 955, 981, 1007, 1033, 1057, 1081, 1105, 1129, 1151, 1173, 1195,
	1217, 1239, 1261, 1283, 1305, 1326, 1347, 1368, 1389, 1409, 1429, 1449,
	1469, 1488, 1507, 1526, 1546, 1565, 1584, 1603, 1622, 1640, 1658, 1676,
	1694, 1712, 1730, 1748, 1766, 1783, 1800, 1817, 1834, 1851, 1868, 1885,
	1902, 1918, 1934, 1950, 1966, 1982, 1998, 2014, 2030, 2046, 2062, 2078,
	2094, 2109, 2124, 2139, 2154, 2169, 2184, 2199, 2214, 2229, 2244, 2259,
	2274, 2289, 2304, 2319, 2334, 2348, 2362, 2376, 2390, 2404, 2418, 2432,
	2446, 2460, 2474, 2488, 2502, 2515, 2528, 2541, 2554, 2568, 2581, 2594,
	2607, 2621, 2635, 2649, 2663, 2676, 2689, 2702, 2715, 2727, 2739, 2751,
	2763, 2776, 2789, 2802, 2815, 2827, 2839, 2851, 2863, 2876, 2889, 2902,
	2915, 2927, 2939, 2951, 2963, 2975, 2987, 2999, 3011, 3023, 3035, 3047,
	3059, 3070, 3081, 3092, 3103, 3115, 3127, 3139, 3151, 3162, 3173, 3184,
	3195, 3207, 3219, 3231, 3243, 3254, 3265, 3276, 3287, 3298, 3309, 3320,
	3331, 3342, 3353, 3364, 3375, 3386, 3397, 3408, 3419, 3430, 3441, 3452,
	3463, 3473, 3483, 3493, 3503, 3514, 3525, 3536, 3547, 3557, 3567, 3577,
	3588, 3599, 3610, 3621, 3632, 3642, 3652, 3662, 3672, 3682, 3692, 3702,
	3712, 3722, 3732, 3742, 3752, 3762, 3772, 3782, 3792, 3802, 3812, 3822,
	3832, 3842, 3852, 3862, 3872, 3882, 3892, 3902, 3912, 3922, 3932, 3942,
	3952, 3961, 3970, 3979, 3988, 3998, 4008, 4018, 4028, 4037, 4046, 4055,
	4064, 4072, 4080, 4088, 4095,
};

static int
e007t_gamma151_pack(u8 *dst, size_t bytes)
{
	unsigned int i;

	if (!dst || bytes != E007T_GAMMA_BYTES)
		return -EINVAL;

	for (i = 0; i < 256; i++) {
		int x = e007t_gamma_curve[i];
		int y = e007t_gamma_curve[i + 1];
		int d = y - x;
		u32 word;

		if (d < -2048)
			d = -2048;
		else if (d > 2047)
			d = 2047;

		word = (u32)x | (((u32)d & 0xfff) << 12);
		memcpy(dst + i * sizeof(word), &word, sizeof(word));
	}

	return 0;
}

struct e007t_rear_remaining_ops {
	int (*stable_non_gamma)(void *ctx, u16 dmi_reg, u8 selector,
				 u8 *dst, size_t bytes);
};

struct e007t_rear_dmi_state {
	struct e007s_rear_dmi_state dmi;
	const struct e007t_rear_remaining_ops *remaining;
	void *stable_ctx;
};

static int
e007t_rear_stable_nonzero(void *ctx, u16 dmi_reg, u8 selector,
			 u8 *dst, size_t bytes)
{
	struct e007t_rear_dmi_state *s = ctx;

	if (!s || !dst)
		return -EINVAL;

	if (dmi_reg == E007T_GAMMA_DMI_REG &&
	    selector >= 1 && selector <= 3)
		return e007t_gamma151_pack(dst, bytes);

	if (!s->remaining || !s->remaining->stable_non_gamma)
		return -EOPNOTSUPP;

	return s->remaining->stable_non_gamma(s->stable_ctx, dmi_reg,
					      selector, dst, bytes);
}

static const struct e007s_rear_remaining_ops
e007t_rear_e007s_remaining_ops = {
	.stable_nonzero = e007t_rear_stable_nonzero,
};

static int
e007t_rear_bind(struct e007t_rear_dmi_state *s)
{
	if (!s)
		return -EINVAL;

	s->dmi.remaining = &e007t_rear_e007s_remaining_ops;
	s->dmi.stable_ctx = s;
	return 0;
}

static int
e007t_rear_validate_request(struct e007t_rear_dmi_state *s,
			    u64 expected_request_id)
{
	int ret;

	if (!s)
		return -EINVAL;

	/* BPC/ABF and DSX remain mandatory first-frame dependencies. */
	if (!s->remaining || !s->remaining->stable_non_gamma)
		return -EOPNOTSUPP;

	ret = e007t_rear_bind(s);
	if (ret)
		return ret;

	return e007s_rear_validate_request(&s->dmi, expected_request_id);
}

static int
e007t_rear_prepare_dynamic(struct e007t_rear_dmi_state *s,
			   u64 expected_request_id,
			   struct e006g_rear_dynamic_payloads *out)
{
	int ret = e007t_rear_validate_request(s, expected_request_id);

	if (ret)
		return ret;

	return e007s_rear_prepare_dynamic(&s->dmi, expected_request_id, out);
}

static int
e007t_rear_fill_slot(struct e007t_rear_dmi_state *s,
		     u64 expected_request_id,
		     const struct e006g_rear_dynamic_payloads *dyn,
		     const struct e006g_rear_dmi_slot *slot,
		     struct e006g_rear_slot_buffer *out)
{
	int ret = e007t_rear_validate_request(s, expected_request_id);

	if (ret)
		return ret;

	return e007s_rear_fill_slot(&s->dmi, expected_request_id,
				    dyn, slot, out);
}

struct e007t_rear_gamma_ops {
	int (*validate)(struct e007t_rear_dmi_state *s, u64 request_id);
	int (*prepare_dynamic)(struct e007t_rear_dmi_state *s, u64 request_id,
			       struct e006g_rear_dynamic_payloads *out);
	int (*fill_slot)(struct e007t_rear_dmi_state *s, u64 request_id,
			 const struct e006g_rear_dynamic_payloads *dyn,
			 const struct e006g_rear_dmi_slot *slot,
			 struct e006g_rear_slot_buffer *out);
};

static const struct e007t_rear_gamma_ops
e007t_rear_gamma_recipe __used = {
	.validate = e007t_rear_validate_request,
	.prepare_dynamic = e007t_rear_prepare_dynamic,
	.fill_slot = e007t_rear_fill_slot,
};
