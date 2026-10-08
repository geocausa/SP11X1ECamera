/* SPDX-License-Identifier: GPL-2.0-only */
/* Diagnostic admission only: default rear runtime remains denied. The caller
 * owns REAR/PM and allocated spans; no compression transition is supported.
 * Never write FULL metadata, UBWC mode/control/loss registers or addresses.
 */
static int native_rear_nv12_cold_admit(struct vfe_device *vfe)
{
 unsigned int i;
 if (!vfe680_e004nt_rear_4k_target(vfe) || !vfe->base)
  return -EINVAL;
 for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++)
  if (readl(vfe680_x1e_bus_reg(vfe, vfe680_e004nu_rear_wm_contract[i].wm, 0)) &
      VFE_BUS_WRITE_CLIENT_CFG_EN)
   return -EBUSY;
 for (i = 0; i < 2; i++)
  if (readl(vfe680_x1e_bus_reg(vfe, i, VFE680_X1E_BUS_MODE_CFG)) & BIT(0))
   return -EOPNOTSUPP;
 return 0;
}

static void native_rear_nv12_write_full_disabled(struct vfe_device *vfe, unsigned int wm)
{
 void __iomem *cfg = vfe680_x1e_bus_reg(vfe, wm, 0);
 u32 rows = wm ? NATIVE_REAR_NV12_HEIGHT / 2U : NATIVE_REAR_NV12_HEIGHT;
 writel_relaxed(0, cfg + VFE680_X1E_BUS_CFG);
 writel_relaxed(0, cfg + VFE680_X1E_BUS_BW_LIMIT);
 writel_relaxed((rows << 16) | NATIVE_REAR_NV12_WIDTH, cfg + VFE680_X1E_BUS_IMAGE_CFG0);
 writel_relaxed(0, cfg + VFE680_X1E_BUS_IMAGE_CFG1);
 writel_relaxed(NATIVE_REAR_NV12_STRIDE, cfg + VFE680_X1E_BUS_IMAGE_CFG2);
 writel_relaxed(NATIVE_REAR_NV12_PACKER, cfg + VFE680_X1E_BUS_PACKER_CFG);
 writel_relaxed(rows * NATIVE_REAR_NV12_STRIDE, cfg + VFE680_X1E_BUS_FRAME_INCR);
 writel_relaxed(0, cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD);
 writel_relaxed(1, cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN);
 writel_relaxed(0, cfg + VFE680_X1E_BUS_FRAMEDROP_PERIOD);
 writel_relaxed(1, cfg + VFE680_X1E_BUS_FRAMEDROP_PATTERN);
}

static int native_rear_nv12_full_readback(struct vfe_device *vfe)
{
 unsigned int wm, word;
 for (wm = 0; wm < 2; wm++) {
  void __iomem *cfg = vfe680_x1e_bus_reg(vfe, wm, 0);
  u32 rows = wm ? NATIVE_REAR_NV12_HEIGHT / 2U : NATIVE_REAR_NV12_HEIGHT;
  struct e006p_output_path path = { .bit_width = 8, .enabled = true };
  u32 base = wm ? 0x9e60 : 0x9c60;
  if (readl(cfg + VFE680_X1E_BUS_CFG) != 0 ||
      (readl(cfg + VFE680_X1E_BUS_MODE_CFG) & BIT(0)) ||
      readl(cfg + VFE680_X1E_BUS_BW_LIMIT) != 0 ||
      readl(cfg + VFE680_X1E_BUS_IMAGE_CFG0) != ((rows << 16) | NATIVE_REAR_NV12_WIDTH) ||
      readl(cfg + VFE680_X1E_BUS_IMAGE_CFG1) != 0 ||
      readl(cfg + VFE680_X1E_BUS_IMAGE_CFG2) != NATIVE_REAR_NV12_STRIDE ||
      readl(cfg + VFE680_X1E_BUS_PACKER_CFG) != NATIVE_REAR_NV12_PACKER ||
      readl(cfg + VFE680_X1E_BUS_FRAME_INCR) != rows * NATIVE_REAR_NV12_STRIDE ||
      readl(cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD) != 0 ||
      readl(cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN) != 1 ||
      readl(cfg + VFE680_X1E_BUS_FRAMEDROP_PERIOD) != 0 ||
      readl(cfg + VFE680_X1E_BUS_FRAMEDROP_PATTERN) != 1)
   return -EIO;
  for (word = 0; word <= 10; word++) {
   u32 expected, reg = word ? base + 0x10 + (word - 1) * 4 : base;
   int ret = e006p_roundclamp_word(&path, wm != 0, word, &expected);
   if (ret)
    return ret;
   if (readl(vfe->base + reg) != expected)
    return -EIO;
  }
 }
 return 0;
}
