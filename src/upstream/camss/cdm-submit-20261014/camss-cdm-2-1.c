// SPDX-License-Identifier: GPL-2.0-only
/*
 * Independently written CDM2.1 reset backend, dormant until parent integration.
 * Exact Qualcomm GPL definitions are pinned in
 * src/upstream/camss/cdm-lifetime-reference-20261012.json.
 * Single retained REG_CONT submission; no DMA release or runtime parent call.
 */
#include <linux/jiffies.h>
#include <linux/iopoll.h>
#include <linux/dma-mapping.h>
#include <linux/limits.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include "camss-cdm-2-1.h"
#include "camss-cdm-power.h"

#define CDM21_HW_VERSION 0x0
#define CDM21_RESET_CMD 0x10
#define CDM21_CORE_EN 0x1c
#define CDM21_IRQ_MASK(n) (0x30 + (n) * 0x100)
#define CDM21_IRQ_CLEAR(n) (0x34 + (n) * 0x100)
#define CDM21_IRQ_CLEAR_CMD 0x38
#define CDM21_IRQ_STATUS(n) (0x44 + (n) * 0x100)
#define CDM21_PENDING0 0x6c
#define CDM21_PENDING1 0x70
#define CDM21_REQUIRED_SPAN 0x360
#define CDM21_RESET_TIMEOUT_MS 300
#define CDM21_PAUSE_REQUEST 3U
#define CDM21_RESET_ACK 1U
#define CDM21_CORE_CFG 0x18
#define CDM21_FIFO_CFG(n) (0x5c + (n) * 0x100)
#define CDM21_FIFO_BASE 0x50
#define CDM21_FIFO_LEN 0x54
#define CDM21_FIFO_STORE 0x58
#define CDM21_SINGLE_FIFO_CFG (1U << 16)
/* Qualcomm public AHB STOP_ON_ERROR | BURST_EN | BURST_LEN_16. */
#define CDM21_SINGLE_CORE_CFG 0x11fU

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
	if (!cdm->active) {
		spin_unlock_irqrestore(&cdm->irq_lock, flags);
		return IRQ_NONE;
	}
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++) {
		status[i] = readl(cdm->base + CDM21_IRQ_STATUS(i));
		observed |= status[i] != 0;
	}
	if (observed) {
		cdm21_clear_status(cdm, status);
		if (!cdm->issued) {
			/* Clear a stale level IRQ, but never count it as a fresh ACK. */
			cdm->reset.fault = true;
		} else {
			for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
				sp11_cdm21_reset_note(&cdm->reset, cdm->reset.epoch,
						     i, status[i]);
			if (cdm->reset.fault ||
			    sp11_cdm21_reset_ack_complete(&cdm->reset, cdm->reset.epoch))
				complete(&cdm->reset_complete);
		}
	}
	spin_unlock_irqrestore(&cdm->irq_lock, flags);
	return observed ? IRQ_HANDLED : IRQ_NONE;
}

int camss_cdm21_reset_paused_owned(struct camss_cdm21 *cdm,
				 struct camss_cdm21_power *owner)
{
	struct sp11_cdm21_pending pending;
	unsigned long flags, time;
	u32 version, status[4], raw[2];
	unsigned int i;
	int ret, drain_ret, pause_ret;

	if (!cdm || !cdm->initialized)
		return -EINVAL;
	mutex_lock(&cdm->lock);
	if (cdm->power_owner != owner) {
		ret = -EPERM;
		goto unlock;
	}
	if (owner && (!owner->initialized || !owner->held || !owner->touched ||
		      owner->fault || owner->cdm != cdm)) {
		ret = -EPERM;
		goto unlock;
	}
	if (cdm->command_held) {
		ret = -EBUSY;
		goto unlock;
	}
	cdm->reset_ready = false;
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
	if (cdm->irq_disabled) {
		/* Only after version, mask, drain, clear, pause and epoch admission. */
		enable_irq(cdm->irq);
		cdm->irq_disabled = false;
	}
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		writel(CDM21_RESET_ACK, cdm->base + CDM21_IRQ_MASK(i));
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_IRQ_MASK(i)) != CDM21_RESET_ACK) {
			ret = -EIO;
			goto finish;
		}
	/* Reject status arriving during unmask, before this command exists. */
	spin_lock_irqsave(&cdm->irq_lock, flags);
	if (cdm->reset.fault)
		ret = -EIO;
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
		if (!cdm->irq_disabled) {
			disable_irq(cdm->irq);
			cdm->irq_disabled = true;
		}
		cdm->quarantined = true;
	}
	cdm->reset_ready = !ret;
