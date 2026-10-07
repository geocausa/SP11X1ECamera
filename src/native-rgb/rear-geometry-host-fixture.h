/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual packers and binder; unrelated packet fields omitted only in this fixture. */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#define __used __attribute__((used))
#define E007Y_STARTUP_PACKETS 4
typedef int (*e006m_scalar_fn)(void *, u16, u32 *);
#include "camss-e006p-crop-roundclamp.inc"
#include "camss-e006q-mnds23.inc"
#include "camss-e006s-bc101.inc"
#include "camss-e006t-small-iq.inc"
#include "e007c-period-types.h"
#include "camss-e007w-period-cfg.inc"
struct e008o_rear_packet_semantics {
	struct {
		struct e006p_rear_geometry geometry;
		struct e006q_mnds23_state mnds;
		struct e007c_period_cfg_state period;
		struct e006s_bc101_state bc101;
		struct e006t_small_iq_state small_iq;
		u8 unrelated[32];
	} regs;
	u8 dmi[32];
	u64 request_id;
	bool ready;
};
#include "native-rear-startup-geometry.inc"
static void native_rear_geometry_test_init(
	struct e008o_rear_packet_semantics base[4],
	struct native_rear_geometry_mode *mode)
{
	static const u64 ids[4] = {4, 5, 6, 6};
	unsigned p;
	memset(base, 0x5a, sizeof(*base) * 4);
	memset(mode, 0, sizeof(*mode));
	mode->sensor_width = 4076;
	mode->sensor_height = 2806;
	mode->isp_width = 4064;
	mode->isp_height = 2286;
	mode->output_width = 3840;
	mode->output_height = 2160;
	mode->bit_width = 10;
	for (p = 0; p < 4; p++) {
		base[p].ready = false;
		mode->request_id[p] = base[p].request_id = ids[p];
	}
}
static int native_rear_geometry_test_lookup(
	struct e008o_rear_packet_semantics *packet, unsigned phase,
	u16 reg, u32 *value)
{
	int ret;
	if (phase >= 4)
		return -EINVAL;
	if (reg == E007C_PERIOD_CFG_REG)
		return e007c_period_cfg_lookup(&packet->regs.period, phase, reg, value);
	ret = e006p_crop12_lookup(&packet->regs.geometry, reg, value);
	if (ret != -ENOENT)
		return ret;
	ret = e006p_roundclamp12_lookup(&packet->regs.geometry, reg, value);
	if (ret != -ENOENT)
		return ret;
	ret = e006q_mnds23_lookup(&packet->regs.mnds, reg, value);
	if (ret != -ENOENT)
		return ret;
	ret = e006s_bc101_lookup(&packet->regs.bc101, reg, value);
	if (ret != -ENOENT)
		return ret;
	ret = e006t_bayer_gtm101_lookup(&packet->regs.small_iq, reg, value);
	if (ret != -ENOENT)
		return ret;
	ret = e006t_bayer_ltm101_lookup(&packet->regs.small_iq, reg, value);
	if (ret != -ENOENT)
		return ret;
	ret = e006t_lcac111_lookup(&packet->regs.small_iq, reg, value);
	if (ret != -ENOENT)
		return ret;
	return e006t_uv_gamma101_lookup(&packet->regs.small_iq, reg, value);
}
