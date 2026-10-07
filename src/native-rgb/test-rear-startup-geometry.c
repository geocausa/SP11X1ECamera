/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdio.h>
#include <stdlib.h>
#include "rear-geometry-host-fixture.h"
static unsigned assertions;
#define CHECK(x) do { assertions++; if (!(x)) { \
	fprintf(stderr, "FAIL:%d %s\n", __LINE__, #x); abort(); } } while (0)
static void positive(void)
{
	struct e008o_rear_packet_semantics base[4], before[4];
	struct native_rear_geometry_mode mode;
	static const u16 widths[3] = {3840, 960, 240};
	static const u16 heights[3] = {2160, 540, 136};
	static const u16 luma_base[3] = {0x9c60, 0xa460, 0xac60};
	static const u16 chroma_base[3] = {0x9e60, 0xa660, 0xae60};
	unsigned p, path, plane, i;
	u32 value;
	native_rear_geometry_test_init(base, &mode);
	memcpy(before, base, sizeof(base));
	CHECK(native_rear_bind_startup_geometry(base, &mode) == 0);
	for (p = 0; p < 4; p++) {
		CHECK(!base[p].ready && base[p].request_id == before[p].request_id);
		CHECK(!memcmp(base[p].regs.unrelated, before[p].regs.unrelated, 32));
		CHECK(!memcmp(base[p].dmi, before[p].dmi, 32));
		CHECK(base[p].regs.mnds.input_width == 4064);
		CHECK(base[p].regs.mnds.input_height == 2286);
		for (path = 0; path < 3; path++) {
			for (plane = 0; plane < 2; plane++) {
				u16 address = plane ? chroma_base[path] : luma_base[path];
				u16 width = widths[path] / (plane ? 2 : 1);
				u16 height = heights[path] / (plane ? 2 : 1);
				CHECK(native_rear_geometry_test_lookup(&base[p], p,
				       address + 8, &value) == 0);
				CHECK(value == (u32)(height - 1));
				CHECK(native_rear_geometry_test_lookup(&base[p], p,
				       address + 12, &value) == 0);
				CHECK(value == (u32)(width - 1));
				CHECK(native_rear_geometry_test_lookup(&base[p], p,
				       address, &value) == 0 && (value & 0x200));
				for (i = 0; i < 10; i++)
					CHECK(native_rear_geometry_test_lookup(&base[p], p,
					       address + 0x10 + 4 * i, &value) == 0);
				CHECK(native_rear_geometry_test_lookup(&base[p], p,
				       address + 0x28, &value) == 0 && value == 1023);
			}
		}
		for (plane = 0; plane < 2; plane++) {
			u16 address = plane ? 0x9a60 : 0x9860;
			for (i = 0; i < 10; i++)
				CHECK(native_rear_geometry_test_lookup(&base[p], p,
				       address + 4 * i, &value) == 0);
		}
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x8c, &value) == 0);
		CHECK(value == 0); /* canonical non-HFR, no undefined upper bits */
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x3f60, &value) == 0 && !value);
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x3f64, &value) == 0 && !value);
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x3f68, &value) == 0 && !value);
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x4d60, &value) == 0 && !value);
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x5260, &value) == 0 && !value);
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x5460, &value) == 0 && !value);
		CHECK(native_rear_geometry_test_lookup(&base[p], p, 0x6360, &value) == 0 && !value);
	}
	memcpy(before, base, sizeof(base));
	CHECK(native_rear_bind_startup_geometry(base, &mode) == 0);
	CHECK(!memcmp(before, base, sizeof(base)));
	value = 0x12345678;
	CHECK(native_rear_geometry_test_lookup(&base[0], 0, 0xffff, &value) == -ENOENT);
	CHECK(value == 0x12345678);
}
static void negative(void)
{
	struct e008o_rear_packet_semantics base[4], before[4];
	struct native_rear_geometry_mode mode, valid;
	unsigned p, field;
	native_rear_geometry_test_init(base, &valid);
	for (p = 0; p < 4; p++) {
		mode = valid;
		mode.request_id[p]++;
		memcpy(before, base, sizeof(base));
		CHECK(native_rear_bind_startup_geometry(base, &mode) == -ESTALE);
		CHECK(!memcmp(before, base, sizeof(base)));
		mode = valid;
		base[p].ready = true;
		memcpy(before, base, sizeof(base));
		CHECK(native_rear_bind_startup_geometry(base, &mode) == -EBUSY);
		CHECK(!memcmp(before, base, sizeof(base)));
		base[p].ready = false;
		mode.request_id[p] = base[p].request_id = 3;
		memcpy(before, base, sizeof(base));
		CHECK(native_rear_bind_startup_geometry(base, &mode) == -ESTALE);
		CHECK(!memcmp(before, base, sizeof(base)));
		base[p].request_id = valid.request_id[p];
	}
	for (field = 0; field < 7; field++) {
		mode = valid;
		switch (field) {
		case 0: mode.sensor_width--; break;
		case 1: mode.sensor_height--; break;
		case 2: mode.isp_width--; break;
		case 3: mode.isp_height--; break;
		case 4: mode.output_width--; break;
		case 5: mode.output_height--; break;
		case 6: mode.bit_width = 8; break;
		}
		memcpy(before, base, sizeof(base));
		CHECK(native_rear_bind_startup_geometry(base, &mode) == -EOPNOTSUPP);
		CHECK(!memcmp(before, base, sizeof(base)));
	}
	CHECK(native_rear_bind_startup_geometry(NULL, &valid) == -EINVAL);
	CHECK(native_rear_bind_startup_geometry(base, NULL) == -EINVAL);
}
int main(void)
{
	positive();
	negative();
	printf("NATIVE_REAR_GEOMETRY_PASS assertions=%u hardware_callbacks=0\n", assertions);
	return 0;
}
