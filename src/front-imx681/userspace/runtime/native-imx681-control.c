// SPDX-License-Identifier: GPL-2.0-only
#include <math.h>
#include <stdint.h>
#include <string.h>
#include "native-imx681-control.h"

#define E003I_IMX681_WIDTH                 3840U
#define E003I_IMX681_HEIGHT                2160U
#define E003I_IMX681_LINE_LENGTH           6752U
#define E003I_IMX681_DEFAULT_FLL           3554U
#define E003I_IMX681_FPS                   30.0
#define E003I_IMX681_MIN_LINE_COUNT        4U
#define E003I_IMX681_VERT_OFFSET           8U
#define E003I_IMX681_EXTRA_OFFSET          0U
#define E003I_IMX681_ANALOG_SCALE          1024.0
#define E003I_IMX681_ANALOG_REG_MAX        0x03c0U
#define E003I_IMX681_DIGITAL_SCALE_F       256.0f
#define E003I_IMX681_DIGITAL_INV_SCALE_F   (1.0f / 256.0f)
#define E003I_IMX681_DIGITAL_REAL_MAX_F    15.0f
#define E003I_T681_GAIN_MIN_F              1.0f
/* AQ 2026-09-10 live controller recapture pins the active preview range. */
#define E003I_T681_GAIN_OUTPUT_MAX_F       92.0f
#define E003I_T681_TIME_MIN_NS             UINT64_C(37516)
#define E003I_T681_TIME_MAX_NS             UINT64_C(66666664)

static double e003i_imx681_line_readout_ns(void)
{
    uint32_t pixels_per_frame;
    double vt_clock_f;
    uint64_t vt_clock;

    /*
     * Mirrors ImageSensorData::GetLineReadoutTime for the selected ordinary
     * mode: 32-bit lineLength*frameLength, multiply by maxFPS in double,
     * FCVTZU to the integer VT clock, then lineLength*1e9 / VT clock.
     */
    pixels_per_frame = E003I_IMX681_LINE_LENGTH * E003I_IMX681_DEFAULT_FLL;
    vt_clock_f = (double)pixels_per_frame * E003I_IMX681_FPS;
    vt_clock = (uint64_t)vt_clock_f;

    return ((double)(E003I_IMX681_LINE_LENGTH & 0xffffU) * 1000000000.0) /
           (double)vt_clock;
}

static uint32_t e003i_windows_frinta_positive(double value)
{
    /* ARM64 FRINTA: nearest integer, ties away from zero. Inputs are > 0. */
    return (uint32_t)round(value);
}

static void e003i_imx681_gain_codes(float requested_gain,
                                    uint32_t *analogue_gain_code,
                                    uint32_t *digital_gain_code,
                                    float *isp_gain)
{
    double target;
    uint32_t analog_reg;
    float analog_gain;
    float digital_target;
    uint32_t digital_reg;
    float digital_gain;

    target = (double)requested_gain;
    if (target < 1.0)
        target = 1.0;
    else if (target > 16.0)
        target = 16.0;

    analog_reg = (uint32_t)(E003I_IMX681_ANALOG_SCALE -
                            E003I_IMX681_ANALOG_SCALE / target);
    if (analog_reg > E003I_IMX681_ANALOG_REG_MAX)
        analog_reg = E003I_IMX681_ANALOG_REG_MAX;

    analog_gain = (float)(E003I_IMX681_ANALOG_SCALE /
                          (E003I_IMX681_ANALOG_SCALE - (double)analog_reg));

    if (requested_gain <= 16.0f)
        digital_target = 1.0f;
    else
        digital_target = requested_gain / analog_gain;
    if (digital_target > E003I_IMX681_DIGITAL_REAL_MAX_F)
        digital_target = E003I_IMX681_DIGITAL_REAL_MAX_F;

    digital_reg = (uint32_t)(digital_target * E003I_IMX681_DIGITAL_SCALE_F);
    digital_gain = (float)digital_reg * E003I_IMX681_DIGITAL_INV_SCALE_F;

    *analogue_gain_code = analog_reg;
    *digital_gain_code = digital_reg;
    *isp_gain = requested_gain / (analog_gain * digital_gain);
}

int e003i_imx681_controls_from_t681(const struct e003i_t681_result *in,
                                    struct e003i_imx681_controls *out)
{
    double lines;
    uint32_t line_count;
    uint32_t frame_length;

    if (in == NULL || out == NULL)
        return -1;
    if (!isfinite(in->gain) || in->gain < E003I_T681_GAIN_MIN_F ||
        in->gain > E003I_T681_GAIN_OUTPUT_MAX_F)
        return -2;
    if (in->exposure_time_ns < E003I_T681_TIME_MIN_NS ||
        in->exposure_time_ns > E003I_T681_TIME_MAX_NS)
        return -3;

    lines = (double)in->exposure_time_ns / e003i_imx681_line_readout_ns();
    if (lines < (double)E003I_IMX681_MIN_LINE_COUNT)
        lines = (double)E003I_IMX681_MIN_LINE_COUNT;
    line_count = e003i_windows_frinta_positive(lines);

    /*
     * CQ3/CQ4 prove ordinary policy code 8 with extraOffset==0. Once the
     * nominal frame cannot contain lineCount+vertOffset, Windows extends FLL
     * instead of clipping coarse integration.
     */
    frame_length = E003I_IMX681_DEFAULT_FLL;
    if (line_count > E003I_IMX681_DEFAULT_FLL -
                     E003I_IMX681_VERT_OFFSET -
                     E003I_IMX681_EXTRA_OFFSET)
        frame_length = line_count + E003I_IMX681_VERT_OFFSET +
                       E003I_IMX681_EXTRA_OFFSET;

    memset(out, 0, sizeof(*out));
    out->line_count_before_even = line_count;
    out->frame_length_lines = frame_length;
    out->vertical_blanking = frame_length - E003I_IMX681_HEIGHT;

    /* Active IMX681 FillExposureSettings clears coarse-integration bit 0. */
    out->exposure_lines = line_count & ~1U;

    e003i_imx681_gain_codes(in->gain,
                            &out->analogue_gain_code,
                            &out->digital_gain_code,
                            &out->isp_gain);
    return 0;
}
