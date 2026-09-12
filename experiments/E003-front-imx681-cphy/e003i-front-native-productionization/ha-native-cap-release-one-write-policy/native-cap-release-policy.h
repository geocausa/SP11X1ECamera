// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_CAP_RELEASE_POLICY_H
#define E003I_NATIVE_CAP_RELEASE_POLICY_H
#include <stdint.h>
#include "native-raw-control-join.h"

enum e003i_ha_decision {
    E003I_HA_STARTUP_OWNED = 1,
    E003I_HA_SHADOW_CAP_ACTIVE = 2,
    E003I_HA_SHADOW_UNCHANGED = 3,
    E003I_HA_APPLY_ONE_NATIVE = 4,
    E003I_HA_SHADOW_ALREADY_APPLIED = 5,
    E003I_HA_SHADOW_INVALID = 6,
};

enum e003i_ha_decision
e003i_ha_decide(uint32_t source_generation,
                uint32_t later_native_write_already_applied,
                const struct e003i_imx681_controls *last_applied,
                const struct e003i_raw_control_output *native_output);
#endif
