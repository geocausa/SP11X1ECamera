/* SPDX-License-Identifier: MIT */
/* Offline AF-to-BF handoff for one normal rear startup request. */
#ifndef E009C_AF_REQUEST_ROI_HANDOFF_H
#define E009C_AF_REQUEST_ROI_HANDOFF_H
#include "../e008x-rear-af-bf-roi-map/af-bf-roi-map.h"
#include "../e008z-rear-af-default-rectangle/af-default-rectangle.h"

/* The caller must supply the rectangle selected by AF for THIS request.
 * The interior BAF branch is modeled; unsupported clamps fail closed.
 * Packet 0 is the separate IFENode hardcode policy.
 */
static int e009c_rear_apply_af_rect(struct e008o_rear_bootstrap *state,
                                    unsigned int packet,
                                    uint32_t camif_width,
                                    uint32_t camif_height,
                                    const struct e008z_af_rect *af)
{
    struct e008x_rect baf;
    struct e008x_roi mapped[25];
    struct e007e_bf_dmi_state *d;
    unsigned int i;

    if (!state || !state->initialized || !af || packet < 1 || packet > 3 ||
        camif_width < 88 || camif_height < 80 ||
        camif_width > 8192 || camif_height > 16384 ||
        !af->width || !af->height ||
        (uint32_t)af->x + af->width > camif_width ||
        (uint32_t)af->y + af->height > camif_height)
        return -1;
    d = e008t_rear_bf_dmi(&state->packet[packet].dmi);
    if (!d || d->roi_count != 25 || !d->gamma_valid ||
        state->packet[packet].consumed)
        return -1;
    baf.x = af->x & ~1U;
    baf.y = af->y & ~1U;
    baf.width = af->width & ~1U;
    baf.height = (af->height & ~1U) + 5U + 11U;
    if (baf.x < 76 || baf.y < 64 ||
        baf.x + baf.width > camif_width - 12 ||
        baf.y + baf.height > camif_height ||
        e008x_normal_roi_map(baf, mapped))
        return -1;
    for (i = 0; i < 25; i++) {
        d->roi[i].left = mapped[i].left;
        d->roi[i].top = mapped[i].top;
        d->roi[i].width = mapped[i].width;
        d->roi[i].height = mapped[i].height;
    }
    return 0;
}
#endif
