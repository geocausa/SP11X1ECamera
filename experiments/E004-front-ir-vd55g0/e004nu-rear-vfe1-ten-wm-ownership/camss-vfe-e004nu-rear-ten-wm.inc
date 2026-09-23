/* SPDX-License-Identifier: GPL-2.0-only
 * E004nu: source-pinned 10-client rear-only VFE1 BUS target and
 * candidate per-client frame ownership. Two distinct OEM Windows rear
 * LIVE capture phases show identical static WM0/1/2/3/11/12/13/14/16/18.
 *
 * The active front E003i BUS recipe has only NINE WMs and is NOT
 * suitable for rear: WM16 BAF must have its own DMA and completion.
 * Everything below is SOURCE-ONLY compiled and UNCALLED. It must NEVER
 * be armed until a source-backed WM16 event/retire, all 10 allocations,
 * rear RT-CDM/IQ, front/rear core exclusion and Golden rollback exist.
 */
#ifndef VFE680_E004NU_REAR_TEN_WM_INC
#define VFE680_E004NU_REAR_TEN_WM_INC

#define VFE680_E004NU_REAR_CLIENTS	10U
#define VFE680_E004NU_REAR_CLIENTS_MASK	0x03ffU
#define VFE680_E004NU_REAR_WM16_BAF	16U

struct vfe680_e004nu_rear_wm_static {
	u8 wm;
	u32 cfg;
	u32 frame_incr;
	u32 image_cfg0;
	u32 image_cfg1;
	u32 image_cfg2;
	u32 packer;
	u32 bw_limit;
	u32 irq_subsample_period;
	u32 irq_subsample_pattern;
	u32 frame_drop_period;
	u32 frame_drop_pattern;
	u32 meta_cfg;
	u32 mode_cfg;
	u32 stats_ctrl;
	u32 ctrl2;
	u32 loss0;
	u32 loss1;
};

