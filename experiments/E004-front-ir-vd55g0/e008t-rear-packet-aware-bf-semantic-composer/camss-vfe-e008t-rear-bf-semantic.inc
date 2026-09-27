/* SPDX-License-Identifier: MIT */
/*
 * E008t rear packet-aware BF semantic composer.
 *
 * Generated only from the pinned DeviceMFT and rear tuning sources.
 * No captured Windows register words or DMI payload bytes are embedded.
 *
 * Scope: populate the BF semantic seed inside E008o's already-isolated
 * per-packet states. BFStats25 ROI validation/adjustment and final DMI parity
 * remain a later gate. No runtime caller is introduced here.
 */

#define E008T_REAR_STARTUP_PACKETS 4
#define E008T_REAR_GRID_COUNT 5

static const u16 e008t_normal_gamma[] = { 0, 512, 1024, 1536, 2048, 2560, 3072, 3584, 4096, 4608, 5120, 5632, 6144, 6656, 7168, 7680, 8192, 8704, 9216, 9728, 10240, 10752, 11264, 11776, 12288, 12800, 13312, 13824, 14336, 14848, 15360, 15872 };
static const s16 e008t_normal_iir_a[] = { 2009, 0, -2009, -5513, 22353, -12367, 5513, 0, 14297, -11289 };
static const s16 e008t_normal_iir_b[] = { 2009, 0, -2009, 22353, -12367, 5513, 0, -5513, 14297, -11289 };
static const u8 e008t_normal_coring_lanes[] = { 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 4, 5, 7, 9, 11, 13, 16 };
static const s8 e008t_hardcode_fir[] = { -1, -2, -1, 1, 5, 8, 10, 8, 5, 1, -1, -2, -1 };
static const s16 e008t_hardcode_iir_a[] = { 1513, 0, -1513, -1851, 28052, -13358, 1851, 0, 30633, -14725 };
static const s16 e008t_hardcode_iir_b[] = { 14662, -29322, 14662, 29141, -13120, 1851, 0, -1851, 30633, -14725 };
static const u8 e008t_hardcode_coring_lanes[] = { 0, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16 };

#define E008T_NORMAL_CORING_SCALAR 200U
#define E008T_HARDCODE_CORING_SCALAR 65536U

static struct e007e_bf_dmi_state *
e008t_rear_bf_dmi(struct e007v_rear_dmi_state *s)
{
    if (!s)
        return NULL;
    return &s->dmi.dmi.dmi.dmi.dmi.dmi.bfstats25;
}

static int
e008t_rear_seed_roi_common(struct e007e_bf_dmi_state *d,
                           u32 left, u32 top, u32 cell_w, u32 cell_h)
{
    unsigned int row, col, idx = 0;

    if (!d || !cell_w || !cell_h)
        return -EINVAL;
    if (cell_w - 1 > 0x0fff || cell_h - 1 > 0x1fff)
        return -ERANGE;

    for (row = 0; row < E008T_REAR_GRID_COUNT; row++) {
        for (col = 0; col < E008T_REAR_GRID_COUNT; col++) {
            struct e007e_bf_roi *r = &d->roi[idx];
            u32 x = left + col * cell_w;
            u32 y = top + row * cell_h;

            if (x > 0x1fff || y > 0x3fff)
                return -ERANGE;
            r->left = x;
            r->top = y;
            r->width = cell_w - 1;
            r->height = cell_h - 1;
            r->rid = idx;
            r->oid = idx;
            r->merge = false;
            r->type = false;
            idx++;
        }
    }
    d->roi_count = idx;
    return idx == E007E_BF_ROI_COUNT ? 0 : -EINVAL;
}

static int
e008t_rear_seed_packet0_roi(struct e007e_bf_dmi_state *d,
                            u32 camif_w, u32 camif_h)
{
    u32 cell_w, cell_h, left, top;

    if (!d || !camif_w || !camif_h)
        return -EINVAL;

    /* IFENode::hardcode BF ROI helper RVA 0x7637D8. */
    cell_w = ((camif_w * 25U) / 500U) & ~1U;
    cell_h = ((camif_h * 25U) / 500U) & ~1U;
    if (!cell_w || !cell_h ||
        camif_w < cell_w * E008T_REAR_GRID_COUNT ||
        camif_h < cell_h * E008T_REAR_GRID_COUNT)
        return -ERANGE;

    left = (camif_w - cell_w * E008T_REAR_GRID_COUNT) >> 1;
    top = (camif_h - cell_h * E008T_REAR_GRID_COUNT) >> 1;

    /* The hardcode helper forces each generated origin even. */
    left &= ~1U;
    top &= ~1U;
    return e008t_rear_seed_roi_common(d, left, top, cell_w, cell_h);
}

