/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008a build-only rear CSID1 producer quiesce + IRQ drain helper.
 * Unreachable: no call site is installed by this checkpoint.
 */
#ifndef CAMSS_CSID_E008A_REAR_QUIESCE_INC
#define CAMSS_CSID_E008A_REAR_QUIESCE_INC

static void e008a_csid680_clear_all_status(struct csid_device *csid)
{
	u32 val;
	int i;

	val = readl(csid->base + CSID_TOP_IRQ_STATUS);
	if (val)
		writel(val, csid->base + CSID_TOP_IRQ_CLEAR);

	val = readl(csid->base + CSID_CSI2_RX_IRQ_STATUS);
	if (val)
		writel(val, csid->base + CSID_CSI2_RX_IRQ_CLEAR);

	val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);
	if (val)
		writel(val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);

	val = readl(csid->base + CSID_IPP_IRQ_STATUS);
	if (val)
		writel(val, csid->base + CSID_IPP_IRQ_CLEAR);

	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++) {
		val = readl(csid->base + CSID_CSI2_RDIN_IRQ_STATUS(i));
		if (val)
			writel(val, csid->base + CSID_CSI2_RDIN_IRQ_CLEAR(i));
	}

	writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);
}

static bool e008a_csid680_all_status_zero(struct csid_device *csid)
{
	int i;

	if (readl(csid->base + CSID_TOP_IRQ_STATUS) ||
	    readl(csid->base + CSID_CSI2_RX_IRQ_STATUS) ||
	    readl(csid->base + CSID_BUF_DONE_IRQ_STATUS) ||
	    readl(csid->base + CSID_IPP_IRQ_STATUS))
		return false;

	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++)
		if (readl(csid->base + CSID_CSI2_RDIN_IRQ_STATUS(i)))
			return false;

	return true;
}

/*
 * exact_rear_owner is an external ownership precondition. This helper refuses
 * to infer route ownership from mutable hardware state alone.
 *
 * The sequence reuses the physically accepted front CSID680 immediate reset
 * completion mechanism, then strengthens it for DMA lifetime by masking all
 * producer/completion IRQ banks and synchronizing the real Linux CSID IRQ.
 */
int csid680_e008a_rear_quiesce(struct csid_device *csid,
				 bool exact_rear_owner);

int __used
csid680_e008a_rear_quiesce(struct csid_device *csid, bool exact_rear_owner)
{
	unsigned long time;
	u32 val;
	int i;

	if (!csid || !exact_rear_owner || csid->id != 1 || csid_is_lite(csid) ||
	    !csid->phy.en_ipp || !csid->irq)
		return -EINVAL;

	/* Block new rear completion/path interrupts while retaining reset ACK. */
	writel(SP11_CSID_TOP_IRQ_MASK_MODE0, csid->base + CSID_TOP_IRQ_MASK);
	writel(0, csid->base + CSID_BUF_DONE_IRQ_MASK);
	writel(0, csid->base + CSID_IPP_IRQ_MASK);
	writel(0, csid->base + CSID_CSI2_RX_IRQ_MASK);
	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++)
		writel(0, csid->base + CSID_CSI2_RDIN_IRQ_MASK(i));

	e008a_csid680_clear_all_status(csid);

	reinit_completion(&csid->reset_complete);
	val = CSID_RESET_CFG_MODE_IMMEDIATE |
	      CSID_RESET_CFG_LOCATION_COMPLETE;
	writel(val, csid->base + CSID_RESET_CFG);
	writel(CSID_RESET_CMD_HW_RESET, csid->base + CSID_RESET_CMD);

	time = wait_for_completion_timeout(&csid->reset_complete,
					   msecs_to_jiffies(SP11_CSID_RESET_TIMEOUT_MS));
	if (!time)
		return -EIO;

	/*
	 * After reset completion, no path interrupt is allowed to become visible.
	 * Clear any reset-edge residue, wait out any ISR that had already entered,
	 * then require a completely quiet status surface.
	 */
	writel(0, csid->base + CSID_TOP_IRQ_MASK);
	writel(0, csid->base + CSID_BUF_DONE_IRQ_MASK);
	writel(0, csid->base + CSID_IPP_IRQ_MASK);
	writel(0, csid->base + CSID_CSI2_RX_IRQ_MASK);
	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++)
		writel(0, csid->base + CSID_CSI2_RDIN_IRQ_MASK(i));

	e008a_csid680_clear_all_status(csid);
	synchronize_irq(csid->irq);

	/* Clear once more after the ISR barrier, then prove no producer residue. */
	e008a_csid680_clear_all_status(csid);
	synchronize_irq(csid->irq);
	if (!e008a_csid680_all_status_zero(csid))
		return -EBUSY;

	return 0;
}

#endif /* CAMSS_CSID_E008A_REAR_QUIESCE_INC */
