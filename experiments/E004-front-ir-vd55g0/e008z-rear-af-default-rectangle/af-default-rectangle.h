/* SPDX-License-Identifier: MIT */
/* Offline, parameterized default AF ROI source slice; no hardware call site. */
#ifndef E008Z_AF_DEFAULT_RECTANGLE_H
#define E008Z_AF_DEFAULT_RECTANGLE_H
#include <stdint.h>

struct e008z_af_default_inputs {
    uint16_t camif_width, camif_height;
    float width_fraction, height_fraction, mode_scale;
    float zoom, pd_width_scale, pd_height_scale;
    int alternate_mode, pd_scale_enabled, sparse_pd;
};
struct e008z_af_rect {
    uint16_t x, y, width, height;
};

/*
 * Pinned af_util_get_roi_default: CAMIF width/height, tune fractions and
 * inverse zoom feed truncating single-precision dimensions. An optional
 * policy gate applies separate PD scales. The selected PD mode imposes a
 * 400 or 200 minimum per axis, followed by centered halfword geometry.
 * The caller supplies all policy decisions; this helper cannot identify
 * which request selected them. Later af_util_adjust_roi and BAF clamps
 * are separate stages.
 */
static int e008z_af_default_rect(const struct e008z_af_default_inputs *in,
                                  struct e008z_af_rect *out)
{
    float inverse, width_f, height_f;
    uint32_t width, height, min_size;
    if (!in || !out || !in->camif_width || !in->camif_height ||
        !(in->zoom > 0.0f) || !(in->width_fraction > 0.0f) ||
        !(in->height_fraction > 0.0f) ||
        (in->alternate_mode && !(in->mode_scale > 0.0f)) ||
        (in->pd_scale_enabled && (!(in->pd_width_scale > 0.0f) ||
                                  !(in->pd_height_scale > 0.0f))))
        return -1;
    inverse = 1.0f / in->zoom;
    width_f = in->width_fraction;
    height_f = in->height_fraction;
    if (in->alternate_mode) {
        width_f *= in->mode_scale;
        height_f = in->mode_scale * height_f;
    }
    width_f = width_f * (float)in->camif_width * inverse;
    height_f = height_f * (float)in->camif_height * inverse;
    if (!(width_f >= 0.0f && width_f < 65536.0f &&
          height_f >= 0.0f && height_f < 65536.0f))
        return -1;
    width = (uint16_t)(uint32_t)width_f;
    height = (uint16_t)(uint32_t)height_f;
    if (in->pd_scale_enabled) {
        width_f = (float)width * in->pd_width_scale;
        height_f = (float)height * in->pd_height_scale;
        if (!(width_f >= 0.0f && width_f < 65536.0f &&
              height_f >= 0.0f && height_f < 65536.0f))
            return -1;
        width = (uint16_t)(uint32_t)width_f;
        height = (uint16_t)(uint32_t)height_f;
    }
    if (height > in->camif_height)
        height = in->camif_height;
    min_size = in->sparse_pd ? 400U : 200U;
    if (width < min_size) width = min_size;
    if (height < min_size) height = min_size;
    if (width > in->camif_width || height > in->camif_height)
        return -1; /* Outside the source slice's supported valid geometry. */
    out->width = (uint16_t)width;
    out->height = (uint16_t)height;
    out->x = (uint16_t)((in->camif_width >> 1) - (width >> 1));
    out->y = (uint16_t)((in->camif_height >> 1) - (height >> 1));
    return 0;
}
#endif
