/* Authored decoder for the bounded whole-frame RS metadata-input contract.
 * This decodes an incoming record; it does not implement the upstream AFD
 * algorithm or authorize hardware. Missing or unsupported inputs never use
 * a guessed default. All arithmetic remains in the existing E011AM producer.
 */
#ifndef E011DK_NORMAL_RS_INPUT_H
#define E011DK_NORMAL_RS_INPUT_H
#include <stddef.h>
#include "../e011am-rear-rs-full-startup-integration/rs-producer.h"

struct e011dk_whole_frame_crop { uint32_t left, top, right, bottom; };
static uint32_t e011dk_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static int e011dk_overlap(const void *a, size_t an, const void *b, size_t bn)
{
    uintptr_t x=(uintptr_t)a, y=(uintptr_t)b;
    return x<=y ? y-x<an : x-y<bn;
}
static int e011dk_decode_rs_input(
    const uint8_t *record, size_t bytes,
    const struct e011dk_whole_frame_crop *crop, uint32_t half_width,
    struct e011am_rs_input *out)
{
    struct e011am_rs_input candidate;
    struct e011am_rs_output checked;
    int ret;
    if (!record || !crop || !out || bytes != 132)
        return -EINVAL;
    if (e011dk_overlap(out,sizeof(*out),record,bytes) ||
        e011dk_overlap(out,sizeof(*out),crop,sizeof(*crop)))
        return -EINVAL;
    if (crop->left || crop->top ||
        e011dk_le32(record + 8) || e011dk_le32(record + 12))
        return -EOPNOTSUPP;
    if (crop->right == UINT32_MAX || crop->bottom == UINT32_MAX ||
        crop->right < crop->left || crop->bottom < crop->top)
        return -ERANGE;
    candidate = (struct e011am_rs_input) {
        .crop_width = crop->right - crop->left + 1,
        .crop_height = crop->bottom - crop->top + 1,
        .h_num = e011dk_le32(record),
        .v_num = e011dk_le32(record + 4),
        .half_width = half_width,
        .color_conversion = e011dk_le32(record + 128),
    };
    ret = e011am_produce_rs(&candidate, &checked);
    if (ret)
        return ret;
    *out = candidate;
    return 0;
}
#endif
