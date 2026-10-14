/* SPDX-License-Identifier: GPL-2.0-only */
/* Typed front coefficient/rounding command fragments, not a startup profile.
 * Functional field layouts come from the project's independently tested front
 * coefficient and RoundClamp12 adapters; see FRONT-FIELDS-PROVENANCE-20261011.md.
 * No private schema, tuning file, enable/shift default, DMI bank or DMA address
 * is imported. Missing scaler/crop/statistics and module setup remains mandatory.
 */
#ifndef SP11_OPEN_FRONT_FIELDS_H
#define SP11_OPEN_FRONT_FIELDS_H
#include "sp11-cdm.h"

#define SP11_FRONT_CST_COMMAND_BYTES 48U
#define SP11_FRONT_CCM_COMMAND_BYTES 32U
#define SP11_FRONT_ROUND_COMMAND_BYTES 120U

static inline u32 sp11_front_pair(s16 a, s16 b)
{
	return ((u32)a & 0x1fffU) | (((u32)b & 0x1fffU) << 16);
}

/* Matrix rows are Y,Cb,Cr; columns G,B,R; Q10. Only coefficients are owned.
 * Offsets, shifts, clamps and module enables are NOT synthesized by this slice.
 */
static inline int sp11_front_cst_commands(u8 *out, size_t capacity,
					const s16 matrix[9])
{
	u8 tmp[SP11_FRONT_CST_COMMAND_BYTES];
	u32 values[2];
	unsigned int i;
	int ret;

	if (!out || !matrix)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), matrix, 9 * sizeof(*matrix)))
		return -EINVAL;
	for (i = 0; i < 9; i++)
		if (matrix[i] < -4096 || matrix[i] > 4095)
			return -ERANGE;
	for (i = 0; i < 3; i++) {
		values[0] = sp11_front_pair(matrix[3 * i], matrix[3 * i + 1]);
		values[1] = sp11_front_pair(matrix[3 * i + 2], 0);
		ret = sp11_cdm_reg_cont(tmp + 16 * i, 16,
					0x6168U + 24 * i, values, 2);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* Matrix rows/columns G,B,R; Q7. Hardware coefficient groups are transposed.
 * The qualified CCM policy uses the signed 12-bit numerical range, packed in
 * the observed 13-bit fields. This is narrower than the CST numerical range.
 */
static inline int sp11_front_ccm_commands(u8 *out, size_t capacity,
					const s16 matrix[9])
{
	u8 tmp[SP11_FRONT_CCM_COMMAND_BYTES];
	u32 values[6];
	unsigned int i;
	int ret;

	if (!out || !matrix)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), matrix, 9 * sizeof(*matrix)))
		return -EINVAL;
	for (i = 0; i < 9; i++)
		if (matrix[i] < -2048 || matrix[i] > 2047)
			return -ERANGE;
	for (i = 0; i < 3; i++) {
		values[2 * i] = sp11_front_pair(matrix[i], matrix[3 + i]);
		values[2 * i + 1] = sp11_front_pair(matrix[6 + i], 0);
	}
	ret = sp11_cdm_reg_cont(tmp, sizeof(tmp), 0x5868U, values, 6);
	if (ret)
		return ret;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}

/* FULL luma and interleaved chroma rounding/clamping, 8- or 10-bit output.
 * Crop registers and each block's +4 word are excluded. This does not create
 * a scaler, configure the bus write masters or assert a complete NV12 path.
 */
static inline int sp11_front_round_commands_state(u8 *out, size_t capacity,
						unsigned int bits, bool enabled)
{
	u8 tmp[SP11_FRONT_ROUND_COMMAND_BYTES];
	u32 values[10], enable, maximum, round;
	unsigned int chroma;
	int ret;

	if (!out || (bits != 8 && bits != 10))
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	maximum = (1U << bits) - 1;
	round = 10 - bits;
	for (chroma = 0; chroma < 2; chroma++) {
		u32 base = chroma ? 0x9e60U : 0x9c60U;
		u8 *p = tmp + 60 * chroma;

		enable = chroma ? 0x3e01U : 0x0e01U;
		if (!enabled)
			enable &= ~1U;
		memset(values, 0, sizeof(values));
		values[1] = (chroma ? 7U : 6U) | (round << 3);
		values[6] = maximum;
		if (chroma) {
			values[3] = 7U | (round << 3);
			values[7] = maximum;
		}
		ret = sp11_cdm_reg_cont(p, 12, base, &enable, 1);
		if (ret)
			return ret;
		ret = sp11_cdm_reg_cont(p + 12, 48, base + 0x10,
					values, 10);
		if (ret)
			return ret;
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
static inline int sp11_front_round_commands(u8 *out, size_t capacity,
					  unsigned int bits)
{
	return sp11_front_round_commands_state(out, capacity, bits, true);
}
#endif
