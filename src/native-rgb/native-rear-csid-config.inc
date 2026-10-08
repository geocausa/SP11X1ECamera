/* SPDX-License-Identifier: GPL-2.0-only */
/* Rear CSI transport configuration before RT-CDM packet0.
 * Lane routing and RAW10 decode are derived from the admitted Linux route.
 * Fixed transport policy uses the accepted rear mode0 register contract.
 * Crop/format-measure, IRQ subsampling, RUP/AUP and all IFE IQ stay owned by
 * the four packets. This does not replay the final-state E004ns prepare.
 * Caller holds exclusive rear ownership and media-pipeline PM after reset.
 */
#ifndef NATIVE_REAR_CSID_CONFIG_INC
#define NATIVE_REAR_CSID_CONFIG_INC
#include "camss-e008k-rear-bridge.h"

int csid680_native_rear_configure(struct csid_device *csid)
{
 const struct csid_format_info *format;
 const struct v4l2_mbus_framefmt *fmt;
 u32 rx_cfg0,cfg0;

 if (!csid_e004ns_rear_ipp_mode0(csid))
  return -EINVAL;
 fmt=&csid->fmt[MSM_CSID_PAD_PIX];
 format=csid_get_fmt_entry(csid->res->formats->formats,
                          csid->res->formats->nformats,fmt->code);
 if (!format)
  return -EINVAL;
 rx_cfg0=csid_e004ns_rear_rx_cfg0(csid);
 cfg0=(format->decode_format << IPP_CFG0_DECODE_FORMAT) |
      (format->data_type << IPP_CFG0_DATA_TYPE) | IPP_CFG0_ENABLE;
 if (rx_cfg0!=CSID_E004NS_REAR_RX_CFG0 ||
     cfg0!=CSID_E004NS_REAR_IPP_CFG0 || format->data_type!=0x2b)
  return -EINVAL;
 if (readl(csid->base+CSID_IPP_CTRL)!=0)
  return -EBUSY;

 writel(rx_cfg0,csid->base+CSID_CSI2_RX_CFG0);
 writel(CSID_E004NS_REAR_RX_CFG1,csid->base+CSID_CSI2_RX_CFG1);
 writel(CSID_E004NS_REAR_RX_IRQ_MASK,csid->base+CSID_CSI2_RX_IRQ_MASK);
 writel(CSID_E004NS_REAR_BUF_DONE_IRQ_MASK,csid->base+CSID_BUF_DONE_IRQ_MASK);
 writel(CSID_E004NS_REAR_FRAME_DROP_PATTERN,csid->base+CSID_IPP_FRM_DROP_PATTERN);
 writel(CSID_E004NS_REAR_FRAME_DROP_PERIOD,csid->base+CSID_IPP_FRM_DROP_PERIOD);
 writel(CSID_E004NS_REAR_PIX_DROP_PATTERN,csid->base+CSID_IPP_PIX_DROP_PATTERN);
 writel(CSID_E004NS_REAR_PIX_DROP_PERIOD,csid->base+CSID_IPP_PIX_DROP_PERIOD);
 writel(CSID_E004NS_REAR_LINE_DROP_PATTERN,csid->base+CSID_IPP_LINE_DROP_PATTERN);
 writel(CSID_E004NS_REAR_LINE_DROP_PERIOD,csid->base+CSID_IPP_LINE_DROP_PERIOD);
 writel(CSID_E004NS_REAR_EPOCH_IRQ_CFG,csid->base+CSID_IPP_EPOCH_IRQ_CFG);
 writel(CSID_E004NS_REAR_EPOCH_PATTERN,csid->base+CSID_IPP_EPOCH0_SUBSAMPLE_PATTERN);
 writel(CSID_E004NS_REAR_EPOCH_PATTERN,csid->base+CSID_IPP_EPOCH1_SUBSAMPLE_PATTERN);
 writel(cfg0,csid->base+CSID_IPP_CFG0);
 writel(CSID_E004NS_REAR_IPP_CFG1,csid->base+CSID_IPP_CFG1);
 return 0;
}
#endif