/* E004nr WM-RESULT.json; no dynamic image or metadata DMA addresses. */
static const struct vfe680_e004nu_rear_wm_static
vfe680_e004nu_rear_wm_contract[VFE680_E004NU_REAR_CLIENTS] __used = {
	{ .wm = 0, .cfg = 0x00000011U, .frame_incr = 0x00a9d000U, .image_cfg0 = 0x08700f00U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00001400U, .packer = 0x0000000bU, .bw_limit = 0x0000000bU, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000800U, .mode_cfg = 0x00000023U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000001U, .loss0 = 0x06210022U, .loss1 = 0x0000040aU },
	{ .wm = 1, .cfg = 0x00000011U, .frame_incr = 0x00559000U, .image_cfg0 = 0x04380f00U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00001400U, .packer = 0x0000000bU, .bw_limit = 0x0000000bU, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000800U, .mode_cfg = 0x00000033U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000001U, .loss0 = 0x06210022U, .loss1 = 0x0000040aU },
	{ .wm = 2, .cfg = 0x00000011U, .frame_incr = 0x0010e000U, .image_cfg0 = 0x010e01e0U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000f00U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 3, .cfg = 0x00000011U, .frame_incr = 0x00018000U, .image_cfg0 = 0x00440078U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000400U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 11, .cfg = 0x00010001U, .frame_incr = 0x000a0000U, .image_cfg0 = 0x00000000U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000001U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 12, .cfg = 0x00010001U, .frame_incr = 0x00001800U, .image_cfg0 = 0x00000000U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000001U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 13, .cfg = 0x00010001U, .frame_incr = 0x00048000U, .image_cfg0 = 0x00000000U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000001U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 14, .cfg = 0x00010001U, .frame_incr = 0x00151800U, .image_cfg0 = 0x00000000U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000001U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 16, .cfg = 0x00020001U, .frame_incr = 0x00002d00U, .image_cfg0 = 0x00190004U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000020U, .packer = 0x0000000aU, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
	{ .wm = 18, .cfg = 0x00010001U, .frame_incr = 0x00010000U, .image_cfg0 = 0x00000000U, .image_cfg1 = 0x00000000U, .image_cfg2 = 0x00000001U, .packer = 0x00000008U, .bw_limit = 0x00000000U, .irq_subsample_period = 0x00000000U, .irq_subsample_pattern = 0x00000001U, .frame_drop_period = 0x00000000U, .frame_drop_pattern = 0x00000001U, .meta_cfg = 0x00000000U, .mode_cfg = 0x00000000U, .stats_ctrl = 0x00000000U, .ctrl2 = 0x00000000U, .loss0 = 0x00000000U, .loss1 = 0x00000000U },
};

static_assert(ARRAY_SIZE(vfe680_e004nu_rear_wm_contract) == 10U);
static_assert(VFE680_E004NU_REAR_CLIENTS_MASK ==
	      ((1U << VFE680_E004NU_REAR_CLIENTS) - 1U));

static bool __used
vfe680_e004nu_rear_wm_contract_valid(void)
{
	const struct vfe680_e004nu_rear_wm_static *y =
		&vfe680_e004nu_rear_wm_contract[0];
	const struct vfe680_e004nu_rear_wm_static *c =
		&vfe680_e004nu_rear_wm_contract[1];
	unsigned int i;

	if (y->wm != 0 || c->wm != 1 ||
	    y->cfg != 0x11U || c->cfg != 0x11U ||
	    y->frame_incr != VFE680_E004NT_REAR_Y_FRAME_INCR ||
	    c->frame_incr != VFE680_E004NT_REAR_C_FRAME_INCR ||
	    y->image_cfg0 != (2160U << 16 | 3840U) ||
	    c->image_cfg0 != (1080U << 16 | 3840U) ||
	    y->image_cfg2 != VFE680_E004NT_REAR_WM_STRIDE ||
	    c->image_cfg2 != VFE680_E004NT_REAR_WM_STRIDE ||
	    y->packer != VFE680_E004NT_REAR_FULL_PACKER_CFG ||
	    c->packer != VFE680_E004NT_REAR_FULL_PACKER_CFG ||
	    y->meta_cfg != VFE680_E004NT_REAR_FULL_META_CFG ||
	    c->meta_cfg != VFE680_E004NT_REAR_FULL_META_CFG ||
	    vfe680_e004nu_rear_wm_contract[8].wm !=
			VFE680_E004NU_REAR_WM16_BAF ||
	    vfe680_e004nu_rear_wm_contract[8].cfg != 0x00020001U ||
	    vfe680_e004nu_rear_wm_contract[8].frame_incr != 0x2d00U)
		return false;
	for (i = 0; i < ARRAY_SIZE(vfe680_e004nu_rear_wm_contract); i++) {
		const struct vfe680_e004nu_rear_wm_static *wm =
			&vfe680_e004nu_rear_wm_contract[i];

		if (!(wm->cfg & VFE_BUS_WRITE_CLIENT_CFG_EN) ||
		    !wm->frame_incr ||
		    (i && wm->wm <= vfe680_e004nu_rear_wm_contract[i - 1].wm))
			return false;
	}

	return true;
}

/* CONFIGURATION ONLY: checks all ten existing client enable bits FIRST,
 * before any write. Writes each configured client disabled, with no
 * dynamic image/meta address and no WM enable. Do not call from front
 * stream; no caller is installed into the isolated module.
 */
static int __used
vfe680_e004nu_rear_wm_prepare_disabled(struct vfe_device *vfe)
{
	unsigned int i;

	if (!vfe680_e004nt_rear_4k_target(vfe) ||
	    !vfe680_e004nu_rear_wm_contract_valid() ||
	    !vfe->base)
		return -EINVAL;
	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe,
				       vfe680_e004nu_rear_wm_contract[i].wm, 0);

		if (readl_relaxed(cfg + VFE680_X1E_BUS_CFG) &
		    VFE_BUS_WRITE_CLIENT_CFG_EN)
			return -EBUSY;
	}
	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		const struct vfe680_e004nu_rear_wm_static *c =
			&vfe680_e004nu_rear_wm_contract[i];
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe, c->wm, 0);

		/* Never enable a WM or set its image/meta address here. */
		writel_relaxed(c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN,
			       cfg + VFE680_X1E_BUS_CFG);
	writel_relaxed(c->cfg, cfg + VFE680_X1E_BUS_CFG);
	writel_relaxed(c->frame_incr, cfg + VFE680_X1E_BUS_FRAME_INCR);
	writel_relaxed(c->image_cfg0, cfg + VFE680_X1E_BUS_IMAGE_CFG0);
	writel_relaxed(c->image_cfg1, cfg + VFE680_X1E_BUS_IMAGE_CFG1);
	writel_relaxed(c->image_cfg2, cfg + VFE680_X1E_BUS_IMAGE_CFG2);
	writel_relaxed(c->packer, cfg + VFE680_X1E_BUS_PACKER_CFG);
	writel_relaxed(c->bw_limit, cfg + VFE680_X1E_BUS_BW_LIMIT);
	writel_relaxed(c->irq_subsample_period, cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD);
	writel_relaxed(c->irq_subsample_pattern, cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN);
	writel_relaxed(c->frame_drop_period, cfg + VFE680_X1E_BUS_FRAMEDROP_PERIOD);
	writel_relaxed(c->frame_drop_pattern, cfg + VFE680_X1E_BUS_FRAMEDROP_PATTERN);
	writel_relaxed(c->meta_cfg, cfg + VFE680_X1E_BUS_META_CFG);
	writel_relaxed(c->mode_cfg, cfg + VFE680_X1E_BUS_MODE_CFG);
	writel_relaxed(c->stats_ctrl, cfg + VFE680_X1E_BUS_STATS_CTRL);
	writel_relaxed(c->ctrl2, cfg + VFE680_X1E_BUS_CTRL_2);
	writel_relaxed(c->loss0, cfg + VFE680_X1E_BUS_LOSSY_THRESH0);
	writel_relaxed(c->loss1, cfg + VFE680_X1E_BUS_LOSSY_THRESH1);
	}
	return 0;
}

