/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "sp11-front-fields.h"
#include "native-front-nv12-commands.h"

static u32 read32(const u8 *p)
{
	return p[0] | (u32)p[1] << 8 | (u32)p[2] << 16 | (u32)p[3] << 24;
}

static int signed13(u32 v)
{
	v &= 0x1fff;
	return v & 0x1000 ? (int)v - 0x2000 : (int)v;
}

static void unchanged(const u8 *out, size_t bytes)
{
	for (size_t i = 0; i < bytes; i++)
		assert(out[i] == 0xa5);
}

static void test_reg_commands(void)
{
	u8 out[32];
	u32 input[] = {0, 0x11223344, 0xffffffff};

	memset(out, 0xa5, sizeof(out));
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0x6168, input, 3) == 0);
	assert(read32(out) == 0x03000003 && read32(out + 4) == 0x6168);
	assert(read32(out + 8) == 0 && read32(out + 12) == 0x11223344);
	assert(read32(out + 16) == 0xffffffff);
	unchanged(out + 20, sizeof(out) - 20);
	memset(out, 0xa5, sizeof(out));
	assert(sp11_cdm_reg_cont(out, 19, 0x6168, input, 3) == -ENOSPC);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 1, input, 3) == -ERANGE);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0x1000000, input, 3) == -ERANGE);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0xfffffc, input, 2) == -ERANGE);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0, input, 0) == -EINVAL);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0, input, 65536) == -ERANGE);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0, input, (size_t)-1) == -ERANGE);
	assert(sp11_cdm_reg_cont(out, sizeof(out), 0, NULL, 1) == -EINVAL);
	assert(sp11_cdm_reg_cont(NULL, sizeof(out), 0, input, 1) == -EINVAL);
	unchanged(out, sizeof(out));
	union {u32 values[8]; u8 bytes[32];} overlap;
	memset(&overlap, 0xa5, sizeof(overlap));
	assert(sp11_cdm_reg_cont(overlap.bytes, 32, 0, overlap.values, 3) == -EINVAL);
	assert(sp11_cdm_reg_cont(overlap.bytes + 4, 28, 0, overlap.values, 3) == -EINVAL);
	assert(sp11_cdm_reg_cont(overlap.bytes, 32, 0, overlap.values + 2, 3) == -EINVAL);
	unchanged(overlap.bytes, sizeof(overlap));
}

static void test_dmi(void)
{
	u8 out[16];

	memset(out, 0xa5, sizeof(out));
	assert(sp11_cdm_dmi(out, 16, 0x5f08, 3, 0x1000, 3072, 2048, 1024) == 0);
	assert(read32(out) == 0x010003ff);
	assert(read32(out + 4) == 0x1800 && read32(out + 8) == 0x03005f08);
	unchanged(out + 12, 4);
	assert(sp11_cdm_dmi(out, 16, 0, 255, 0xffff0000ULL, 65536, 0, 65536) == 0);
	assert(read32(out) == 0x0100ffff && read32(out + 4) == 0xffff0000U);
	assert(sp11_cdm_dmi(out, 16, 0, 0, 0xfffffffcULL, 4, 0, 4) == 0);
	memset(out, 0xa5, sizeof(out));
#define BAD(reg, sel, base, extent, off, n) \
	assert(sp11_cdm_dmi(out, 16, reg, sel, base, extent, off, n) < 0)
	BAD(1, 0, 0x1000, 1024, 0, 4);
	BAD(0x1000000, 0, 0x1000, 1024, 0, 4);
	BAD(0, 256, 0x1000, 1024, 0, 4);
	BAD(0, 0, 0x1001, 1024, 0, 4);
	BAD(0, 0, 0x100000000ULL, 1024, 0, 4);
	BAD(0, 0, 0xfffffffcULL, 8, 0, 4);
	BAD(0, 0, 0x1000, 0, 0, 4);
	BAD(0, 0, 0x1000, 1024, 0, 0);
	BAD(0, 0, 0x1000, 1024, 0, 3);
	BAD(0, 0, 0x1000, 1024, 1, 4);
	BAD(0, 0, 0x1000, 1024, 1028, 4);
	BAD(0, 0, 0x1000, 1024, 1024, 4);
	BAD(0, 0, 0x1000, 1024, 4, 1024);
	BAD(0, 0, 0x1000, 131072, 0, 65540);
	BAD(0, 0, 0x1000, (size_t)-1, 0, 4);
	BAD(0, 0, 0x1000, 1024, (size_t)-1, 4);
#undef BAD
	assert(sp11_cdm_dmi(out, 11, 0, 0, 0x1000, 1024, 0, 4) == -ENOSPC);
	assert(sp11_cdm_dmi(NULL, 16, 0, 0, 0x1000, 1024, 0, 4) == -EINVAL);
	unchanged(out, sizeof(out));
}

