// SPDX-License-Identifier: GPL-2.0-only
#include <assert.h>
#include <stdio.h>
#include "sp11-vfe680-nv12.h"
#ifdef SP11_NV12_REFERENCE
#include "nv12-reference.h"
#endif

static u32 le32(const u8 *p)
{
	return (u32)p[0] | (u32)p[1] << 8 | (u32)p[2] << 16 | (u32)p[3] << 24;
}

static void check_program(const u8 *p, const struct sp11_vfe680_nv12 *mode)
{
	u32 regs[2][28] = {{0}};
	bool seen[2][28] = {{false}};
	size_t pos = 0;
	unsigned int commands = 0;
	while (pos < SP11_VFE680_NV12_SETUP_BYTES) {
		u32 count = le32(p + pos) & 0xffffU;
		u32 reg = le32(p + pos + 4);
		assert(le32(p + pos) >> 24 == 3 && count && !(reg & 3));
		assert(pos + 8 + count * 4 <= SP11_VFE680_NV12_SETUP_BYTES);
		if (commands < 2)
			assert(count == 1 && reg == 0xe00 + commands * 0x100);
		for (u32 j = 0; j < count; j++) {
			u32 addr = reg + j * 4, plane = (addr - 0xe00) / 0x100;
			u32 word = ((addr - 0xe00) % 0x100) / 4;
			assert(addr >= 0xe00 && addr < 0xf70 && plane < 2 && word < 28);
			assert(!seen[plane][word]);
#ifdef SP11_NV12_REFERENCE
			bool public_address = false;
			for (u32 k = 0; k < 17; k++)
				if (addr == public_nv12_registers[plane][k]) public_address = true;
			assert(public_address);
#endif
			seen[plane][word] = true;
			regs[plane][word] = le32(p + pos + 8 + j * 4);
		}
		commands++;
		pos += 8 + count * 4;
	}
	assert(pos == SP11_VFE680_NV12_SETUP_BYTES && commands == 12);
	for (u32 i = 0; i < 2; i++) {
		const struct sp11_vfe680_nv12_plane *plane = &mode->plane[i];
		u32 height = mode->height >> i;
		const bool expected[28] = {
			[0] = true, [1] = true, [2] = true, [3] = true,
			[4] = true, [5] = true, [6] = true, [8] = true,
			[9] = true, [10] = true, [12] = true, [13] = true,
			[14] = true, [15] = true, [18] = true, [24] = true, [25] = true
		};
		for (u32 j = 0; j < 28; j++) assert(seen[i][j] == expected[j]);
		assert(regs[i][0] == 0); /* no enable, frame header or frame-based mode */
		assert(regs[i][1] == plane->dma_base + plane->offset);
		assert(regs[i][2] == (u64)plane->stride * height);
		assert(regs[i][3] == ((height << 16) | mode->width));
		assert(regs[i][4] == 0 && regs[i][5] == plane->stride);
		assert(regs[i][6] == 3);
		assert(regs[i][8] == 0 && regs[i][9] == 0 && regs[i][10] == 0);
		assert(regs[i][12] == 0 && regs[i][13] == 1);
		assert(regs[i][14] == 0 && regs[i][15] == 1);
		assert(regs[i][18] == 0 && regs[i][24] == 0 && regs[i][25] == 0);
#ifdef SP11_NV12_REFERENCE
		struct cam_vfe_bus_ver3_wm_resource_data ref = {CAM_FORMAT_NV12, i, 2};
		assert(regs[i][6] == cam_vfe_bus_ver3_get_packer_fmt(&ref));
#endif
	}
}

static struct sp11_vfe680_nv12 mode_for(u32 width, u32 height, u32 padding)
{
	struct sp11_vfe680_nv12 mode = {.width = width, .height = height};
	for (u32 i = 0; i < 2; i++) {
		mode.plane[i].stride = ((width + 15) & ~15U) + padding;
		mode.plane[i].dma_base = i ? 0x80000000ULL : 0x10000000ULL;
		mode.plane[i].offset = 16;
		mode.plane[i].allocation_bytes = 16 + (u64)mode.plane[i].stride * (height >> i);
	}
	return mode;
}

