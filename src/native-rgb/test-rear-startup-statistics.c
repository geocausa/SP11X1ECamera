/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdio.h>
#include <stdlib.h>
#include "rear-statistics-host-fixture.h"
static unsigned assertions;
#define CHECK(x) do { assertions++; if (!(x)) { \
	fprintf(stderr, "FAIL:%d %s\n", __LINE__, #x); abort(); } } while (0)
static void positive(void)
{
	struct e008o_rear_packet_semantics base[4], before[4];
	struct native_rear_startup_stats_input input;
	static const u16 regs[3] = { 0xb060, 0xb660, 0xb860 };
	unsigned p, family, word;
	u32 value;
	CHECK(native_rear_stats_test_initialize(base, &input) == 0);
	memcpy(before, base, sizeof(base));
	CHECK(input.packet[0].aec.roi.width == 3658);
	CHECK(input.packet[0].aec.roi.height == 2058);
	CHECK(input.packet[1].aec.roi.width == 4064);
	CHECK(input.packet[1].aec.roi.height == 2286);
	CHECK(native_rear_bind_startup_statistics(base, &input) == 0);
	for (p = 0; p < 4; p++) {
		struct native_rear_bg_input *inputs[3] = {
			&input.packet[p].aec, &input.packet[p].tintless, &input.packet[p].awb,
		};
		struct e006w_aecbe17_state *outputs[3] = {
			&base[p].regs.aec_be, &base[p].regs.tintless_bg, &base[p].regs.awb_bg,
		};
		CHECK(!base[p].ready && base[p].request_id == before[p].request_id);
		CHECK(!memcmp(base[p].regs.unrelated, before[p].regs.unrelated, 32));
		CHECK(!memcmp(base[p].dmi, before[p].dmi, 32));
		CHECK(!memcmp(&base[p].regs.geometry, &before[p].regs.geometry, sizeof(base[p].regs.geometry)));
		CHECK(!memcmp(&base[p].regs.mnds, &before[p].regs.mnds, sizeof(base[p].regs.mnds)));
		CHECK(base[p].regs.rs.h_num == 16 && base[p].regs.rs.v_num == 1024);
		CHECK(base[p].regs.rs.region_width == 254 && base[p].regs.rs.region_height == 2);
		CHECK(base[p].regs.rs.h_num * base[p].regs.rs.region_width <= 4064);
		CHECK(base[p].regs.rs.v_num * base[p].regs.rs.region_height <= 2286);
		for (family = 0; family < 3; family++) {
			struct e006w_aecbe17_state *o = outputs[family];
			struct native_rear_bg_input *i = inputs[family];
			CHECK(o->h_num * o->region_width <= i->roi.width);
			CHECK(o->v_num * o->region_height <= i->roi.height);
			CHECK(!(o->region_width & 1) && !(o->region_height & 1));
			CHECK(o->black_level_offset == i->black_level_offset);
			for (word = 0; word < 18; word++)
				CHECK(native_rear_stats_test_lookup(&base[p], regs[family] + word * 4, &value) == 0);
			CHECK(native_rear_stats_test_lookup(&base[p], regs[family] + 0x24, &value) == 0);
			CHECK(value == (i->threshold_r << 14));
			CHECK(native_rear_stats_test_lookup(&base[p], regs[family] + 0x34, &value) == 0);
			CHECK(value == 0U - (i->black_level_offset << 13));
		}
		CHECK(native_rear_stats_test_lookup(&base[p], 0xb26c, &value) == 0);
		CHECK(value == ((input.packet[p].bhist.width / 2 - 1) |
			       ((u32)(input.packet[p].bhist.height / 2 - 1) << 16)));
		CHECK(native_rear_stats_test_lookup(&base[p], 0xbe60, &value) == 0);
		CHECK(!!(value & 0x10) == input.packet[p].rs.color_conversion);
	}
	CHECK(base[0].regs.aec_be.region_width == 56);
	CHECK(base[0].regs.aec_be.region_height == 42);
	CHECK(base[1].regs.aec_be.region_width == 126);
	CHECK(base[1].regs.aec_be.region_height == 70);
	CHECK(base[0].regs.tintless_bg.region_width == 126);
	CHECK(base[0].regs.tintless_bg.region_height == 94);
	CHECK(base[1].regs.awb_bg.region_width == 62);
	CHECK(base[1].regs.awb_bg.region_height == 46);
	memcpy(before, base, sizeof(base));
	CHECK(native_rear_bind_startup_statistics(base, &input) == 0);
	CHECK(!memcmp(base, before, sizeof(base)));
}
static void mutate(struct native_rear_packet_stats_input *i, unsigned field)
{
	switch (field) {
	case 0: i->request_id++; break;
	case 1: i->phase ^= 1; break;
	case 2: i->active_width--; break;
	case 3: i->active_height--; break;
	case 4: i->bhist.left = 2; break;
	case 5: i->bhist.width = 0; break;
	case 6: i->bhist.width = 65535; break;
	case 7: i->rs.v_num = 0; break;
	case 8: i->rs.roi.height = 100; break;
	case 9: i->rs.roi.top = 1; break;
	case 10: i->aec.h_num = 63; break;
	case 11: i->aec.roi.width = 10; break;
	case 12: i->aec.controls_valid = false; break;
	case 13: i->aec.threshold_r = 0x40000; break;
	case 14: i->aec.threshold_b = 0x40000; break;
	case 15: i->aec.threshold_gr = 0x40000; break;
	case 16: i->aec.threshold_gb = 0x40000; break;
	case 17: i->aec.black_level_offset = 0x40000; break;
	case 18: i->aec.y_weight_q4[2] = 128; break;
	case 19: i->tintless.roi.top = 1; break;
	case 20: i->tintless.controls_valid = false; break;
	case 21: i->tintless.v_num = 64; break;
	case 22: i->awb.roi.left = 1; break;
	case 23: i->awb.roi.height = 10; break;
	case 24: i->awb.controls_valid = false; break;
	case 25: i->awb.threshold_gb = 0x40000; break;
	case 26: i->awb.roi.top = 2286; break;
	case 27: i->awb.roi.width = 65535; break;
	}
}
static void negative(void)
{
	struct e008o_rear_packet_semantics base[4], before[4];
	struct native_rear_startup_stats_input input;
	unsigned p, field;
	for (p = 0; p < 4; p++) {
		for (field = 0; field < 28; field++) {
			CHECK(native_rear_stats_test_initialize(base, &input) == 0);
			mutate(&input.packet[p], field);
			memcpy(before, base, sizeof(base));
			CHECK(native_rear_bind_startup_statistics(base, &input) < 0);
			CHECK(!memcmp(base, before, sizeof(base)));
		}
		CHECK(native_rear_stats_test_initialize(base, &input) == 0);
		base[p].ready = true;
		memcpy(before, base, sizeof(base));
		CHECK(native_rear_bind_startup_statistics(base, &input) == -EBUSY);
		CHECK(!memcmp(base, before, sizeof(base)));
	}
	CHECK(native_rear_bind_startup_statistics(NULL, &input) == -EINVAL);
	CHECK(native_rear_bind_startup_statistics(base, NULL) == -EINVAL);
}
static void rs_request_override(void)
{
 struct e008o_rear_packet_semantics base[4], before[4];
 struct native_rear_startup_stats_input input;
 CHECK(native_rear_stats_test_initialize(base, &input) == 0);
 input.packet[1].rs.h_num = 1;
 input.packet[1].rs.v_num = 256;
 CHECK(native_rear_bind_startup_statistics(base, &input) == 0);
 CHECK(base[1].regs.rs.h_num == 1 && base[1].regs.rs.v_num == 256);
 CHECK(base[1].regs.rs.region_width == 4064 && base[1].regs.rs.region_height == 8);
 memcpy(before, base, sizeof(base));
 input.packet[3].rs.h_num = 17;
 CHECK(native_rear_bind_startup_statistics(base, &input) == -ERANGE);
 CHECK(!memcmp(base, before, sizeof(base)));
 input.packet[3].rs.h_num = 16;
 input.packet[3].rs.v_num = 1025;
 CHECK(native_rear_bind_startup_statistics(base, &input) == -ERANGE);
 CHECK(!memcmp(base, before, sizeof(base)));
}
static void preset_preservation(void)
{
	struct e008o_rear_packet_semantics base[4];
	struct native_rear_startup_stats_input input;
	struct native_rear_bg_input saved[3];
	struct native_rear_packet_stats_input before;
	unsigned preset;
	CHECK(native_rear_stats_test_initialize(base, &input) == 0);
	for (preset = 0; preset < 2; preset++) {
		saved[0] = input.packet[0].aec;
		saved[1] = input.packet[0].tintless;
		saved[2] = input.packet[0].awb;
		CHECK(native_rear_stats_geometry_preset(&input.packet[0], preset) == 0);
		CHECK(input.packet[0].aec.threshold_r == saved[0].threshold_r);
		CHECK(input.packet[0].tintless.black_level_offset == saved[1].black_level_offset);
		CHECK(!memcmp(input.packet[0].awb.y_weight_q4, saved[2].y_weight_q4, 3));
		CHECK(input.packet[0].aec.controls_valid == saved[0].controls_valid);
	}
	before = input.packet[0];
	CHECK(native_rear_stats_geometry_preset(&input.packet[0], 2) == -EINVAL);
	CHECK(!memcmp(&before, &input.packet[0], sizeof(before)));
	input.packet[0].active_width--;
	before = input.packet[0];
	CHECK(native_rear_stats_geometry_preset(&input.packet[0], NATIVE_REAR_STATS_COLD) == -EINVAL);
	CHECK(!memcmp(&before, &input.packet[0], sizeof(before)));
}
int main(void)
{
	positive(); negative(); rs_request_override(); preset_preservation();
 {
  struct e008o_rear_packet_semantics base[4], before[4];
  struct native_rear_startup_stats_input input;
  CHECK(native_rear_stats_test_initialize(base, &input) == 0);
  memcpy(before, base, sizeof(base));
  statistics_fail_allocation = true;
  CHECK(native_rear_bind_startup_statistics(base, &input) == -ENOMEM);
  CHECK(!memcmp(base, before, sizeof(base)));
  statistics_fail_allocation = false;
 }
 CHECK(statistics_allocations == 0);
	printf("NATIVE_REAR_STATISTICS_PASS assertions=%u hardware_callbacks=0\n", assertions);
	return 0;
}
