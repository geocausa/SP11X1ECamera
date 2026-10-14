/* SPDX-License-Identifier: GPL-2.0-only */
/* Reuse retained Crop12 coordinates for the calibrated front output only. */
#ifndef SP11_FRONT_CROP_CONFIG_H
#define SP11_FRONT_CROP_CONFIG_H

#include "sp11-geometry-stats.h"
#include "sp11-front-cold-fields.h"

#define SP11_FRONT_CROP_CONFIG_BYTES 32U

static inline int
sp11_front_crop_config(u8 *out, size_t capacity,
		       const struct sp11_front_cold_policy *policy)
{
	u8 checked[SP11_FRONT_COLD_BYTES];
	u8 full[SP11_GEOMETRY_COMMAND_BYTES];
	struct sp11_geometry geometry;
	int ret;

	if (!out || !policy)
		return -EINVAL;
	if (capacity < SP11_FRONT_CROP_CONFIG_BYTES)
		return -ENOSPC;
	if (sp11_cdm_overlap(out, SP11_FRONT_CROP_CONFIG_BYTES, policy,
			     sizeof(*policy)))
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
	/* Existing last two commands own only output Crop12 coordinates. */
	memcpy(out, full + 96, SP11_FRONT_CROP_CONFIG_BYTES);
	return 0;
}
#endif
