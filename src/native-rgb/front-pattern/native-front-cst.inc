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

/* Experimental register masks for module studies (e.g. switching a module's
 * enable bit off): up to eight (register, AND mask, OR mask) triples applied
 * to every REG_CONT command word that writes the register in the command
 * area of the materialized capsule. Each listed register must be found at
 * least once; nothing is written otherwise.
 */
#define NATIVE_FRONT_REGMASK_MAX 32U
#define NATIVE_FRONT_REGMASK_AREA 0x7400U
static u32 native_front_reg_mask[3 * NATIVE_FRONT_REGMASK_MAX];
static int native_front_reg_mask_count;
module_param_array(native_front_reg_mask, uint, &native_front_reg_mask_count, 0400);
MODULE_PARM_DESC(native_front_reg_mask,
	"Front ISP register study: triples reg,and,or applied to all REG_CONT writes of reg");

static int native_front_regmask_walk(u8 *capsule, size_t bytes, bool write, unsigned int *hits)
{
	size_t limit = min_t(size_t, bytes, NATIVE_FRONT_REGMASK_AREA);
	size_t p;
	unsigned int t;

	for (p = 0x400; p + 8 <= limit; p += 4) {
		u32 h = get_unaligned_le32(capsule + p);
		u32 n = h & 0xffffU, start;

		if ((h >> 24) != 3U || (h & 0x00ff0000U) || !n || n >= 512U ||
		    p + 8 + 4 * (size_t)n > limit)
			continue;
		start = get_unaligned_le32(capsule + p + 4);
		if (start >= 0x10000U || (start & 3U))
			continue;
		for (t = 0; t < (unsigned int)native_front_reg_mask_count / 3; t++) {
			u32 reg = native_front_reg_mask[3 * t];
			u8 *w;

			if (reg < start || reg >= start + 4 * n)
				continue;
			w = capsule + p + 8 + (reg - start);
			hits[t]++;
			if (write)
				put_unaligned_le32((get_unaligned_le32(w) & native_front_reg_mask[3 * t + 1]) |
						   native_front_reg_mask[3 * t + 2], w);
		}
		p += 4 + 4 * (size_t)n; /* skip this command's body */
	}
	return 0;
}

static int native_front_regmask_apply(struct camss_video *video, u8 *capsule, size_t bytes)
{
	unsigned int hits[NATIVE_FRONT_REGMASK_MAX] = { 0 };
	unsigned int t, total = 0;

	if (!native_front_reg_mask_count)
		return 0;
	if (!capsule || native_front_reg_mask_count % 3)
		return -EINVAL;
	native_front_regmask_walk(capsule, bytes, false, hits);
	for (t = 0; t < (unsigned int)native_front_reg_mask_count / 3; t++) {
		if (!hits[t])
			return -ENOENT;
		total += hits[t];
	}
	memset(hits, 0, sizeof(hits));
	native_front_regmask_walk(capsule, bytes, true, hits);
	for (t = 0; t < (unsigned int)native_front_reg_mask_count / 3; t++)
		dev_info(video->camss->dev, "NATIVE_FRONT_REGMASK reg=0x%04x and=0x%08x or=0x%08x writes=%u\n",
			 native_front_reg_mask[3 * t], native_front_reg_mask[3 * t + 1],
			 native_front_reg_mask[3 * t + 2], hits[t]);
	return 0;
}

/* Own measured lens-shading mesh (open-profile work). When enabled, the
 * 17x13 LSC DMI payloads of this exact profile are replaced by
 * qcom/sp11/imx681-front-lsc-v1.bin: three 884-byte selector tables (red/green,
 * blue/green, zeros; Q10 gains, see open-profile/fit-lsc.py). The payload
 * offsets below belong to the one admitted profile digest; every target must
 * currently hold a non-zero table or nothing is written.
 */
#define NATIVE_FRONT_LSC_FW "qcom/sp11/imx681-front-lsc-v1.bin"
#define NATIVE_FRONT_LSC_TABLE 884U
static bool native_front_lsc;
module_param(native_front_lsc, bool, 0400);
MODULE_PARM_DESC(native_front_lsc, "Replace the profile LSC mesh with " NATIVE_FRONT_LSC_FW);
static const u32 native_front_lsc_sel1_at[] = { 0x3b40, 0x4740, 0x7600 };
static const u32 native_front_lsc_sel2_at[] = { 0x3ec0, 0x65c0, 0x7980 };

static bool native_front_lsc_nonzero(const u8 *p)
{
	unsigned int i;

	for (i = 0; i < NATIVE_FRONT_LSC_TABLE; i++)
		if (p[i])
			return true;
	return false;
}

