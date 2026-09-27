/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008d: build-only Linux-owned rear ten-WM DMA/address provider.
 *
 * This supersedes the unusable E004nu "prepare_disabled" implementation:
 * E004nu's historical helper accidentally contains a second enabled CFG write.
 * E008d never calls it. All ten WMs must be disabled before E008d writes any
 * static or dynamic register, and they remain disabled on successful return.
 *
 * No runtime call site and no WM enable are provided here.
 */
#ifndef VFE680_E008D_REAR_TEN_WM_DMA_ADDR_INC
#define VFE680_E008D_REAR_TEN_WM_DMA_ADDR_INC

#define E008D_REAR_AUX_COUNT 8

struct e008d_rear_aux_buffer {
	void *cpu;
	dma_addr_t dma;
	size_t size;
	u8 wm;
};

struct e008d_rear_dma_set {
	struct vfe680_e004nt_rear_surface full;
	struct e008d_rear_aux_buffer aux[E008D_REAR_AUX_COUNT];
	bool allocated;
	bool prepared_disabled;
};

struct e008d_rear_addresses {
	u8 wm[VFE680_E004NU_REAR_CLIENTS];
	u32 image[VFE680_E004NU_REAR_CLIENTS];
	u32 full_meta[2];
};

static const u8 e008d_rear_aux_wms[E008D_REAR_AUX_COUNT] = {
	2, 3, 11, 12, 13, 14, 16, 18,
};

static const struct vfe680_e004nu_rear_wm_static *
e008d_rear_contract_for_wm(u8 wm)
{
	unsigned int i;

	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++)
		if (vfe680_e004nu_rear_wm_contract[i].wm == wm)
			return &vfe680_e004nu_rear_wm_contract[i];
	return NULL;
}

static struct e008d_rear_aux_buffer *
e008d_rear_aux_for_wm(struct e008d_rear_dma_set *set, u8 wm)
{
	unsigned int i;

	for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
		if (set->aux[i].wm == wm)
			return &set->aux[i];
	return NULL;
}

static void
e008d_rear_aux_release(struct vfe_device *vfe,
		       struct e008d_rear_aux_buffer *aux)
{
	if (!aux->cpu)
		return;

	memset(aux->cpu, 0, aux->size);
	dma_free_coherent(vfe->camss->dev, aux->size, aux->cpu, aux->dma);
	memset(aux, 0, sizeof(*aux));
}

static void
e008d_rear_release_partial(struct vfe_device *vfe,
			   struct e008d_rear_dma_set *set)
{
	unsigned int i;

	for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
		e008d_rear_aux_release(vfe, &set->aux[i]);
	if (set->full.cpu)
		(void)vfe680_e004nt_rear_surface_free(vfe, &set->full);
	memset(set, 0, sizeof(*set));
}

static int __used
e008d_rear_dma_alloc(struct vfe_device *vfe, struct e008d_rear_dma_set *set)
{
	unsigned int i;
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !set ||
	    !vfe680_e004nu_rear_wm_contract_valid())
		return -EINVAL;
	if (set->allocated || set->prepared_disabled || set->full.cpu)
		return -EBUSY;

	ret = vfe680_e004nt_rear_surface_alloc(vfe, &set->full);
	if (ret)
		return ret;

	for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {
		const struct vfe680_e004nu_rear_wm_static *c;
		struct e008d_rear_aux_buffer *aux = &set->aux[i];

		c = e008d_rear_contract_for_wm(e008d_rear_aux_wms[i]);
		if (!c || !c->frame_incr) {
			ret = -EINVAL;
			goto fail;
		}
		aux->wm = c->wm;
		aux->size = c->frame_incr;
		aux->cpu = dma_alloc_coherent(vfe->camss->dev, aux->size,
					      &aux->dma, GFP_KERNEL);
		if (!aux->cpu) {
			ret = -ENOMEM;
			goto fail;
		}
		if (!vfe680_x1e_dma_span_32bit(aux->dma, aux->size)) {
			ret = -ERANGE;
			goto fail;
		}
		memset(aux->cpu, 0, aux->size);
	}

	set->allocated = true;
	return 0;

fail:
	e008d_rear_release_partial(vfe, set);
	return ret;
}

static int
e008d_rear_build_addresses(struct vfe_device *vfe,
			   struct e008d_rear_dma_set *set,
			   struct e008d_rear_addresses *out)
{
	struct vfe680_e004nt_rear_wm_addrs full;
	unsigned int i;
	int ret;

	if (!vfe || !set || !out || !set->allocated)
		return -EINVAL;

	ret = vfe680_e004nt_rear_surface_addrs(vfe, &set->full, &full);
	if (ret)
		return ret;
	memset(out, 0, sizeof(*out));

	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		const struct vfe680_e004nu_rear_wm_static *c =
			&vfe680_e004nu_rear_wm_contract[i];
		struct e008d_rear_aux_buffer *aux;

		out->wm[i] = c->wm;
		switch (c->wm) {
		case 0:
			out->image[i] = full.y_image;
			out->full_meta[0] = full.y_meta;
			break;
		case 1:
			out->image[i] = full.c_image;
			out->full_meta[1] = full.c_meta;
			break;
		default:
			aux = e008d_rear_aux_for_wm(set, c->wm);
			if (!aux || !aux->cpu || aux->dma > U32_MAX ||
			    aux->size != c->frame_incr)
				return -EINVAL;
			out->image[i] = (u32)aux->dma;
			break;
		}
		if (!out->image[i])
			return -ERANGE;
	}

	return 0;
}

