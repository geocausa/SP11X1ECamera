// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_MINIMAL_DGAIN_SENTINEL_H
#define E003I_MINIMAL_DGAIN_SENTINEL_H
#include <stdint.h>
#include "native-imx681-control.h"

enum e003i_gw_decision {
    E003I_GW_APPLY_SENTINEL = 1,
    E003I_GW_SHADOW_NOT_SOURCE = 2,
    E003I_GW_SHADOW_BASE_CHANGED = 3,
    E003I_GW_SHADOW_RANGE = 4,
};

enum e003i_gw_decision
e003i_gw_make_sentinel(uint32_t source_generation,
                       const struct e003i_imx681_controls *last_applied,
                       const struct e003i_imx681_controls *native_candidate,
                       struct e003i_imx681_controls *sentinel);
#endif
