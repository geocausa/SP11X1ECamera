/* SPDX-License-Identifier: MIT */
/* Offline sensor/crop ratio hypothesis; upstream Windows producer unproven. */
#ifndef E009F_INITIAL_ZOOM_CANDIDATE_H
#define E009F_INITIAL_ZOOM_CANDIDATE_H
#include <stdint.h>
static int e009f_initial_zoom_candidate(uint32_t sensor_width,
                                         uint32_t camif_width, float *zoom)
{
    if (!zoom || !camif_width || !sensor_width ||
        camif_width > sensor_width || sensor_width > 8192)
        return -1;
    *zoom = (float)camif_width / (float)sensor_width;
    return 0;
}
#endif
