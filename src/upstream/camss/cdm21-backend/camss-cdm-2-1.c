// SPDX-License-Identifier: GPL-2.0-only
/*
 * Independently written CDM2.1 reset backend, dormant until parent integration.
 * Exact Qualcomm GPL definitions are pinned in
 * src/upstream/camss/cdm-lifetime-reference-20261012.json.
 * No command submission, DMA allocation/release, DT binding or power operation.
 */
#include <linux/jiffies.h>
#include <linux/limits.h>
#include "camss-cdm-2-1.h"

#define CDM21_HW_VERSION 0x0
#define CDM21_RESET_CMD 0x10
#define CDM21_CORE_EN 0x1c
#define CDM21_IRQ_MASK(n) (0x30 + (n) * 0x100)
#define CDM21_IRQ_CLEAR(n) (0x34 + (n) * 0x100)
#define CDM21_IRQ_CLEAR_CMD 0x38
#define CDM21_IRQ_STATUS(n) (0x44 + (n) * 0x100)
#define CDM21_PENDING0 0x6c
#define CDM21_PENDING1 0x70
#define CDM21_REQUIRED_SPAN 0x348
#define CDM21_RESET_TIMEOUT_MS 300
#define CDM21_PAUSE_REQUEST 3U
#define CDM21_RESET_ACK 1U

int camss_cdm21_init(struct camss_cdm21 *cdm, void __iomem *base,
		    size_t span, int irq)
{
	if (!cdm || !base || span < CDM21_REQUIRED_SPAN || irq < 0)
		return -EINVAL;
	if (cdm->initialized)
		return -EBUSY;
	cdm->base = base;
	cdm->irq = irq;
	mutex_init(&cdm->lock);
	spin_lock_init(&cdm->irq_lock);
	init_completion(&cdm->reset_complete);
	cdm->initialized = true;
	return 0;
}

/* Always attempt all banks, then drain even if a mask readback failed. */
static int cdm21_mask_and_drain(struct camss_cdm21 *cdm)
{
	unsigned int i;
	int ret = 0;

	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		writel(0, cdm->base + CDM21_IRQ_MASK(i));
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_IRQ_MASK(i)))
			ret = -EIO;
	synchronize_irq(cdm->irq);
	return ret;
}

static void cdm21_clear_status(struct camss_cdm21 *cdm, const u32 status[4])
{
	unsigned int i;

	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		writel(status[i], cdm->base + CDM21_IRQ_CLEAR(i));
	/* Public CDM2.1 ISR uses the bank-zero global clear command once. */
	writel(1, cdm->base + CDM21_IRQ_CLEAR_CMD);
	readl(cdm->base + CDM21_IRQ_STATUS(0));
}

static int cdm21_clear_old(struct camss_cdm21 *cdm)
{
	u32 status[4];
	unsigned int i;
	int ret = 0;

	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		status[i] = readl(cdm->base + CDM21_IRQ_STATUS(i));
	cdm21_clear_status(cdm, status);
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_IRQ_STATUS(i)))
			ret = -EIO;
	return ret;
}

static int cdm21_request_pause(struct camss_cdm21 *cdm)
{
	writel(CDM21_PAUSE_REQUEST, cdm->base + CDM21_CORE_EN);
	return readl(cdm->base + CDM21_CORE_EN) == CDM21_PAUSE_REQUEST ?
	       0 : -EIO;
}

irqreturn_t camss_cdm21_isr(int irq, void *data)
{
	struct camss_cdm21 *cdm = data;
	unsigned long flags;
	u32 status[4];
	unsigned int i;
	bool observed = false;

	if (!cdm || !cdm->initialized || irq != cdm->irq)
		return IRQ_NONE;
	spin_lock_irqsave(&cdm->irq_lock, flags);
	if (!cdm->active || !cdm->issued) {
		spin_unlock_irqrestore(&cdm->irq_lock, flags);
		return IRQ_NONE;
	}
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++) {
		status[i] = readl(cdm->base + CDM21_IRQ_STATUS(i));
		observed |= status[i] != 0;
	}
	if (observed) {
		cdm21_clear_status(cdm, status);
		for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
			sp11_cdm21_reset_note(&cdm->reset, cdm->reset.epoch,
					     i, status[i]);
		if (cdm->reset.fault ||
		    sp11_cdm21_reset_ack_complete(&cdm->reset, cdm->reset.epoch))
			complete(&cdm->reset_complete);
	}
	spin_unlock_irqrestore(&cdm->irq_lock, flags);
	return observed ? IRQ_HANDLED : IRQ_NONE;
}

