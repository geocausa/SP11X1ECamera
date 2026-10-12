/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef CAMSS_CDM_POWER_H
#define CAMSS_CDM_POWER_H

#include <linux/clk.h>
#include <linux/device.h>
#include "camss-cdm-2-1.h"

/* Parent supplies reviewed, live PM-device and clock handles/array extent.
 * This does not discover DT routing, program clock rates, certify fresh power
 * or replace regulator/interconnect/domain sequencing in the parent.
 * Zeroed state, clock array and provider handles must outlive the bound backend.
 * Parent serializes construction, runtime operations and detach; callbacks
 * must not reenter these operations while the power mutex is held.
 */
struct camss_cdm21_power {
	struct camss_cdm21 *cdm;
	struct device *dev;
	const struct clk_bulk_data *clocks;
	int num_clocks;
	struct mutex lock;
	bool initialized;
	bool held;
	bool touched;
	bool fault;
};

int camss_cdm21_power_init(struct camss_cdm21_power *power,
			  struct camss_cdm21 *cdm, struct device *dev,
			  const struct clk_bulk_data *clocks, int num_clocks);
int camss_cdm21_power_hold(struct camss_cdm21_power *power);
int camss_cdm21_power_reset(struct camss_cdm21_power *power);

/* Release only an unused acquisition, before any reset/MMIO attempt.
 * There is deliberately no post-reset power-release API. Physical retirement
 * and full parent recovery must be implemented before runtime admission.
 */
int camss_cdm21_power_release_unused(struct camss_cdm21_power *power);

#endif