static void
e008d_rear_write_static_disabled(
	struct vfe_device *vfe,
	const struct vfe680_e004nu_rear_wm_static *c)
{
	void __iomem *cfg = vfe680_x1e_bus_reg(vfe, c->wm, 0);

	/* There is intentionally NO later write of c->cfg with EN set. */
	writel_relaxed(c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN,
		       cfg + VFE680_X1E_BUS_CFG);
	writel_relaxed(c->frame_incr, cfg + VFE680_X1E_BUS_FRAME_INCR);
	writel_relaxed(c->image_cfg0, cfg + VFE680_X1E_BUS_IMAGE_CFG0);
	writel_relaxed(c->image_cfg1, cfg + VFE680_X1E_BUS_IMAGE_CFG1);
	writel_relaxed(c->image_cfg2, cfg + VFE680_X1E_BUS_IMAGE_CFG2);
	writel_relaxed(c->packer, cfg + VFE680_X1E_BUS_PACKER_CFG);
	writel_relaxed(c->bw_limit, cfg + VFE680_X1E_BUS_BW_LIMIT);
	writel_relaxed(c->irq_subsample_period,
		       cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD);
	writel_relaxed(c->irq_subsample_pattern,
		       cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN);
	writel_relaxed(c->frame_drop_period,
		       cfg + VFE680_X1E_BUS_FRAMEDROP_PERIOD);
	writel_relaxed(c->frame_drop_pattern,
		       cfg + VFE680_X1E_BUS_FRAMEDROP_PATTERN);
	writel_relaxed(c->meta_cfg, cfg + VFE680_X1E_BUS_META_CFG);
	writel_relaxed(c->mode_cfg, cfg + VFE680_X1E_BUS_MODE_CFG);
	writel_relaxed(c->stats_ctrl, cfg + VFE680_X1E_BUS_STATS_CTRL);
	writel_relaxed(c->ctrl2, cfg + VFE680_X1E_BUS_CTRL_2);
	writel_relaxed(c->loss0, cfg + VFE680_X1E_BUS_LOSSY_THRESH0);
	writel_relaxed(c->loss1, cfg + VFE680_X1E_BUS_LOSSY_THRESH1);
}

static int __used
e008d_rear_prepare_addresses_disabled(struct vfe_device *vfe,
				      struct e008d_rear_dma_set *set,
				      struct e008d_rear_addresses *out)
{
	struct e008d_rear_addresses addr;
	unsigned int i;
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !set || !out ||
	    !set->allocated || set->prepared_disabled)
		return -EINVAL;

	ret = e008d_rear_build_addresses(vfe, set, &addr);
	if (ret)
		return ret;

	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe, addr.wm[i], 0);

		if (readl_relaxed(cfg + VFE680_X1E_BUS_CFG) &
		    VFE_BUS_WRITE_CLIENT_CFG_EN)
			return -EBUSY;
	}

	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++)
		e008d_rear_write_static_disabled(
			vfe, &vfe680_e004nu_rear_wm_contract[i]);

	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe, addr.wm[i], 0);

		writel_relaxed(addr.image[i],
			       cfg + VFE680_X1E_BUS_IMAGE_ADDR);
		if (addr.wm[i] == 0)
			writel_relaxed(addr.full_meta[0],
				       cfg + VFE680_X1E_BUS_META_ADDR);
		else if (addr.wm[i] == 1)
			writel_relaxed(addr.full_meta[1],
				       cfg + VFE680_X1E_BUS_META_ADDR);
	}
	wmb();

	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++) {
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe, addr.wm[i], 0);

		if (readl_relaxed(cfg + VFE680_X1E_BUS_CFG) &
		    VFE_BUS_WRITE_CLIENT_CFG_EN)
			return -EIO;
		if (readl_relaxed(cfg + VFE680_X1E_BUS_IMAGE_ADDR) !=
		    addr.image[i])
			return -EIO;
		if (addr.wm[i] == 0 &&
		    readl_relaxed(cfg + VFE680_X1E_BUS_META_ADDR) !=
		    addr.full_meta[0])
			return -EIO;
		if (addr.wm[i] == 1 &&
		    readl_relaxed(cfg + VFE680_X1E_BUS_META_ADDR) !=
		    addr.full_meta[1])
			return -EIO;
	}

	set->prepared_disabled = true;
	*out = addr;
	return 0;
}

static int __used
e008d_rear_dma_free_unprepared(struct vfe_device *vfe,
			       struct e008d_rear_dma_set *set)
{
	if (!vfe680_e004nt_rear_4k_target(vfe) || !set || !set->allocated)
		return -EINVAL;
	if (set->prepared_disabled)
		return -EBUSY;

	e008d_rear_release_partial(vfe, set);
	return 0;
}

static int __used e008d_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

struct e008d_rear_dma_ops {
	int (*alloc)(struct vfe_device *, struct e008d_rear_dma_set *);
	int (*prepare_addresses_disabled)(struct vfe_device *,
					 struct e008d_rear_dma_set *,
					 struct e008d_rear_addresses *);
	int (*free_unprepared)(struct vfe_device *, struct e008d_rear_dma_set *);
};

static const struct e008d_rear_dma_ops e008d_rear_dma_recipe __used = {
	.alloc = e008d_rear_dma_alloc,
	.prepare_addresses_disabled = e008d_rear_prepare_addresses_disabled,
	.free_unprepared = e008d_rear_dma_free_unprepared,
};

#endif
