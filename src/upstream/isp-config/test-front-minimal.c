// SPDX-License-Identifier: GPL-2.0-only
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "sp11-front-minimal.h"

static u32 le32(const u8 *p)
{
	return (u32)p[0] | (u32)p[1] << 8 | (u32)p[2] << 16 | (u32)p[3] << 24;
}

static void check_program(const u8 *p)
{
	u32 final[SP11_FRONT_MINIMAL_MODULES] = {0};
	const u32 required[6] = {0x5660, 0x6160, 0x9860, 0x9a60, 0x9c60, 0x9e60};
	const u32 enabled[6] = {1, 1, 1, 1, 0xe01, 0x3e01};
	size_t pos = 0;
	unsigned int commands = 0;
	while (pos < SP11_FRONT_MINIMAL_BYTES) {
		u32 header = le32(p + pos), reg = le32(p + pos + 4);
		size_t words = header & 0xffffU;
		assert(header >> 24 == 3 && words && !(reg & 3));
		assert(pos + 8 + words * 4 <= SP11_FRONT_MINIMAL_BYTES);
		if (commands < SP11_FRONT_MINIMAL_MODULES) {
			assert(words == 1);
			assert(reg == sp11_front_minimal_module_regs[commands]);
			assert(le32(p + pos + 8) == 0);
		}
		for (unsigned int j = 0; j < words; j++) {
			u32 addr = reg + j * 4, value = le32(p + pos + 8 + j * 4);
			for (unsigned int k = 0; k < SP11_FRONT_MINIMAL_MODULES; k++) {
				if (addr != sp11_front_minimal_module_regs[k])
					continue;
				/* Enable never precedes the final commit phase. */
				if (pos < SP11_FRONT_MINIMAL_BYTES - 72)
					assert(!(value & 1U));
				final[k] = value;
			}
		}
		if (pos >= SP11_FRONT_MINIMAL_BYTES - 72) {
			u32 i = (u32)((pos - (SP11_FRONT_MINIMAL_BYTES - 72)) / 12);
			assert(words == 1 && i < 6 && reg == required[i]);
			assert(le32(p + pos + 8) == enabled[i]);
		}
		pos += 8 + words * 4;
		commands++;
	}
	assert(pos == SP11_FRONT_MINIMAL_BYTES && commands == 81);
	for (unsigned int i = 0; i < SP11_FRONT_MINIMAL_MODULES; i++) {
		u32 value = 0;
		for (unsigned int j = 0; j < 6; j++)
			if (sp11_front_minimal_module_regs[i] == required[j])
				value = enabled[j];
		assert(final[i] == value);
	}
}

static void dump_program(const u8 *p)
{
	size_t pos = 0;
	printf("{\"schema\":\"sp11-open-front-minimal-program-v1\","
	       "\"complete_startup_provider\":false,\"hardware_qualified\":false,"
	       "\"runtime_dependencies_removed\":false,\"private_input_read\":false,"
	       "\"bytes\":%u,\"dmi_transfers\":0,\"register_commands\":[", SP11_FRONT_MINIMAL_BYTES);
	while (pos < SP11_FRONT_MINIMAL_BYTES) {
		u32 count = le32(p + pos) & 0xffffU;
		printf("%s{\"register\":%u,\"values\":[", pos ? "," : "", le32(p + pos + 4));
		for (unsigned int i = 0; i < count; i++)
			printf("%s%u", i ? "," : "", le32(p + pos + 8 + i * 4));
		printf("]}");
		pos += 8 + count * 4;
	}
	puts("]}");
}