unlock:
	mutex_unlock(&cdm->lock);
	return ret;
}

int camss_cdm21_reset_paused(struct camss_cdm21 *cdm)
{
	return camss_cdm21_reset_paused_owned(cdm, NULL);
}

int camss_cdm21_bind(struct platform_device *pdev,
		    const struct camss_cdm21_resource_names *names,
		    struct camss_cdm21 **out)
{
	struct camss_cdm21 *cdm;
	struct resource *mem;
	resource_size_t span;
	void __iomem *base;
	void *group;
	int irq, ret;

	if (!pdev || !names || !out || !names->registers ||
	    !names->registers[0] || !names->irq || !names->irq[0])
		return -EINVAL;
	mem = platform_get_resource_byname(pdev, IORESOURCE_MEM, names->registers);
	if (!mem)
		return -ENODEV;
	if (mem->end < mem->start || (mem->start & 3))
		return -EINVAL;
	span = resource_size(mem);
	if (span < CDM21_REQUIRED_SPAN || span != (size_t)span)
		return -EINVAL;
	irq = platform_get_irq_byname(pdev, names->irq);
	if (irq < 0)
		return irq;
	group = devres_open_group(&pdev->dev, NULL, GFP_KERNEL);
	if (!group)
		return -ENOMEM;
	base = devm_ioremap_resource(&pdev->dev, mem);
	if (IS_ERR(base)) {
		ret = PTR_ERR(base);
		goto release;
	}
	cdm = devm_kzalloc(&pdev->dev, sizeof(*cdm), GFP_KERNEL);
	if (!cdm) {
		ret = -ENOMEM;
		goto release;
	}
	ret = camss_cdm21_init(cdm, base, span, irq);
	if (ret)
		goto release;
	cdm->irq_disabled = true;
	ret = devm_request_irq(&pdev->dev, irq, camss_cdm21_isr, IRQF_NO_AUTOEN,
			       "camss-cdm21", cdm);
	if (ret)
		goto release;
	/* Managed cleanup releases IRQ before state and mapping, in reverse order. */
	devres_remove_group(&pdev->dev, group);
	*out = cdm;
	return 0;
release:
	devres_release_group(&pdev->dev, group);
	return ret;
}

static int cdm21_empty(struct camss_cdm21 *cdm)
{
	struct sp11_cdm21_pending pending;
	u32 raw[2];
	unsigned int i;
	int ret;

	raw[0] = readl(cdm->base + CDM21_PENDING0);
	raw[1] = readl(cdm->base + CDM21_PENDING1);
	ret = sp11_cdm21_decode_pending(SP11_CDM21_VERSION, raw, &pending);
	for (i = 0; !ret && i < SP11_CDM21_FIFO_COUNT; i++)
		if (pending.count[i])
			ret = -EBUSY;
	return ret;
}

/* IRQ remains masked and drained; this sleepable finite polling path does not
 * participate in the reset ISR. Accumulate faults before accepting BL_DONE.
 */
static int cdm21_command_status(struct camss_cdm21 *cdm, u32 *seen)
{
	u32 status;
	unsigned int i;

	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++) {
		status = readl(cdm->base + CDM21_IRQ_STATUS(i));
		if ((!i && (status & ~6U)) || (i && status))
			return -EIO;
		if (!i)
			*seen |= status;
	}
	return sp11_cdm21_command_status_valid(*seen) ? 0 : -EAGAIN;
}

int camss_cdm21_submit_owned(struct camss_cdm21 *cdm,
			    struct camss_cdm21_power *owner,
			    const struct sp11_cdm21_command *command,
			    const struct camss_cdm21_retention *retention,
			    struct sp11_cdm21_receipt *receipt)
{
	struct sp11_cdm21_command next;
	struct sp11_cdm21_receipt done;
	u32 status[4], seen = 0, version;
	unsigned int i;
	int ret, poll_ret, drain_ret, pause_ret;

