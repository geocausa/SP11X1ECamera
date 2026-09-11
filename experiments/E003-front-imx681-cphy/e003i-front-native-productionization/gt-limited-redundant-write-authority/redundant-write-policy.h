// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_REDUNDANT_WRITE_POLICY_H
#define E003I_REDUNDANT_WRITE_POLICY_H
#include <stdint.h>
#include "native-imx681-control.h"

enum e003i_redundant_write_decision {
    E003I_WRITE_PROVEN_STARTUP = 1,
    E003I_WRITE_REDUNDANT_ALLOWED = 2,
    E003I_WRITE_SHADOW_CHANGED = 3,
    E003I_WRITE_SHADOW_BOUND = 4,
};

int e003i_sensor_controls_equal(const struct e003i_imx681_controls *a,
                                const struct e003i_imx681_controls *b);
enum e003i_redundant_write_decision
e003i_redundant_write_decide(uint32_t source_generation,
                             const struct e003i_imx681_controls *last_applied,
                             const struct e003i_imx681_controls *candidate);
#endif
