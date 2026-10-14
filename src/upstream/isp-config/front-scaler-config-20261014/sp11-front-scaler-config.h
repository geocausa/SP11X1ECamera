/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Reuse existing full-frame MNDS arithmetic for the calibrated front mode.
 * Omit both top-level module controls and all separate Crop12 commands.
 * The source normal-path image does not establish pixel-depth conversion.
 * No DMI, bus, allocation, MMIO or runtime caller.
 */
#ifndef SP11_FRONT_SCALER_CONFIG_H
#define SP11_FRONT_SCALER_CONFIG_H

#include "sp11-geometry-stats.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_SCALER_CONFIG_BYTES 88U

static inline int
sp11_front_scaler_config(u8 *out, size_t capacity,
			 const struct sp11_front_cold_policy *policy)
{
	u8 checked[SP11_FRONT_COLD_BYTES];
	u8 full[SP11_GEOMETRY_COMMAND_BYTES];
	u8 tmp[SP11_FRONT_SCALER_CONFIG_BYTES];
	struct sp11_geometry geometry;
	unsigned int plane;
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), policy, sizeof(*policy)))
		return -EINVAL;
	ret = sp11_front_cold_fields(checked, sizeof(checked), policy);
	if (ret)
		return ret;
	geometry.input_width = policy->domain.sensor_width;
	geometry.input_height = policy->domain.sensor_height;
	geometry.output_width = policy->domain.output_width;
	geometry.output_height = policy->domain.output_height;
	ret = sp11_geometry_commands_state(full, sizeof(full), &geometry, false);
	if (ret)
		return ret;
	for (plane = 0; plane < 2; plane++) {
		u8 *p = tmp + 44 * plane;

		/* Retained command: header/address, module word, nine fields. */
		sp11_cdm_put32(p, 0x03000009U);
		sp11_cdm_put32(p + 4, plane ? 0x9a64U : 0x9864U);
		memcpy(p + 8, full + 48 * plane + 12, 36);
	}
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
