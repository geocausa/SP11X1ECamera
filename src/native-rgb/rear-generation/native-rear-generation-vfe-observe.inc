/* SPDX-License-Identifier: GPL-2.0-only */
/* Candidate-only common VFE register reads; no DMA address/content reads. */
static void native_rear_generation_vfe_snapshot(struct vfe_device *vfe,const char *phase)
{
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_GENERATION_VFE phase=%s core0=%08x core1=%08x top_mask=%08x/%08x top_status=%08x/%08x bus_mask=%08x/%08x bus_status=%08x/%08x ubwc=%08x violation=%08x overflow=%08x image_violation=%08x\n",
  phase,readl(vfe->base+VFE680_X1E_SP11_DAL_CORE_CFG0),readl(vfe->base+VFE680_X1E_SP11_DAL_CORE_CFG1),
  readl(vfe->base+VFE_TOP_IRQn_MASK(vfe,0)),readl(vfe->base+VFE_TOP_IRQn_MASK(vfe,1)),
  readl(vfe->base+VFE_TOP_IRQn_STATUS(vfe,0)),readl(vfe->base+VFE_TOP_IRQn_STATUS(vfe,1)),
  readl(vfe->base+VFE_BUS_IRQn_MASK(vfe,0)),readl(vfe->base+VFE_BUS_IRQn_MASK(vfe,1)),
  readl(vfe->base+VFE_BUS_IRQn_STATUS(vfe,0)),readl(vfe->base+VFE_BUS_IRQn_STATUS(vfe,1)),
  readl(vfe->base+VFE680_X1E_BUS_UBWC_STATIC_CTRL),readl(vfe->base+VFE_BUS_WR_VIOLATION_STATUS(vfe)),
  readl(vfe->base+VFE_BUS_WR_OVERFLOW_STATUS(vfe)),readl(vfe->base+VFE_BUS_WR_IMAGE_VIOLATION_STATUS(vfe)));
}
