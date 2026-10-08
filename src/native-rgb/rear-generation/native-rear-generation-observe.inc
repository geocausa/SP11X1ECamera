/* SPDX-License-Identifier: GPL-2.0-only */
/* Candidate-only register observations. No writes, ACKs, tuning or pixel reads. */
#include "camss-e008k-rear-bridge.h"
void csid680_native_rear_generation_snapshot(struct csid_device *csid,const char *phase)
{
 if (!csid || !csid_e004ns_rear_ipp_mode0(csid))
  return;
 dev_info(csid->camss->dev,
  "NATIVE_REAR_GENERATION_CSI phase=%s rx0=%08x rx1=%08x rx_status=%08x rx_mask=%08x packets=%u ecc=%u crc=%u\n",
  phase,readl(csid->base+CSID_CSI2_RX_CFG0),readl(csid->base+CSID_CSI2_RX_CFG1),
  readl(csid->base+CSID_CSI2_RX_IRQ_STATUS),readl(csid->base+CSID_CSI2_RX_IRQ_MASK),
  readl(csid->base+CSID_CSI2_RX_TOTAL_PKTS_RCVD),readl(csid->base+CSID_CSI2_RX_STATS_ECC),
  readl(csid->base+CSID_CSI2_RX_CRC_ERRORS));
 dev_info(csid->camss->dev,
  "NATIVE_REAR_GENERATION_PACKET_FIELDS phase=%s frame=%08x irq_pattern=%08x irq_period=%08x hcrop=%08x vcrop=%08x measure_cfg0=%08x measure_cfg1=%08x rup=%08x\n",
  phase,readl(csid->base+CSID_IPP_SP11_PARITY_ZERO1),
  readl(csid->base+CSID_IPP_IRQ_SUBSAMPLE_PATTERN),readl(csid->base+CSID_IPP_IRQ_SUBSAMPLE_PERIOD),
  readl(csid->base+CSID_IPP_HCROP),readl(csid->base+CSID_IPP_VCROP),
  readl(csid->base+CSID_IPP_FORMAT_MEASURE_CFG0),readl(csid->base+CSID_IPP_FORMAT_MEASURE_CFG1),
  readl(csid->base+CSID_REG_UPDATE_CMD));
 dev_info(csid->camss->dev,
  "NATIVE_REAR_GENERATION_CAMIF phase=%s multi_vcdt=%08x camif1=%08x camif0=%08x halt=%08x measure0=%08x measure1=%08x measure2=%08x lut_bank=%08x buf_status=%08x buf_mask=%08x\n",
  phase,readl(csid->base+0x30c),readl(csid->base+0x340),readl(csid->base+0x344),
  readl(csid->base+0x348),readl(csid->base+CSID_IPP_FORMAT_MEASURE0),
  readl(csid->base+CSID_IPP_FORMAT_MEASURE1),readl(csid->base+CSID_IPP_FORMAT_MEASURE2),
  readl(csid->base+0x3b8),readl(csid->base+CSID_BUF_DONE_IRQ_STATUS),
  readl(csid->base+CSID_BUF_DONE_IRQ_MASK));
 dev_info(csid->camss->dev,
  "NATIVE_REAR_GENERATION_IPP phase=%s cfg0=%08x cfg1=%08x ctrl=%08x status=%08x mask=%08x epoch_cfg=%08x top=%08x/%08x route=%08x epochs=%u done=%u overflow=%u errors=%u\n",
  phase,readl(csid->base+CSID_IPP_CFG0),readl(csid->base+CSID_IPP_CFG1),
  readl(csid->base+CSID_IPP_CTRL),readl(csid->base+CSID_IPP_IRQ_STATUS),
  readl(csid->base+CSID_IPP_IRQ_MASK),readl(csid->base+CSID_IPP_EPOCH_IRQ_CFG),
  readl(csid->base+CSID_TOP_IRQ_STATUS),readl(csid->base+CSID_TOP_IRQ_MASK),
  readl(csid->camss->csid_wrapper_base+CSID_TOP_IO_PATH_CFG0(csid->id)),
  READ_ONCE(csid->e008i_rear_epoch0_count),READ_ONCE(csid->e008i_rear_done_count),
  READ_ONCE(csid->e008i_rear_done_overflow),READ_ONCE(csid->e008i_rear_latch_errors));
}
