/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef CAMSS_CDM_COMMAND_H
#define CAMSS_CDM_COMMAND_H
#include "camss-cdm-power.h"
#include "sp11-front-minimal.h"

/* Opaque coherent command allocation. Its CPU pointer is never published.
 * Parent power/backend storage, DMA-device binding and reviewed handles must
 * outlive every program. Serialize construction, calls and all parent detach
 * operations. Device/module refs preserve objects/code, not devres or clocks.
 */
struct camss_cdm21_program;

int camss_cdm21_program_create(struct camss_cdm21_power *power,
			      u64 owner, u64 request,
			      const struct sp11_front_minimal *mode,
			      struct camss_cdm21_program **out);
int camss_cdm21_program_submit(struct camss_cdm21_power *power,
			      struct camss_cdm21_program *program,
			      struct sp11_cdm21_receipt *receipt);
/* Only an untransferred allocation can be destroyed. Submitted, failed after
 * retention, and successfully completed commands remain pinned until reboot.
 */
int camss_cdm21_program_destroy_unused(struct camss_cdm21_power *power,
				      struct camss_cdm21_program **program);

/* A refusal predicate for future parent admission, not a platform .remove
 * veto. Linux core still releases devres after a void remove callback. Real
 * pre-detach exclusion or resource-retaining teardown is required before use.
 */
int camss_cdm21_power_detach_ready(struct camss_cdm21_power *power);
#endif
