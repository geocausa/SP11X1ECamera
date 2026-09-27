/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008i rear CSID1 software-latch observer.
 *
 * Included only in an isolated build. The ISR hook consumes the already-read
 * BUF_DONE/IPP status after the existing BUF_DONE clear write; it adds no IRQ
 * ACK and no camera-control MMIO. VFE ADDR_STATUS0 reads are observation-only.
 */
#ifndef CAMSS_CSID_E008I_REAR_OBSERVER_INC
#define CAMSS_CSID_E008I_REAR_OBSERVER_INC

static void
e008i_rear_latch_buf_done(struct csid_device *csid, u32 buf_done_status)
{
	struct e008i_rear_done_event *evt;
	u64 owner_epoch;
	u32 n;
	int ret;

	if (!csid_e004ns_rear_ipp_mode0(csid) ||
	    !(buf_done_status & E008I_REAR_BUF_DONE_MASK))
		return;

	owner_epoch = READ_ONCE(csid->e008i_rear_owner_epoch);
	n = READ_ONCE(csid->e008i_rear_done_count);
	if (!owner_epoch || n >= E008I_REAR_DONE_DEPTH) {
		WRITE_ONCE(csid->e008i_rear_done_overflow,
			   READ_ONCE(csid->e008i_rear_done_overflow) + 1);
		return;
	}

	evt = &csid->e008i_rear_done[n];
	evt->owner_epoch = owner_epoch;
	evt->sequence = n + 1;
	evt->raw_buf_done_status = buf_done_status;
	evt->wm_mask = 0;
	evt->reserved = 0;

	ret = vfe680_e008i_rear_snapshot_addr_status0(&csid->camss->vfe[1],
						      buf_done_status,
						      &evt->wm_mask,
						      evt->addr_status0);
	if (ret) {
		WRITE_ONCE(csid->e008i_rear_latch_errors,
			   READ_ONCE(csid->e008i_rear_latch_errors) + 1);
		memset(evt, 0, sizeof(*evt));
		return;
	}

	/* Publish the fully populated record only after all MMIO samples land. */
	smp_wmb();
	WRITE_ONCE(csid->e008i_rear_done_count, n + 1);
}

static void
e008i_rear_latch_ipp(struct csid_device *csid, u32 ipp_status)
{
	if (!csid_e004ns_rear_ipp_mode0(csid) ||
	    !(ipp_status & CSID_IPP_CAMIF_EPOCH0))
		return;

	WRITE_ONCE(csid->e008i_rear_epoch0_count,
		   READ_ONCE(csid->e008i_rear_epoch0_count) + 1);
}

int csid680_e008i_rear_reset(struct csid_device *csid, u64 owner_epoch)
{
	if (!csid || !csid_e004ns_rear_ipp_mode0(csid) ||
	    !owner_epoch || !csid->irq)
		return -EINVAL;

	/*
	 * Future runner contract: call only after exclusive REAR owner acquire
	 * and before rear CSID IRQ masks are armed. Drain any pre-existing ISR
	 * instance before clearing software history.
	 */
	synchronize_irq(csid->irq);
	memset(csid->e008i_rear_done, 0, sizeof(csid->e008i_rear_done));
	WRITE_ONCE(csid->e008i_rear_owner_epoch, owner_epoch);
	WRITE_ONCE(csid->e008i_rear_epoch0_count, 0);
	WRITE_ONCE(csid->e008i_rear_done_count, 0);
	WRITE_ONCE(csid->e008i_rear_done_overflow, 0);
	WRITE_ONCE(csid->e008i_rear_latch_errors, 0);
	return 0;
}

u32 csid680_e008i_rear_epoch0_seq(struct csid_device *csid)
{
	if (!csid || !csid_e004ns_rear_ipp_mode0(csid))
		return 0;
	return READ_ONCE(csid->e008i_rear_epoch0_count);
}

int csid680_e008i_rear_poll_next_epoch0(struct csid_device *csid,
					u32 after_seq,
					unsigned long timeout_us)
{
	u32 seq;
	int ret;

	if (!csid || !timeout_us || !csid_e004ns_rear_ipp_mode0(csid) ||
	    !READ_ONCE(csid->e008i_rear_owner_epoch))
		return -EINVAL;

	ret = read_poll_timeout(READ_ONCE, seq, seq != after_seq, 10,
				timeout_us, false,
				csid->e008i_rear_epoch0_count);
	if (ret)
		return ret;
	return seq == after_seq + 1 ? 0 : -EPROTO;
}

u32 csid680_e008i_rear_done_count(struct csid_device *csid)
{
	if (!csid || !csid_e004ns_rear_ipp_mode0(csid))
		return 0;
	return READ_ONCE(csid->e008i_rear_done_count);
}

u32 csid680_e008i_rear_done_overflow(struct csid_device *csid)
{
	if (!csid)
		return U32_MAX;
	return READ_ONCE(csid->e008i_rear_done_overflow);
}

u32 csid680_e008i_rear_latch_errors(struct csid_device *csid)
{
	if (!csid)
		return U32_MAX;
	return READ_ONCE(csid->e008i_rear_latch_errors);
}

int csid680_e008i_rear_poll_done(struct csid_device *csid,
				 u32 after_count,
				 unsigned long timeout_us)
{
	u32 count;

	if (!csid || !timeout_us || !csid_e004ns_rear_ipp_mode0(csid) ||
	    !READ_ONCE(csid->e008i_rear_owner_epoch))
		return -EINVAL;

	return read_poll_timeout(READ_ONCE, count, count > after_count, 10,
				 timeout_us, false,
				 csid->e008i_rear_done_count);
}

int csid680_e008i_rear_done_event(struct csid_device *csid,
				  u32 index,
				  struct e008i_rear_done_event *out)
{
	u32 count;

	if (!csid || !out || !csid_e004ns_rear_ipp_mode0(csid))
		return -EINVAL;
	if (READ_ONCE(csid->e008i_rear_done_overflow) ||
	    READ_ONCE(csid->e008i_rear_latch_errors))
		return -EOVERFLOW;

	count = READ_ONCE(csid->e008i_rear_done_count);
	if (index >= count)
		return -ENOENT;

	smp_rmb();
	*out = csid->e008i_rear_done[index];
	if (!out->owner_epoch || out->sequence != index + 1 ||
	    !out->wm_mask || !(out->raw_buf_done_status & E008I_REAR_BUF_DONE_MASK))
		return -EPROTO;
	return 0;
}

static int __used e008i_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif /* CAMSS_CSID_E008I_REAR_OBSERVER_INC */
