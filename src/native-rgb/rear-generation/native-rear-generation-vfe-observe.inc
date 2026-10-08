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

 /* Sizes, formats and counters only; never image/meta addresses or contents. */
 for (unsigned int wm = 0; wm < 4; wm++) {
  void __iomem *cfg = vfe680_x1e_bus_reg(vfe, wm, 0);
  dev_info(vfe->camss->dev,
   "NATIVE_REAR_GENERATION_WM phase=%s wm=%u cfg=%08x incr=%08x image0=%08x image1=%08x stride=%08x packer=%08x meta_cfg=%08x mode=%08x ctrl2=%08x debug0=%08x debug1=%08x\n",
   phase, wm, readl(cfg+VFE680_X1E_BUS_CFG),readl(cfg+VFE680_X1E_BUS_FRAME_INCR),
   readl(cfg+VFE680_X1E_BUS_IMAGE_CFG0),readl(cfg+VFE680_X1E_BUS_IMAGE_CFG1),
   readl(cfg+VFE680_X1E_BUS_IMAGE_CFG2),readl(cfg+VFE680_X1E_BUS_PACKER_CFG),
   readl(cfg+VFE680_X1E_BUS_META_CFG),readl(cfg+VFE680_X1E_BUS_MODE_CFG),
   readl(cfg+VFE680_X1E_BUS_CTRL_2),readl(cfg+VFE680_X1E_BUS_DEBUG_STATUS0),
   readl(cfg+VFE680_X1E_BUS_DEBUG_STATUS1));
 }
 for (unsigned int offset = 0x9860; offset <= 0x9884; offset += 4)
  dev_info(vfe->camss->dev,
   "NATIVE_REAR_GENERATION_MNDS phase=%s offset=%04x value=%08x\n",
   phase, offset, readl(vfe->base+offset));
}