/* A per-client candidate pending mask; NO unknown group event is
 * mapped to an individual WM. WM16 BAF and WM0/1 video cannot be
 * treated as retired merely because a front-style VIDEO IRQ arrives.
 */
struct vfe680_e004nu_rear_frame {
	struct vfe680_e004nt_rear_surface *surface;
	u16 pending;
	bool active;
};

static int __used
vfe680_e004nu_rear_frame_begin(struct vfe_device *vfe,
			       struct vfe680_e004nu_rear_frame *frame,
			       struct vfe680_e004nt_rear_surface *surface)
{
	struct vfe680_e004nt_rear_wm_addrs candidate;
	int ret;

	if (!frame || !surface || frame->active || frame->pending ||
	    frame->surface || surface->in_flight)
		return -EBUSY;
	ret = vfe680_e004nt_rear_surface_addrs(vfe, surface, &candidate);
	if (ret)
		return ret;

	surface->in_flight = true;
	frame->surface = surface;
	frame->pending = VFE680_E004NU_REAR_CLIENTS_MASK;
	frame->active = true;
	return 0;
}

static int __used
vfe680_e004nu_rear_frame_ack_wm(struct vfe680_e004nu_rear_frame *frame,
				u8 verified_wm)
{
	unsigned int i;

	if (!frame || !frame->active || !frame->surface ||
	    !frame->surface->in_flight)
		return -EINVAL;
	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		if (vfe680_e004nu_rear_wm_contract[i].wm == verified_wm) {
			if (!(frame->pending & BIT(i)))
				return -EALREADY;
			frame->pending &= ~BIT(i);
			return 0;
		}
	}
	return -EINVAL; /* including unknown WM completion IDs */
}

/* NO free/rebind on an incomplete frame. Even after all ten WMs, the
 * future owner must independently prove MMIO BUS disabled and IRQ
 * retirement and then pass stopped=true from the source-backed path.
 * This is NOT a substitute for actually stopping the hardware.
 */
static int __used
vfe680_e004nu_rear_frame_retire(struct vfe680_e004nu_rear_frame *frame,
				bool independently_verified_bus_stopped)
{
	if (!frame || !frame->active || !frame->surface ||
	    !frame->surface->in_flight)
		return -EINVAL;
	if (frame->pending || !independently_verified_bus_stopped)
		return -EBUSY;

	frame->surface->in_flight = false;
	memset(frame, 0, sizeof(*frame));
	return 0;
}

static int __used
vfe680_e004nu_rear_wm_runtime_authorization(struct vfe_device *vfe)
{
	if (!vfe680_e004nt_rear_4k_target(vfe) ||
	    !vfe680_e004nu_rear_wm_contract_valid())
		return -EINVAL;
	return -EOPNOTSUPP;
}
#endif /* VFE680_E004NU_REAR_TEN_WM_INC */
