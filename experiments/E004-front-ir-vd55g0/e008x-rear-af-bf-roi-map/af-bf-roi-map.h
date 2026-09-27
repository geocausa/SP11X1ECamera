/* SPDX-License-Identifier: MIT */
/* Offline source slice: normal 5x5 BAF map and BFStats25 valid ROI branch. */
#ifndef E008X_AF_BF_ROI_MAP_H
#define E008X_AF_BF_ROI_MAP_H
#include <stdint.h>

struct e008x_rect {
    uint32_t x, y, width, height;
};
struct e008x_roi {
    uint32_t left, top, width, height;
};

/*
 * BAFLogicDriver::MapROIConfigure uses single-precision window size
 * 1 / (5 - 4 * overlap). The selected tuning has zero overlap.
 * The input rectangle is caller-owned AF state, not the ISP output crop.
 *
 * BFStats25::ValidateAndAdjustROIBoundary then applies the valid,
 * non-clipping path. The early odd-left store is overwritten by the
 * final original-left store; top and even dimensions retain adjustment.
 * This does not model overlap correction, invalidation, scale or stripes.
 */
static int e008x_normal_roi_map(struct e008x_rect rect,
                                struct e008x_roi out[25])
{
    const float window = 1.0f / 5.0f;
    uint32_t cell_w, cell_h, row, col;

    if (!out || !rect.width || !rect.height ||
        rect.x > 8191 || rect.y > 16383 ||
        rect.width > 8192 || rect.height > 16384)
        return -1;
    cell_w = (uint32_t)((float)rect.width * window);
    cell_h = (uint32_t)((float)rect.height * window);
    if (cell_w < 6 || cell_h < 8)
        return -1;
    for (row = 0; row < 5; row++) {
        for (col = 0; col < 5; col++) {
            struct e008x_roi *r = &out[row * 5 + col];
            uint32_t left = rect.x + col * cell_w;
            uint32_t top = rect.y + row * cell_h;
            uint32_t width = cell_w - 1;
            uint32_t height = cell_h - 1;

            if (left + width > 8191 || top + height > 16383)
                return -1;
            r->left = left;
            r->top = top & ~1U;
            r->width = width - (!(width & 1U));
            r->height = height - (!(height & 1U));
        }
    }
    return 0;
}
#endif