int main(int argc, char **argv)
{
	static const u32 widths[8] = {64, 128, 640, 1280, 1920, 3840, 4096, 16384};
	static const u32 heights[8] = {64, 128, 480, 720, 1080, 2160, 4096, 16384};
	struct sp11_front_minimal mode = {{3840, 2160, 2560, 1440}, 10, SP11_FRONT_RGGB};
	u8 out[SP11_FRONT_MINIMAL_BYTES + 32], expected[sizeof(out)];
	unsigned int successful = 0, rejected = 0;
	assert(SP11_FRONT_MINIMAL_BYTES == 1204);
	assert(sizeof(sp11_front_minimal_module_regs) / sizeof(u32) == SP11_FRONT_MINIMAL_MODULES);
	memset(out, 0xa5, sizeof(out));
	assert(!sp11_front_minimal_commands(out, sizeof(out), &mode));
	check_program(out);
	if (argc == 2 && !strcmp(argv[1], "--dump")) {
		dump_program(out);
		return 0;
	}
	assert(argc == 1);
	for (unsigned int x = 0; x < 8; x++) for (unsigned int y = 0; y < 8; y++)
		for (unsigned int divisor = 1; divisor <= 32; divisor *= 2) {
			mode.geometry = (struct sp11_geometry){widths[x], heights[y],
				(widths[x] / divisor) & ~1U, (heights[y] / divisor) & ~1U};
			memset(out, 0xa5, sizeof(out));
			assert(!sp11_front_minimal_commands(out, sizeof(out), &mode));
			check_program(out);
			for (size_t i = SP11_FRONT_MINIMAL_BYTES; i < sizeof(out); i++)
				assert(out[i] == 0xa5);
			successful++;
		}
	mode.geometry = (struct sp11_geometry){3840, 2160, 2560, 1440};
#define REJECT(call, result) do { \
	memset(out, 0xa5, sizeof(out)); memcpy(expected, out, sizeof(out)); \
	assert((call) == (result)); assert(!memcmp(expected, out, sizeof(out))); \
	rejected++; \
} while (0)
	for (size_t capacity = 0; capacity < SP11_FRONT_MINIMAL_BYTES; capacity++)
		REJECT(sp11_front_minimal_commands(out, capacity, &mode), -ENOSPC);
	REJECT(sp11_front_minimal_commands(out, sizeof(out), NULL), -EINVAL);
	REJECT(sp11_front_minimal_commands(NULL, sizeof(out), &mode), -EINVAL);
	for (unsigned int bits = 0; bits < 17; bits++) {
		if (bits == 10)
			continue;
		mode.input_bits = bits;
		REJECT(sp11_front_minimal_commands(out, sizeof(out), &mode), -EOPNOTSUPP);
	}
	mode.input_bits = 10;
	for (int bayer = -1; bayer < 6; bayer++) {
		if (bayer == SP11_FRONT_RGGB)
			continue;
		mode.bayer = (enum sp11_front_bayer)bayer;
		REJECT(sp11_front_minimal_commands(out, sizeof(out), &mode), -EOPNOTSUPP);
	}
	mode.bayer = SP11_FRONT_RGGB;
	static const struct sp11_geometry invalid[] = {
		{0, 2160, 2560, 1440}, {3840, 0, 2560, 1440}, {3840, 2160, 0, 1440},
		{3840, 2160, 2560, 0}, {3839, 2160, 2560, 1440}, {3840, 2159, 2560, 1440},
		{3840, 2160, 2559, 1440}, {3840, 2160, 2560, 1439},
		{3840, 2160, 3842, 1440}, {3840, 2160, 2560, 2162},
		{16386, 2160, 2560, 1440}, {3840, 16386, 2560, 1440}, {3840, 2160, 2, 2}
	};
	for (size_t i = 0; i < sizeof(invalid) / sizeof(invalid[0]); i++) {
		mode.geometry = invalid[i];
		int result = sp11_geometry_validate(&mode.geometry);
		assert(result < 0);
		REJECT(sp11_front_minimal_commands(out, sizeof(out), &mode), result);
	}
#undef REJECT
	struct { struct sp11_front_minimal mode; u8 tail[SP11_FRONT_MINIMAL_BYTES]; } alias;
	alias.mode = (struct sp11_front_minimal){{3840, 2160, 2560, 1440}, 10, SP11_FRONT_RGGB};
	u8 snapshot[sizeof(alias)]; memcpy(snapshot, &alias, sizeof(alias));
	assert(sp11_front_minimal_commands((u8 *)&alias, sizeof(alias), &alias.mode) == -EINVAL);
	assert(!memcmp(snapshot, &alias, sizeof(alias))); rejected++;
	printf("PASS minimal processing geometry=%u rejected=%u bytes=%u commands=81 DMI=0\n",
	       successful, rejected, SP11_FRONT_MINIMAL_BYTES);
	return 0;
}
