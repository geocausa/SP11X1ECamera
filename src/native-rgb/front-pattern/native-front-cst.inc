/* SPDX-License-Identifier: GPL-2.0-only */
/* Optional measured front colour matrices.
 *
 * native_front_ccm_q7 carries the nine Q7 coefficients of the linear-domain
 * colour-correction module (rows/outputs and columns/inputs G,B,R), applied
 * before the gamma LUT. When supplied, only its six coefficient words in each
 * colour-correction command (two startup packets and the steady packet) are
 * replaced (offsets/shift untouched).
 *
 * native_front_cst_q10 carries nine Q10 coefficients (rows Y,U,V; columns
 * G,B,R in the CST12 register order) produced by independent pattern
 * calibration in userspace. When supplied, only the six CST12 matrix words of
 * each startup CST command in the materialized capsule are replaced; enable,
 * offsets, clamps and every other command stay as loaded. All occurrences are
 * located and validated before the first byte is written.
 */
static short native_front_cst_q10[9];
static int native_front_cst_q10_count;
module_param_array(native_front_cst_q10, short, &native_front_cst_q10_count, 0400);
MODULE_PARM_DESC(native_front_cst_q10,
	"Front CST12 matrix override, 9 x Q10 (rows Y,U,V; cols G,B,R); empty keeps the profile");

#define NATIVE_FRONT_CST_HEADER ((3U << 24) | 18U)
#define NATIVE_FRONT_CST_FIRST_REG 0x6168U
#define NATIVE_FRONT_CST_COMMANDS 2U
#define NATIVE_FRONT_CCM_HEADER ((3U << 24) | 10U)
#define NATIVE_FRONT_CCM_FIRST_REG 0x5868U
#define NATIVE_FRONT_CCM_COMMANDS 3U /* two startup packets + the steady packet */

static short native_front_ccm_q7[9];
static int native_front_ccm_q7_count;
module_param_array(native_front_ccm_q7, short, &native_front_ccm_q7_count, 0400);
MODULE_PARM_DESC(native_front_ccm_q7,
	"Front colour-correction matrix override, 9 x Q7 (rows/cols G,B,R); empty keeps the profile");

static u32 native_front_cst_s13(short v)
{
	return (u32)(u16)v & 0x1fffU;
}

static int native_front_cst_apply(struct camss_video *video, u8 *capsule, size_t bytes)
{
	size_t at[NATIVE_FRONT_CST_COMMANDS];
	unsigned int found = 0, i;
	size_t p;

	if (!native_front_cst_q10_count)
		return 0;
	if (native_front_cst_q10_count != 9 || !capsule)
		return -EINVAL;
	for (i = 0; i < 9; i++)
		if (native_front_cst_q10[i] < -4096 || native_front_cst_q10[i] > 4095)
			return -ERANGE;
	for (p = 0; p + 8 + 18 * 4 <= bytes; p += 4) {
		if (get_unaligned_le32(capsule + p) != NATIVE_FRONT_CST_HEADER ||
		    get_unaligned_le32(capsule + p + 4) != NATIVE_FRONT_CST_FIRST_REG)
			continue;
		if (found == NATIVE_FRONT_CST_COMMANDS)
			return -EEXIST;
		at[found++] = p + 8;
	}
	if (found != NATIVE_FRONT_CST_COMMANDS)
		return -ENOENT;
	for (i = 0; i < found; i++) {
		u8 *w = capsule + at[i];
		const short *m = native_front_cst_q10;

		/* Word index n is register 0x6168 + 4 * (n - 1). */
		put_unaligned_le32(native_front_cst_s13(m[0]) | native_front_cst_s13(m[1]) << 16, w + 0 * 4);
		put_unaligned_le32(native_front_cst_s13(m[2]), w + 1 * 4);
		put_unaligned_le32(native_front_cst_s13(m[3]) | native_front_cst_s13(m[4]) << 16, w + 6 * 4);
		put_unaligned_le32(native_front_cst_s13(m[5]), w + 7 * 4);
		put_unaligned_le32(native_front_cst_s13(m[6]) | native_front_cst_s13(m[7]) << 16, w + 12 * 4);
		put_unaligned_le32(native_front_cst_s13(m[8]), w + 13 * 4);
	}
	dev_info(video->camss->dev, "NATIVE_FRONT_CST_OVERRIDE commands=%u\n", found);
	return 0;
}

static int native_front_ccm_apply(struct camss_video *video, u8 *capsule, size_t bytes)
{
	size_t at[NATIVE_FRONT_CCM_COMMANDS];
	unsigned int found = 0, i;
	size_t p;

	if (!native_front_ccm_q7_count)
		return 0;
	if (native_front_ccm_q7_count != 9 || !capsule)
		return -EINVAL;
	for (i = 0; i < 9; i++)
		if (native_front_ccm_q7[i] < -2048 || native_front_ccm_q7[i] > 2047)
			return -ERANGE;
	for (p = 0; p + 8 + 10 * 4 <= bytes; p += 4) {
		if (get_unaligned_le32(capsule + p) != NATIVE_FRONT_CCM_HEADER ||
		    get_unaligned_le32(capsule + p + 4) != NATIVE_FRONT_CCM_FIRST_REG)
			continue;
		if (found == NATIVE_FRONT_CCM_COMMANDS)
			return -EEXIST;
		at[found++] = p + 8;
	}
	if (found != NATIVE_FRONT_CCM_COMMANDS)
		return -ENOENT;
	for (i = 0; i < found; i++) {
		u8 *w = capsule + at[i];
		const short *m = native_front_ccm_q7;
		unsigned int r;

		/* The module's coefficient group n holds the weights of input n for
		 * outputs 0/1 (word 2n) and output 2 (word 2n+1), i.e. the transpose
		 * of the row-major output matrix supplied in the parameter (verified
		 * against measured greys/colours on hardware). */
		for (r = 0; r < 3; r++) {
			put_unaligned_le32(native_front_cst_s13(m[r]) |
					   native_front_cst_s13(m[3 + r]) << 16, w + 8 * r);
			put_unaligned_le32(native_front_cst_s13(m[6 + r]), w + 8 * r + 4);
		}
	}
	dev_info(video->camss->dev, "NATIVE_FRONT_CCM_OVERRIDE commands=%u\n", found);
	return 0;
}