int camss_cdm21_reset_paused(struct camss_cdm21 *cdm)
{
	struct sp11_cdm21_pending pending;
	unsigned long flags, time;
	u32 version, status[4], raw[2];
	unsigned int i;
	int ret, drain_ret, pause_ret;

	if (!cdm || !cdm->initialized)
		return -EINVAL;
	mutex_lock(&cdm->lock);
	if (cdm->quarantined) {
		ret = -EIO;
		goto unlock;
	}
	version = readl(cdm->base + CDM21_HW_VERSION);
	if (version != SP11_CDM21_VERSION) {
		/* Unsupported revisions receive no writes or IRQ manipulation. */
		cdm->quarantined = true;
		ret = -ENODEV;
		goto unlock;
	}
	ret = cdm21_mask_and_drain(cdm);
	if (ret)
		goto finish;
	ret = cdm21_clear_old(cdm);
	if (ret)
		goto finish;
	ret = cdm21_request_pause(cdm);
	if (ret)
		goto finish;
	if (cdm->reset.epoch == U64_MAX) {
		ret = -EOVERFLOW;
		goto finish;
	}
	reinit_completion(&cdm->reset_complete);
	spin_lock_irqsave(&cdm->irq_lock, flags);
	ret = sp11_cdm21_reset_begin(&cdm->reset, version,
				    cdm->reset.epoch + 1);
	if (!ret)
		cdm->active = true;
	spin_unlock_irqrestore(&cdm->irq_lock, flags);
	if (ret)
		goto finish;
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		writel(CDM21_RESET_ACK, cdm->base + CDM21_IRQ_MASK(i));
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_IRQ_MASK(i)) != CDM21_RESET_ACK) {
			ret = -EIO;
			goto finish;
		}
	/* Reject status arriving during unmask, before this command exists. */
	spin_lock_irqsave(&cdm->irq_lock, flags);
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_IRQ_STATUS(i)))
			ret = -EIO;
	if (!ret) {
		cdm->issued = true;
		writel(1, cdm->base + CDM21_RESET_CMD);
		readl(cdm->base + CDM21_IRQ_MASK(0));
	}
	spin_unlock_irqrestore(&cdm->irq_lock, flags);
	if (ret)
		goto finish;
	time = wait_for_completion_timeout(&cdm->reset_complete,
					  msecs_to_jiffies(CDM21_RESET_TIMEOUT_MS));
	ret = time ? 0 : -ETIMEDOUT;
finish:
	/* Keep observation active through final masking/drain to catch late faults.
	 * No resume on success or failure. A pause readback is not a pause ACK.
	 */
	drain_ret = cdm21_mask_and_drain(cdm);
	pause_ret = cdm21_request_pause(cdm);
	if (!ret && (drain_ret || pause_ret))
		ret = -EIO;
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		status[i] = readl(cdm->base + CDM21_IRQ_STATUS(i));
	spin_lock_irqsave(&cdm->irq_lock, flags);
	if (cdm->active) {
		for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
			if (status[i] & ~7U)
				cdm->reset.fault = true;
		if (!ret && !sp11_cdm21_reset_ack_complete(&cdm->reset,
							 cdm->reset.epoch))
			ret = -EIO;
		sp11_cdm21_reset_close(&cdm->reset, cdm->reset.epoch);
		cdm->active = false;
		cdm->issued = false;
	}
	spin_unlock_irqrestore(&cdm->irq_lock, flags);
	cdm21_clear_status(cdm, status);
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (!ret && readl(cdm->base + CDM21_IRQ_STATUS(i)))
			ret = -EIO;
	if (!ret) {
		raw[0] = readl(cdm->base + CDM21_PENDING0);
		raw[1] = readl(cdm->base + CDM21_PENDING1);
		ret = sp11_cdm21_decode_pending(version, raw, &pending);
		for (i = 0; !ret && i < SP11_CDM21_FIFO_COUNT; i++)
			if (pending.count[i])
				ret = -EBUSY;
	}
	if (ret) {
		/* Own exclusive IRQ: prevent storms if device masking failed. */
		disable_irq(cdm->irq);
		cdm->irq_disabled = true;
		cdm->quarantined = true;
	}
unlock:
	mutex_unlock(&cdm->lock);
	return ret;
}
