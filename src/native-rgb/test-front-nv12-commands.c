/* SPDX-License-Identifier: GPL-2.0-only */
#include "native-front-nv12-commands.h"
#include <assert.h>
#include <stdio.h>

static size_t fixture(u8 *p)
{
	size_t pos = 0;

	for (unsigned c = 0; c < 2; c++) {
		u32 base = c ? 0x9e60 : 0x9c60;
		native_nv12_put32(p + pos, (3U << 24) | 14);
		native_nv12_put32(p + pos + 4, base);
		for (unsigned i = 0; i < 14; i++) {
			unsigned chroma = 0;
			int index = native_nv12_round_index(base + i * 4, &chroma);
			native_nv12_put32(p + pos + 8 + i * 4,
				index < 0 ? 0xabcd0000U + i :
				native_nv12_round_word(chroma, index, 10));
		}
		pos += 8 + 14 * 4;
	}
	return pos;
}
static void rejected_unchanged(u8 *p, size_t n, int full)
{
	u8 before[256];
	assert(n <= sizeof(before));
	memcpy(before, p, n);
	assert(native_nv12_commands_transform(p, n, full) < 0);
	assert(!memcmp(before, p, n));
}
int main(void)
{
	u8 input[256], valid[256], before[256];
	size_t n = fixture(valid);
	unsigned checks = 0;

	assert(native_nv12_commands_validate(valid, n, 1) == 0); checks++;
	memcpy(input, valid, n);
	assert(native_nv12_commands_transform(input, n, 1) == 0); checks++;
	for (size_t pos = 0; pos < n; pos += 64) {
		u32 base = native_nv12_le32(input + pos + 4);
		assert(!memcmp(input + pos, valid + pos, 8)); checks++;
		for (unsigned i = 0; i < 14; i++) {
			unsigned c = 0;
			int index = native_nv12_round_index(base + i * 4, &c);
			u32 got = native_nv12_le32(input + pos + 8 + i * 4);
			if (index < 0)
				assert(got == native_nv12_le32(valid + pos + 8 + i * 4));
			else
				assert(got == native_nv12_round_word(c, index, 8));
			checks++;
		}
	}
	/* Every truncated two-path register stream must be rejected atomically. */
	for (size_t len = 0; len < n; len++) {
		memcpy(input, valid, n);
		rejected_unchanged(input, len, 1); checks++;
	}
	/* Late corruption, duplicate range, reserved bits, unknown commands. */
	memcpy(input, valid, n);
	native_nv12_put32(input + n - 4, 1);
	rejected_unchanged(input, n, 1); checks++;
	memcpy(input, valid, n);
	native_nv12_put32(input + 64 + 4, 0x9c60);
	rejected_unchanged(input, n, 1); checks++;
	memcpy(input, valid, n);
	input[2] = 1;
	rejected_unchanged(input, n, 1); checks++;
	memcpy(input, valid, n);
	input[3] = 4;
	rejected_unchanged(input, n, 1); checks++;
	memcpy(input, valid, n);
	native_nv12_put32(input, 3U << 24);
	rejected_unchanged(input, n, 1); checks++;
	memcpy(input, valid, n);
	native_nv12_put32(input + 4, 0xfffffc);
	rejected_unchanged(input, n, 1); checks++;
	/* A complete FULL stream is forbidden in steady packets. */
	memcpy(input, valid, n);
	rejected_unchanged(input, n, 0); checks++;
	/* Existing geometry/DMI and unrelated registers are preserved exactly. */
	native_nv12_put32(input, (3U << 24) | 1);
	native_nv12_put32(input + 4, 0x5000);
	native_nv12_put32(input + 8, 0x12345678);
	native_nv12_put32(input + 12, (1U << 24) | (0x20U << 16) | 0x1ff);
	native_nv12_put32(input + 16, 0x12340000);
	native_nv12_put32(input + 20, 0x01003d08);
	memcpy(before, input, 24);
	assert(native_nv12_commands_transform(input, 24, 0) == 0);
	assert(!memcmp(input, before, 24)); checks++;
	/* Refuse any BUS or WM write, even when it follows valid FULL fields. */
	memcpy(input, valid, n);
	native_nv12_put32(input + n, (3U << 24) | 1);
	native_nv12_put32(input + n + 4, 0xe48);
	native_nv12_put32(input + n + 8, 0);
	rejected_unchanged(input, n + 12, 1); checks++;
	assert(native_nv12_commands_validate(NULL, n, 1) < 0); checks++;
	printf("PASS_NATIVE_NV12_COMMANDS %u checks; synthetic inputs, no hardware\n", checks);
	return 0;
}