static int native_front_lsc_apply(struct camss_video *video, u8 *capsule, size_t bytes)
{
	const struct firmware *fw;
	unsigned int i;
	int ret;

	if (!native_front_lsc)
		return 0;
	if (!capsule)
		return -EINVAL;
	for (i = 0; i < ARRAY_SIZE(native_front_lsc_sel1_at); i++)
		if (native_front_lsc_sel1_at[i] + NATIVE_FRONT_LSC_TABLE > bytes ||
		    native_front_lsc_sel2_at[i] + NATIVE_FRONT_LSC_TABLE > bytes ||
		    !native_front_lsc_nonzero(capsule + native_front_lsc_sel1_at[i]) ||
		    !native_front_lsc_nonzero(capsule + native_front_lsc_sel2_at[i]))
			return -ENOENT;
	ret = request_firmware_direct(&fw, NATIVE_FRONT_LSC_FW, video->camss->dev);
	if (ret)
		return ret;
	if (fw->size != 3 * NATIVE_FRONT_LSC_TABLE ||
	    native_front_lsc_nonzero(fw->data + 2 * NATIVE_FRONT_LSC_TABLE)) {
		release_firmware(fw);
		return -EINVAL;
	}
	for (i = 0; i < ARRAY_SIZE(native_front_lsc_sel1_at); i++) {
		memcpy(capsule + native_front_lsc_sel1_at[i], fw->data, NATIVE_FRONT_LSC_TABLE);
		memcpy(capsule + native_front_lsc_sel2_at[i], fw->data + NATIVE_FRONT_LSC_TABLE,
		       NATIVE_FRONT_LSC_TABLE);
	}
	release_firmware(fw);
	dev_info(video->camss->dev, "NATIVE_FRONT_LSC_OVERRIDE tables=%zu\n",
		 2 * ARRAY_SIZE(native_front_lsc_sel1_at));
	return 0;
}

/* Own BPC_ABF noise LUT (open-profile work). The 64-entry table holds an
 * inverse noise level per intensity bin: bits 0-8 value, bits 9 and up the
 * decrement to the next entry (see open-profile/gen-abf-lut.py, built from our
 * measured noise model). When enabled, both copies of the 256-byte payload in
 * the one admitted profile are replaced by qcom/sp11/imx681-front-abf-v1.bin;
 * the copies must currently be identical and non-zero or nothing is written.
 */
#define NATIVE_FRONT_ABF_FW "qcom/sp11/imx681-front-abf-v1.bin"
#define NATIVE_FRONT_ABF_TABLE 256U
static bool native_front_abf;
module_param(native_front_abf, bool, 0400);
MODULE_PARM_DESC(native_front_abf, "Replace the profile BPC_ABF noise LUT with " NATIVE_FRONT_ABF_FW);
static const u32 native_front_abf_at[] = { 0x64c0, 0x8280 };

static int native_front_abf_apply(struct camss_video *video, u8 *capsule, size_t bytes)
{
	const struct firmware *fw;
	unsigned int i, j;
	int ret;

	if (!native_front_abf)
		return 0;
	if (!capsule)
		return -EINVAL;
	for (i = 0; i < ARRAY_SIZE(native_front_abf_at); i++) {
		if (native_front_abf_at[i] + NATIVE_FRONT_ABF_TABLE > bytes ||
		    memcmp(capsule + native_front_abf_at[i], capsule + native_front_abf_at[0],
			   NATIVE_FRONT_ABF_TABLE))
			return -ENOENT;
	}
	for (j = 0; j < NATIVE_FRONT_ABF_TABLE && !capsule[native_front_abf_at[0] + j]; j++)
		;
	if (j == NATIVE_FRONT_ABF_TABLE)
		return -ENOENT;
	ret = request_firmware_direct(&fw, NATIVE_FRONT_ABF_FW, video->camss->dev);
	if (ret)
		return ret;
	if (fw->size != NATIVE_FRONT_ABF_TABLE) {
		release_firmware(fw);
		return -EINVAL;
	}
	for (i = 0; i < ARRAY_SIZE(native_front_abf_at); i++)
		memcpy(capsule + native_front_abf_at[i], fw->data, NATIVE_FRONT_ABF_TABLE);
	release_firmware(fw);
	dev_info(video->camss->dev, "NATIVE_FRONT_ABF_OVERRIDE tables=%zu\n",
		 ARRAY_SIZE(native_front_abf_at));
	return 0;
}
