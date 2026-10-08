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
  "NATIVE_REAR_GENERATION_IPP phase=%s cfg0=%08x cfg1=%08x ctrl=%08x status=%08x mask=%08x epoch_cfg=%08x top=%08x/%08x route=%08x epochs=%u done=%u overflow=%u errors=%u\n",
  phase,readl(csid->base+CSID_IPP_CFG0),readl(csid->base+CSID_IPP_CFG1),
  readl(csid->base+CSID_IPP_CTRL),readl(csid->base+CSID_IPP_IRQ_STATUS),
  readl(csid->base+CSID_IPP_IRQ_MASK),readl(csid->base+CSID_IPP_EPOCH_IRQ_CFG),
  readl(csid->base+CSID_TOP_IRQ_STATUS),readl(csid->base+CSID_TOP_IRQ_MASK),
  readl(csid->camss->csid_wrapper_base+CSID_TOP_IO_PATH_CFG0(csid->id)),
  READ_ONCE(csid->e008i_rear_epoch0_count),READ_ONCE(csid->e008i_rear_done_count),
  READ_ONCE(csid->e008i_rear_done_overflow),READ_ONCE(csid->e008i_rear_latch_errors));
}
