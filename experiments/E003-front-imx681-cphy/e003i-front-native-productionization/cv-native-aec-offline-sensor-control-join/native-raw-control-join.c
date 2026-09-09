// SPDX-License-Identifier: GPL-2.0-only
#include "native-raw-control-join.h"

#include <limits.h>
#include <stddef.h>
#include <string.h>

int e003i_raw_request_to_imx681_controls(
    struct e003i_request_loop_state *state,
    const struct e003i_raw_request_input *in,
    struct e003i_raw_control_output *out)
{
    struct e003i_request_loop_state shadow;
    struct e003i_raw_control_output tmp;
    int rc;

    if (state == NULL || in == NULL || out == NULL)
        return -1;

    /* Keep the caller recurrence atomic across the appended CQ conversion. */
    shadow = *state;
    memset(&tmp, 0, sizeof(tmp));

    rc = e003i_raw_request_loop_process(&shadow, in, &tmp.raw);
    if (rc != 0)
        return -10 + rc;

    /* W proves request_frame = source_generation + 3 for ordinary front. */
    if (tmp.raw.stats_generation > UINT64_MAX - E003I_STATS_TO_REQUEST_DELAY_FRAMES)
        return -20;
    tmp.stats_owned_request_frame =
        tmp.raw.stats_generation + E003I_STATS_TO_REQUEST_DELAY_FRAMES;

    /*
     * AV proves linecount/gain/FLL delay=maxPipeline=2, so CamX performs no
     * extra request-history substitution.  Keep the two-frame sensor pipeline
     * depth explicit without claiming the still-unproven optical latch frame.
     */
    tmp.sensor_pipeline_delay_frames = E003I_IMX681_SENSOR_PIPELINE_DELAY_FRAMES;
    tmp.camx_history_realign_frames = E003I_IMX681_CAMX_HISTORY_REALIGN_FRAMES;

    rc = e003i_imx681_controls_from_t681(&tmp.raw.request.short_arbitration,
                                         &tmp.controls);
    if (rc != 0)
        return -30 + rc;

    *state = shadow;
    *out = tmp;
    return 0;
}