static int
e008t_rear_seed_normal_roi(struct e007e_bf_dmi_state *d,
                           u32 camif_w, u32 camif_h)
{
    u32 roi_w, roi_h, left, top, cell_w, cell_h;

    if (!d || !camif_w || !camif_h)
        return -EINVAL;

    /* AF default window = centered 25%; HAF grid = 5x5, zero overlap. */
    roi_w = camif_w / 4U;
    roi_h = camif_h / 4U;
    if (!roi_w || !roi_h)
        return -ERANGE;
    left = (camif_w - roi_w) >> 1;
    top = (camif_h - roi_h) >> 1;
    cell_w = roi_w / E008T_REAR_GRID_COUNT;
    cell_h = roi_h / E008T_REAR_GRID_COUNT;

    return e008t_rear_seed_roi_common(d, left, top, cell_w, cell_h);
}

static void
e008t_rear_seed_common_registers(struct e007b_bfstats25_calc_state *b,
                                 u8 packet)
{
    memset(b, 0, sizeof(*b));
    b->dmi_lut_bank = packet & 1;
    b->module_lut_bank = packet & 1;
    b->luma_select = 0;
    b->luma_conversion_enable = 0;
    b->scale_enable = 0;
}

static int
e008t_rear_seed_packet_bf(struct e008o_rear_packet_state *p,
                          u8 packet, u32 camif_w, u32 camif_h)
{
    struct e007b_bfstats25_calc_state *b;
    struct e007e_bf_dmi_state *d;
    int ret;

    if (!p || packet >= E008T_REAR_STARTUP_PACKETS)
        return -EINVAL;

    b = &p->regs.bfstats;
    d = e008t_rear_bf_dmi(&p->dmi);
    if (!d)
        return -EINVAL;

    e008t_rear_seed_common_registers(b, packet);
    memset(d, 0, sizeof(*d));

    if (packet == 0) {
        b->gamma_lut_enable = 0;
        b->filter0_enable = 1;
        b->filter1_enable = 1;
        b->filter3_enable = 1;
        memcpy(b->signed6, e008t_hardcode_fir, sizeof(b->signed6));
        memcpy(b->quant16_a, e008t_hardcode_iir_a, sizeof(b->quant16_a));
        memcpy(b->quant16_b, e008t_hardcode_iir_b, sizeof(b->quant16_b));
        b->signed4[0] = -3;
        b->signed4[1] = 0;
        b->tail_scalar17[0] = E008T_HARDCODE_CORING_SCALAR;
        b->tail_scalar17[1] = E008T_HARDCODE_CORING_SCALAR;
        memcpy(b->tail_lane5[0], e008t_hardcode_coring_lanes,
               sizeof(b->tail_lane5[0]));
        memcpy(b->tail_lane5[1], e008t_hardcode_coring_lanes,
               sizeof(b->tail_lane5[1]));
        d->gamma_valid = false;
        ret = e008t_rear_seed_packet0_roi(d, camif_w, camif_h);
    } else {
        b->gamma_lut_enable = 1;
        b->filter0_enable = 0;
        b->filter1_enable = 1;
        b->filter3_enable = 1;
        memcpy(b->quant16_a, e008t_normal_iir_a, sizeof(b->quant16_a));
        memcpy(b->quant16_b, e008t_normal_iir_b, sizeof(b->quant16_b));
        b->signed4[0] = 3;
        b->signed4[1] = 3;
        b->tail_scalar17[0] = E008T_NORMAL_CORING_SCALAR;
        b->tail_scalar17[1] = E008T_NORMAL_CORING_SCALAR;
        memcpy(b->tail_lane5[0], e008t_normal_coring_lanes,
               sizeof(b->tail_lane5[0]));
        memcpy(b->tail_lane5[1], e008t_normal_coring_lanes,
               sizeof(b->tail_lane5[1]));
        memcpy(d->gamma, e008t_normal_gamma, sizeof(d->gamma));
        d->gamma_valid = true;
        ret = e008t_rear_seed_normal_roi(d, camif_w, camif_h);
    }

    if (ret)
        return ret;
    return e007b_bfstats25_validate(b);
}

static int
e008t_rear_seed_bootstrap_bf(struct e008o_rear_bootstrap *s,
                             u32 camif_w, u32 camif_h)
{
    unsigned int packet;
    int ret;

    if (!s || !s->initialized || s->next_packet)
        return -EINVAL;

    for (packet = 0; packet < E008T_REAR_STARTUP_PACKETS; packet++) {
        ret = e008t_rear_seed_packet_bf(&s->packet[packet], packet,
                                        camif_w, camif_h);
        if (ret)
            return ret;
    }
    return 0;
}

struct e008t_rear_bf_semantic_static_ops {
    int (*seed)(struct e008o_rear_bootstrap *s, u32 camif_w, u32 camif_h);
};

static const struct e008t_rear_bf_semantic_static_ops
e008t_rear_bf_semantic_recipe __used = {
    .seed = e008t_rear_seed_bootstrap_bf,
};
