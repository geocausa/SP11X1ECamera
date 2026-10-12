/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef CAMSS_CDM_2_1_H
#define CAMSS_CDM_2_1_H

#include <linux/completion.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include "sp11-cdm21-state.h"

/* Parent-owned, initially zeroed storage. No command or DMA-buffer ownership.
 * Parent must provide a fresh powered CDM instance, exclusive mapped register
 * extent and IRQ, with no other reset/submission owner. Keep power, mapping,
 * IRQ registration and storage live through every operation and handler.
 * A failed transaction quarantines this instance; do not reinitialize it to
 * bypass failure. Full parent power/reset and DMA recovery need separate proof.
 */
struct camss_cdm21 {
	void __iomem *base;
	int irq;
	struct mutex lock;
	spinlock_t irq_lock;
	struct completion reset_complete;
	struct sp11_cdm21_reset_observation reset;
	bool initialized;
	bool active;
	bool issued;
	bool quarantined;
	bool irq_disabled;
};

int camss_cdm21_init(struct camss_cdm21 *cdm, void __iomem *base,
		    size_t span, int irq);
irqreturn_t camss_cdm21_isr(int irq, void *data);

/* Sleepable. Parent must register the ISR before calling, and prevent all
 * concurrent producers/submissions. Success means four reset ACKs, observed
 * zero FIFO counts and a pause request/readback; CDM2.1 has no pause-done
 * register. Neither success nor failure permits DMA release or power removal.
 */
int camss_cdm21_reset_paused(struct camss_cdm21 *cdm);

#endif
