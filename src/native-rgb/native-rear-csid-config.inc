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

/* Full rear IPP uses the qualified full-CSID software reset. Other generic
 * routes retain combined reset; the existing front branch returns earlier. */
static u32 native_rear_csid_reset_command(struct csid_device *csid)
{
 return csid_e004ns_rear_ipp_mode0(csid) ? CSID_RESET_CMD_SW_RESET :
        (CSID_RESET_CMD_HW_RESET | CSID_RESET_CMD_SW_RESET);
}

/* The shared Windows DEVICE_CONFIG route precedes reset/configuration.
 * Exact rear final route is independently observed as 0x101. Establish it
 * before any startup RUP/AUP submission; do not change CTRL or packet data.
 * Called within media PM acquisition under the already-held rear owner.
 * Other routes and the earlier front reset branch remain unchanged.
 */
static void native_rear_csid_route_before_reset(struct csid_device *csid)
{
 if (csid_e004ns_rear_ipp_mode0(csid))
  writel(CSID_E004NS_REAR_WRAPPER_CFG0,
         csid->camss->csid_wrapper_base + CSID_TOP_IO_PATH_CFG0(csid->id));
}

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
 return 0;
}

/* Packet0 owns crop/format/subsample programming. Admit all its expected
 * readbacks before the existing two path configuration writes.
 * Exact Windows Gen2 builder writes crops before CFG0/CFG1. The rear
 * adaptation preserves packet ownership; causality requires hardware proof.
 * No CTRL, RUP/AUP, IRQ ACK or new register value is introduced.
 */
int csid680_native_rear_after_packet0_configure(struct csid_device *csid)
{
 const struct csid_format_info *format;
 u32 cfg0;
 if (!csid_e004ns_rear_ipp_mode0(csid))
  return -EINVAL;
 format=csid_get_fmt_entry(csid->res->formats->formats,
                          csid->res->formats->nformats,
                          csid->fmt[MSM_CSID_PAD_PIX].code);
 if (!format)
  return -EINVAL;
 cfg0=(format->decode_format << IPP_CFG0_DECODE_FORMAT) |
      (format->data_type << IPP_CFG0_DATA_TYPE) | IPP_CFG0_ENABLE;
 if (cfg0!=CSID_E004NS_REAR_IPP_CFG0 || format->data_type!=0x2b)
  return -EINVAL;
 if (readl(csid->base+CSID_IPP_CTRL)!=0)
  return -EBUSY;
 if (readl(csid->base+CSID_IPP_HCROP)!=CSID_E004NS_REAR_IPP_HCROP ||
     readl(csid->base+CSID_IPP_VCROP)!=CSID_E004NS_REAR_IPP_VCROP ||
     readl(csid->base+CSID_IPP_FORMAT_MEASURE_CFG0)!=CSID_E004NS_REAR_IPP_FORMAT_CFG0 ||
     readl(csid->base+CSID_IPP_FORMAT_MEASURE_CFG1)!=CSID_E004NS_REAR_IPP_FORMAT_CFG1 ||
     readl(csid->base+CSID_IPP_SP11_PARITY_ZERO1)!=CSID_E004NS_REAR_PARITY_ZERO1 ||
     readl(csid->base+CSID_IPP_IRQ_SUBSAMPLE_PATTERN)!=CSID_E004NS_REAR_IRQ_SUBSAMPLE_PATTERN ||
     readl(csid->base+CSID_IPP_IRQ_SUBSAMPLE_PERIOD)!=CSID_E004NS_REAR_IRQ_SUBSAMPLE_PERIOD)
  return -EPROTO;
 writel(cfg0,csid->base+CSID_IPP_CFG0);
 writel(CSID_E004NS_REAR_IPP_CFG1,csid->base+CSID_IPP_CFG1);
 return 0;
}
#endif
