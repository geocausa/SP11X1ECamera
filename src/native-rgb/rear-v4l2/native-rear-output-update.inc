/* SPDX-License-Identifier: GPL-2.0-only */
/* Fixed RUP/AUP word from the qualified rear startup wrapper. Address writes
 * alone did not latch generation3 on hardware34. This commit is synchronous
 * MMIO; it submits no command DMA and grants no output release authority.
 */
#ifndef NATIVE_REAR_OUTPUT_UPDATE_INC
#define NATIVE_REAR_OUTPUT_UPDATE_INC
int csid680_native_rear_output_update(struct csid_device *csid, u64 owner)
{
 struct e005y_vfe1_owner *o;
 unsigned long flags;
 int ret = 0;
 if (!csid || !csid->camss || !owner || !csid->irq ||
     csid != &csid->camss->csid[1] || !csid_e004ns_rear_ipp_mode0(csid))
  return -EINVAL;
 if (READ_ONCE(csid->e008i_rear_owner_epoch) != owner ||
     READ_ONCE(csid->e008i_rear_done_overflow) ||
     READ_ONCE(csid->e008i_rear_latch_errors))
  return -ESTALE;
 o = &csid->camss->e005y_vfe1_owner;
 spin_lock_irqsave(&o->lock, flags);
 if (o->active_owner != E005Y_VFE1_OWNER_REAR || o->active_epoch != owner ||
     o->unsafe_stop_pinned)
  ret = -ESTALE;
 else if (readl(csid->base + CSID_IPP_CTRL) != 1 ||
          readl(csid->base + CSID_IPP_CFG0) != CSID_E004NS_REAR_IPP_CFG0 ||
          readl(csid->base + CSID_IPP_CFG1) != CSID_E004NS_REAR_IPP_CFG1)
  ret = -ESHUTDOWN;
 else {
  /* All10 new address readbacks precede this RUP/AUP. No IRQ ACK or
   * packet replay. Completion must still prove all10 consumed addresses.
   */
  wmb();
  writel(0x01f501f5U, csid->base + CSID_REG_UPDATE_CMD);
 }
 spin_unlock_irqrestore(&o->lock, flags);
 return ret;
}
#endif
