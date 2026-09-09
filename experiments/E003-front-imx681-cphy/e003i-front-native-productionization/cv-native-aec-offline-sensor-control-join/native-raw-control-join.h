// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_NATIVE_RAW_CONTROL_JOIN_H
#define E003I_NATIVE_RAW_CONTROL_JOIN_H

#include <stdint.h>

#include "native-imx681-control.h"
#include "native-raw-aec-loop.h"

#define E003I_STATS_TO_REQUEST_DELAY_FRAMES UINT64_C(3)
#define E003I_IMX681_SENSOR_PIPELINE_DELAY_FRAMES UINT32_C(2)
#define E003I_IMX681_CAMX_HISTORY_REALIGN_FRAMES UINT32_C(0)

struct e003i_raw_control_output {
    struct e003i_raw_request_output raw;
    uint64_t stats_owned_request_frame;
    uint32_t sensor_pipeline_delay_frames;
    uint32_t camx_history_realign_frames;
    struct e003i_imx681_controls controls;
};

/*
 * Pure offline composition:
 *   generation-tagged STATS3A -> CU native AEC -> CQ IMX681 control tuple.
 *
 * The caller state is committed only after both CU and CQ succeed.  This
 * function opens no device and issues no ioctl/CCI/I2C operation.
 */
int e003i_raw_request_to_imx681_controls(
    struct e003i_request_loop_state *state,
    const struct e003i_raw_request_input *in,
    struct e003i_raw_control_output *out);

#endif