static void test_coefficients(void)
{
	u8 out[64];
	s16 matrix[9] = {601, 117, 306, -339, 512, -173, -429, -83, 512};

	memset(out, 0xa5, sizeof(out));
	assert(sp11_front_cst_commands(out, sizeof(out), matrix) == 0);
	for (unsigned int i = 0; i < 3; i++) {
		assert(read32(out + 16 * i) == 0x03000002);
		assert(read32(out + 16 * i + 4) == 0x6168 + 24 * i);
		assert(signed13(read32(out + 16 * i + 8)) == matrix[3 * i]);
		assert(signed13(read32(out + 16 * i + 8) >> 16) == matrix[3 * i + 1]);
		assert(signed13(read32(out + 16 * i + 12)) == matrix[3 * i + 2]);
		assert((read32(out + 16 * i + 8) & 0xe000e000U) == 0);
		assert((read32(out + 16 * i + 12) & 0xffffe000U) == 0);
	}
	unchanged(out + 48, 16);
	for (int value = -4096; value <= 4095; value++) {
		matrix[8] = value;
		assert(sp11_front_cst_commands(out, sizeof(out), matrix) == 0);
		assert(signed13(read32(out + 44)) == value);
	}
	for (int i = 0; i < 9; i++)
		matrix[i] = i + 1;
	assert(sp11_front_ccm_commands(out, sizeof(out), matrix) == 0);
	assert(read32(out) == 0x03000006 && read32(out + 4) == 0x5868);
	for (unsigned int i = 0; i < 3; i++) {
		assert(signed13(read32(out + 8 + 8 * i)) == matrix[i]);
		assert(signed13(read32(out + 8 + 8 * i) >> 16) == matrix[3 + i]);
		assert(signed13(read32(out + 12 + 8 * i)) == matrix[6 + i]);
	}
	for (int value = -2048; value <= 2047; value++) {
		matrix[8] = value;
		assert(sp11_front_ccm_commands(out, sizeof(out), matrix) == 0);
		assert(signed13(read32(out + 28)) == value);
	}
	memset(out, 0xa5, sizeof(out));
	matrix[8] = 4096;
	assert(sp11_front_cst_commands(out, sizeof(out), matrix) == -ERANGE);
	matrix[8] = -4097;
	assert(sp11_front_cst_commands(out, sizeof(out), matrix) == -ERANGE);
	matrix[8] = 2048;
	assert(sp11_front_ccm_commands(out, sizeof(out), matrix) == -ERANGE);
	matrix[8] = -2049;
	assert(sp11_front_ccm_commands(out, sizeof(out), matrix) == -ERANGE);
	matrix[8] = 0;
	assert(sp11_front_ccm_commands(out, 31, matrix) == -ENOSPC);
	assert(sp11_front_cst_commands(out, 47, matrix) == -ENOSPC);
	assert(sp11_front_cst_commands(out, 64, NULL) == -EINVAL);
	assert(sp11_front_ccm_commands(NULL, 64, matrix) == -EINVAL);
	unchanged(out, sizeof(out));
	union {s16 matrix[32]; u8 bytes[64];} overlap;
	memset(&overlap, 0xa5, sizeof(overlap));
	assert(sp11_front_cst_commands(overlap.bytes, 64, overlap.matrix) == -EINVAL);
	assert(sp11_front_ccm_commands(overlap.bytes, 64, overlap.matrix + 2) == -EINVAL);
	unchanged(overlap.bytes, sizeof(overlap));
}

static void test_round(void)
{
	u8 ten[128], eight[128], transformed[120];

	memset(ten, 0xa5, sizeof(ten));
	memset(eight, 0xa5, sizeof(eight));
	assert(sp11_front_round_commands(ten, 128, 10) == 0);
	assert(sp11_front_round_commands(eight, 128, 8) == 0);
	assert(native_nv12_commands_validate(ten, 120, 1) == 0);
	memcpy(transformed, ten, 120);
	assert(native_nv12_commands_transform(transformed, 120, 1) == 0);
	assert(memcmp(transformed, eight, 120) == 0);
	/* Independently inspect extents and require exactly the 22 owned fields. */
	for (unsigned int ch = 0; ch < 2; ch++) {
		u32 base = ch ? 0x9e60 : 0x9c60;
		u8 *p = eight + 60 * ch;

		assert(read32(p) == 0x03000001 && read32(p + 4) == base);
		assert(read32(p + 8) == (ch ? 0x3e01U : 0x0e01U));
		assert(read32(p + 12) == 0x0300000a);
		assert(read32(p + 16) == base + 0x10);
		assert(read32(p + 24) == (ch ? 23U : 22U));
		assert(read32(p + 44) == 255);
		assert(read32(p + 48) == (ch ? 255U : 0U));
	}
	unchanged(ten + 120, 8);
	unchanged(eight + 120, 8);
	memset(eight, 0xa5, sizeof(eight));
	assert(sp11_front_round_commands(eight, 119, 8) == -ENOSPC);
	assert(sp11_front_round_commands(eight, 128, 9) == -EINVAL);
	assert(sp11_front_round_commands(NULL, 128, 8) == -EINVAL);
	unchanged(eight, sizeof(eight));
}

int main(void)
{
	test_reg_commands();
	test_dmi();
	test_coefficients();
	test_round();
	puts("PASS: CDM bounds/atomic rejection; 8192 CST and 4096 CCM values; sparse fields; 22 round/clamp fields match the existing validated converter");
	return 0;
}