	if (!cdm || !cdm->initialized || !owner || !command ||
	    !retention || !retention->hold || !receipt)
		return -EINVAL;
	/* Serialize parent storage and ownership throughout this copy and call. */
	next = *command;
	ret = sp11_cdm21_command_validate(&next);
	if (ret)
		return ret;
	if (sp11_cdm_overlap(receipt, sizeof(*receipt), cdm, sizeof(*cdm)) ||
	    sp11_cdm_overlap(receipt, sizeof(*receipt), command, sizeof(*command)) ||
	    sp11_cdm_overlap(receipt, sizeof(*receipt), next.cpu, next.capacity) ||
	    sp11_cdm_overlap(receipt, sizeof(*receipt), owner, sizeof(*owner)) ||
	    sp11_cdm_overlap(receipt, sizeof(*receipt), retention, sizeof(*retention)))
		return -EINVAL;
	mutex_lock(&cdm->lock);
	if (cdm->power_owner != owner || !owner->initialized ||
	    !owner->held || !owner->touched || owner->fault || owner->cdm != cdm) {
		ret = -EPERM;
		goto unlock;
	}
	if (cdm->quarantined) {
		ret = -EIO;
		goto unlock;
	}
	if (!cdm->reset_ready || cdm->active || cdm->command_held) {
		ret = -EBUSY;
		goto unlock;
	}
	if (cdm->command_sequence == U64_MAX) {
		ret = -EOVERFLOW;
		goto unlock;
	}
	version = readl(cdm->base + CDM21_HW_VERSION);
	if (version != SP11_CDM21_VERSION) {
		ret = -ENODEV;
		cdm->quarantined = true;
		goto unlock;
	}
	ret = retention->hold(retention->context, &next);
	if (ret)
		goto unlock;
	/* Even a pre-STORE MMIO failure retains these independent parent holds.
	 * No return path frees, rewrites, retries or drops exposed dependencies.
	 */
	cdm->retained_command = next;
	cdm->command_held = true;
	cdm->reset_ready = false;
	cdm->command_sequence++;
	ret = cdm21_mask_and_drain(cdm);
	if (ret)
		goto finish;
	ret = cdm21_request_pause(cdm);
	if (ret)
		goto finish;
	ret = cdm21_empty(cdm);
	if (ret)
		goto finish;
	ret = cdm21_clear_old(cdm);
	if (ret)
		goto finish;
	/* Only FIFO0, one outstanding program, no implicit wait or other bank. */
	writel(CDM21_SINGLE_CORE_CFG, cdm->base + CDM21_CORE_CFG);
	writel(CDM21_SINGLE_FIFO_CFG, cdm->base + CDM21_FIFO_CFG(0));
	if (readl(cdm->base + CDM21_CORE_CFG) != CDM21_SINGLE_CORE_CFG ||
	    readl(cdm->base + CDM21_FIFO_CFG(0)) != CDM21_SINGLE_FIFO_CFG) {
		ret = -EIO;
		goto finish;
	}
	/* All other FIFO banks must remain disabled after the fresh reset. */
	for (i = 1; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_FIFO_CFG(i))) {
			ret = -EBUSY;
			goto finish;
		}
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (readl(cdm->base + CDM21_IRQ_STATUS(i))) {
			ret = -EIO;
			goto finish;
		}
	dma_wmb();
	writel((u32)next.dma, cdm->base + CDM21_FIFO_BASE);
	writel(sp11_cdm21_command_length(next.bytes), cdm->base + CDM21_FIFO_LEN);
	writel(1, cdm->base + CDM21_FIFO_STORE);
	/* Ordered read flushes the posted STORE before the core can consume it. */
	readl(cdm->base + CDM21_FIFO_LEN);
	writel(1, cdm->base + CDM21_CORE_EN);
	if (readl(cdm->base + CDM21_CORE_EN) != 1) {
		ret = -EIO;
		goto finish;
	}
	poll_ret = read_poll_timeout(cdm21_command_status, ret, ret != -EAGAIN,
				     50, 300000, false, cdm, &seen);
	if (poll_ret)
		ret = poll_ret;
finish:
	drain_ret = cdm21_mask_and_drain(cdm);
	pause_ret = cdm21_request_pause(cdm);
	if (!ret && (drain_ret || pause_ret))
		ret = -EIO;
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++) {
		status[i] = readl(cdm->base + CDM21_IRQ_STATUS(i));
		if (!ret && ((!i && (status[i] & ~6U)) || (i && status[i])))
			ret = -EIO;
	}
	if (!ret && !sp11_cdm21_command_status_valid(seen))
		ret = -EIO;
	if (!ret)
		ret = cdm21_empty(cdm);
	cdm21_clear_status(cdm, status);
	for (i = 0; i < SP11_CDM21_FIFO_COUNT; i++)
		if (!ret && readl(cdm->base + CDM21_IRQ_STATUS(i)))
			ret = -EIO;
	if (ret) {
		if (!cdm->irq_disabled) {
			disable_irq(cdm->irq);
			cdm->irq_disabled = true;
		}
		cdm->quarantined = true;
		goto unlock;
	}
	done.owner = next.owner;
	done.request = next.request;
	done.sequence = cdm->command_sequence;
	done.dma = next.dma;
	done.bytes = next.bytes;
	done.status = seen;
	*receipt = done;
unlock:
	mutex_unlock(&cdm->lock);
	return ret;
}
