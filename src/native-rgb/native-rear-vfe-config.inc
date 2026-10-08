/* SPDX-License-Identifier: GPL-2.0-only */
/* Common IFE1 startup, before rear WM preload. Caller holds REAR owner and PM.
 * Existing source-qualified IFE1 core prefix is independent of front geometry.
 * All ten WMs must remain disabled; packet-owned IQ and dynamic addresses stay
 * untouched. The current rear FULL surface contract is QC10C compressed.
 */
static int native_rear_vfe_configure(struct vfe_device *vfe)
{
 unsigned int i;
 int ret;
 if (!vfe680_e004nt_rear_4k_target(vfe) || !vfe->base ||
     !vfe680_e004nu_rear_wm_contract_valid())
  return -EINVAL;
 for (i=0;i<VFE680_E004NU_REAR_CLIENTS;i++)
  if (readl(vfe680_x1e_bus_reg(vfe,vfe680_e004nu_rear_wm_contract[i].wm,0)) &
      VFE_BUS_WRITE_CLIENT_CFG_EN)
   return -EBUSY;
 ret=vfe680_x1e_pix_runtime_start_prefix(vfe);
 if (ret)
  return ret;
 writel(VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL,vfe->base+VFE680_X1E_BUS_UBWC_STATIC_CTRL);
 if (readl(vfe->base+VFE_TOP_IRQn_MASK(vfe,0))!=VFE680_X1E_WINDOWS_TOP_MASK0 ||
     readl(vfe->base+VFE_TOP_IRQn_MASK(vfe,1))!=0 ||
     readl(vfe->base+VFE_BUS_IRQn_MASK(vfe,1))!=0 ||
     readl(vfe->base+VFE680_X1E_SP11_DAL_CORE_CFG0)!=VFE680_X1E_SP11_DAL_CORE_CFG0_VALUE ||
     readl(vfe->base+VFE680_X1E_SP11_DAL_CORE_CFG1)!=VFE680_X1E_SP11_DAL_CORE_CFG1_VALUE ||
     readl(vfe->base+VFE_BUS_IRQn_MASK(vfe,0))!=VFE680_X1E_SP11_DAL_BUS_MASK0 ||
     readl(vfe->base+VFE680_X1E_BUS_UBWC_STATIC_CTRL)!=VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL)
  return -EIO;
 return 0;
}