int main(void)
{
	const u32 widths[] = {2, 16, 64, 640, 1920, 2560, 3840, 16384};
	const u32 heights[] = {2, 16, 64, 480, 1080, 1440, 2160, 16384};
	u8 out[SP11_VFE680_NV12_SETUP_BYTES + 16], expected[sizeof(out)];
	struct sp11_vfe680_nv12 mode;
	unsigned int good = 0, rejected = 0;
	assert(SP11_VFE680_NV12_SETUP_BYTES == 232);
	for (u32 w = 0; w < 8; w++) for (u32 h = 0; h < 8; h++)
		for (u32 padding = 0; padding <= 48; padding += 16) {
			mode = mode_for(widths[w], heights[h], padding);
			memset(out, 0xa5, sizeof(out));
			assert(!sp11_vfe680_nv12_setup_disabled(out, sizeof(out), &mode));
			check_program(out, &mode);
			for (size_t i = SP11_VFE680_NV12_SETUP_BYTES; i < sizeof(out); i++)
				assert(out[i] == 0xa5);
			good++;
		}
	mode = mode_for(2560, 1440, 0);
#define REJECT(call) do { \
	memset(out, 0xa5, sizeof(out)); memcpy(expected, out, sizeof(out)); \
	assert((call) < 0); assert(!memcmp(out, expected, sizeof(out))); rejected++; \
} while (0)
	for (size_t capacity = 0; capacity < SP11_VFE680_NV12_SETUP_BYTES; capacity++)
		REJECT(sp11_vfe680_nv12_setup_disabled(out, capacity, &mode));
	REJECT(sp11_vfe680_nv12_setup_disabled(NULL, sizeof(out), &mode));
	REJECT(sp11_vfe680_nv12_setup_disabled(out, sizeof(out), NULL));
#define INVALID(change) do { \
	mode = mode_for(2560, 1440, 0); change; \
	REJECT(sp11_vfe680_nv12_setup_disabled(out, sizeof(out), &mode)); \
} while (0)
	INVALID(mode.width = 0); INVALID(mode.height = 0);
	INVALID(mode.width = 2559); INVALID(mode.height = 1439);
	INVALID(mode.width = 16386); INVALID(mode.height = 16386);
	for (u32 i = 0; i < 2; i++) {
		INVALID(mode.plane[i].stride = 2544);
		INVALID(mode.plane[i].stride = 2561);
		INVALID(mode.plane[i].stride = 0xfffffff0U);
		INVALID(mode.plane[i].allocation_bytes = 0);
		INVALID(mode.plane[i].allocation_bytes--);
		INVALID(mode.plane[i].allocation_bytes = 0x100000000ULL);
		INVALID(mode.plane[i].dma_base = 0x100000000ULL);
		INVALID(mode.plane[i].dma_base++);
		INVALID(mode.plane[i].dma_base = 0xfffffff0ULL);
		INVALID(mode.plane[i].offset++);
		INVALID(mode.plane[i].offset = mode.plane[i].allocation_bytes + 16);
		INVALID(mode.plane[i].offset = 0xfffffffffffffff0ULL);
	}
	INVALID(mode.plane[1] = mode.plane[0]);
#undef INVALID
#undef REJECT
	/* Exactly adjacent spans in one allocation are legal. */
	mode = mode_for(2560, 1440, 0);
	mode.plane[0].allocation_bytes += (u64)mode.plane[1].stride * 720;
	mode.plane[1].dma_base = mode.plane[0].dma_base;
	mode.plane[1].allocation_bytes = mode.plane[0].allocation_bytes;
	mode.plane[1].offset = 16 + (u64)mode.plane[0].stride * 1440;
	assert(!sp11_vfe680_nv12_setup_disabled(out, sizeof(out), &mode));
	check_program(out, &mode); good++;
	mode = mode_for(16, 2, 0);
	mode.plane[0] = (struct sp11_vfe680_nv12_plane){0xffffffe0ULL, 32, 0, 16};
	assert(!sp11_vfe680_nv12_setup_disabled(out, sizeof(out), &mode));
	check_program(out, &mode); good++;
	struct { struct sp11_vfe680_nv12 mode; u8 tail[SP11_VFE680_NV12_SETUP_BYTES]; } alias;
	alias.mode = mode_for(2560, 1440, 0);
	u8 snapshot[sizeof(alias)]; memcpy(snapshot, &alias, sizeof(alias));
	assert(sp11_vfe680_nv12_setup_disabled((u8 *)&alias, sizeof(alias), &alias.mode) == -EINVAL);
	assert(!memcmp(snapshot, &alias, sizeof(alias))); rejected++;
#ifdef SP11_NV12_REFERENCE
	for (u32 i = 0; i < 2; i++) {
		struct cam_vfe_bus_ver3_wm_resource_data ref = {CAM_FORMAT_NV21, i, 2};
		assert(cam_vfe_bus_ver3_get_packer_fmt(&ref) == (i ? 4 : 3));
		ref.format = CAM_FORMAT_NV12; ref.num_planes = 3;
		assert(cam_vfe_bus_ver3_get_packer_fmt(&ref) == 1);
	}
#endif
	printf("PASS NV12 geometry=%u atomic_rejections=%u bytes=232 commands=12 clients_enabled=0\n",
	       good, rejected);
	return 0;
}
