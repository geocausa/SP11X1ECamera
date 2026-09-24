/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E004pt: isolated non-retiring CSID1 BF status observation only.
 * The owning CSID ISR has ALREADY latched buf_done_val and writes its
 * ordinary CSID clear register. Do not perform another MMIO read/ACK,
 * call camss_buf_done(), infer WM16 buffer identity or retire any DMA.
 * This has no frame/owner pairing and is NOT a hardware completion fence.
 */
static inline void e004pt_observe_csid1_bf_irq(struct csid_device *csid,
						     u32 already_latched_buf_done)
{
	if (csid_is_lite(csid) || csid->id != 1 ||
	    !(already_latched_buf_done & BIT(7)))
		return;

	WRITE_ONCE(csid->x1e_e004pt_bf_last_status, already_latched_buf_done);
	atomic64_inc(&csid->x1e_e004pt_bf_observations);
}

/* Read-only diagnostic interface; not exported, wired to VB2 or an IRQ ACK.
 * Count is lifetime of this CSID object, NOT per-owner/per-frame and may not
 * be paired with any BF FIFO8/WM16 queue generation.
 */
u64 csid680_e004pt_bf_status_observations(struct csid_device *csid)
{
	if (!csid || csid_is_lite(csid) || csid->id != 1)
		return 0;
	return (u64)atomic64_read(&csid->x1e_e004pt_bf_observations);
}
