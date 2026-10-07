/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual staged packers/composer. Unrelated full packet fields omitted only here. */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#define __used __attribute__((used))
#define GFP_KERNEL 0
static unsigned statistics_allocations;
static bool statistics_fail_allocation;
static void *kzalloc(size_t size, int flags)
{
 void *p;
 (void)flags;
 if (statistics_fail_allocation) return NULL;
 p = calloc(1, size);
 if (p) statistics_allocations++;
 return p;
}
static void kfree(void *p)
{
 if (p) { statistics_allocations--; free(p); }
}
static void memzero_explicit(void *p, size_t size) { memset(p, 0, size); }
#define E007Y_STARTUP_PACKETS 4
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define BIT(n) (1U << (n))
typedef int (*e006m_scalar_fn)(void *, u16, u32 *);
#include "camss-e006p-crop-roundclamp.inc"
#include "camss-e006q-mnds23.inc"
#include "camss-e006s-bc101.inc"
#include "camss-e006t-small-iq.inc"
#include "e007c-period-types.h"
static typeof(&e007c_period_cfg_lookup) statistics_period_typecheck __used = e007c_period_cfg_lookup;
#include "camss-e007w-period-cfg.inc"
#include "camss-e006u-bhist16.inc"
#include "camss-e006v-rsstats14.inc"
#include "camss-e006w-aecbe17.inc"
#include "camss-e006x-tintlessbg17.inc"
#include "camss-e006y-awbbg17.inc"
struct e008o_rear_packet_semantics {
	struct {
		struct e006p_rear_geometry geometry;
		struct e006q_mnds23_state mnds;
		struct e007c_period_cfg_state period;
		struct e006s_bc101_state bc101;
		struct e006t_small_iq_state small_iq;
		struct e006u_bhist16_state bhist;
		struct e006v_rs14_state rs;
		struct e006w_aecbe17_state aec_be, tintless_bg, awb_bg;
		u8 unrelated[32];
	} regs;
	u8 dmi[32];
	u64 request_id;
	bool ready;
};
#include "native-rear-startup-geometry.inc"
#include "native-rear-startup-statistics.inc"

static int native_rear_stats_test_initialize(
	struct e008o_rear_packet_semantics base[4],
	struct native_rear_startup_stats_input *input)
{
	static const u64 ids[4] = {4, 5, 6, 6};
	struct native_rear_geometry_mode geometry = {
		.sensor_width = 4076, .sensor_height = 2806,
		.isp_width = 4064, .isp_height = 2286,
		.output_width = 3840, .output_height = 2160, .bit_width = 10,
	};
	unsigned p, family;
	int ret;
	memset(base, 0x5a, sizeof(*base) * 4);
	memset(input, 0, sizeof(*input));
	for (p = 0; p < 4; p++) {
		struct native_rear_packet_stats_input *i = &input->packet[p];
		struct native_rear_bg_input *bg[3] = { &i->aec, &i->tintless, &i->awb };
		base[p].request_id = geometry.request_id[p] = i->request_id = ids[p];
		base[p].ready = false;
		i->phase = p;
		i->active_width = 4064;
		i->active_height = 2286;
		ret = native_rear_stats_geometry_preset(i, p ? NATIVE_REAR_STATS_NORMAL : NATIVE_REAR_STATS_COLD);
		if (ret)
			return ret;
		i->rs.color_conversion = p & 1;
		for (family = 0; family < 3; family++) {
			bg[family]->threshold_r = 200000 + p * 100 + family;
			bg[family]->threshold_b = 201000 + p * 100 + family;
			bg[family]->threshold_gr = 202000 + p * 100 + family;
			bg[family]->threshold_gb = 203000 + p * 100 + family;
			bg[family]->black_level_offset = 32 + p + family;
			bg[family]->y_weight_q4[0] = 4;
			bg[family]->y_weight_q4[1] = 8;
			bg[family]->y_weight_q4[2] = 4;
			bg[family]->quad_sync_enable = p & 1;
			bg[family]->enabled = true;
			bg[family]->controls_valid = true;
		}
	}
	return native_rear_bind_startup_geometry(base, &geometry);
}

static int native_rear_stats_test_lookup(
	struct e008o_rear_packet_semantics *p, u16 reg, u32 *out)
{
	if (reg >= 0xb060 && reg <= 0xb0a4)
		return e006w_aecbe17_lookup(&p->regs.aec_be, reg, out);
	if (reg >= 0xb660 && reg <= 0xb6a4)
		return e006x_tintless_bg17_lookup(&p->regs.tintless_bg, reg, out);
	if (reg >= 0xb860 && reg <= 0xb8a4)
		return e006y_awbbg17_lookup(&p->regs.awb_bg, reg, out);
	if (reg == 0xbe60 || reg == 0xbe68 || reg == 0xbe6c || reg == 0xbe70)
		return e006v_rs14_lookup(&p->regs.rs, reg, out);
	return e006u_bhist16_lookup(&p->regs.bhist, reg, out);
}
