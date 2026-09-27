/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef CAMSS_E008I_REAR_OBSERVER_H
#define CAMSS_E008I_REAR_OBSERVER_H

#include <linux/types.h>

#define E008I_REAR_WMS			10U
#define E008I_REAR_DONE_DEPTH		16U
#define E008I_REAR_BUF_DONE_MASK	0x000002f1U

struct csid_device;
struct vfe_device;

struct e008i_rear_done_event {
	u64 owner_epoch;
	u32 sequence;
	u32 raw_buf_done_status;
	u16 wm_mask;
	u16 reserved;
	u32 addr_status0[E008I_REAR_WMS];
};

int vfe680_e008i_rear_snapshot_addr_status0(struct vfe_device *vfe,
					    u32 buf_done_status,
					    u16 *wm_mask,
					    u32 addr_status0[E008I_REAR_WMS]);

int csid680_e008i_rear_reset(struct csid_device *csid, u64 owner_epoch);
u32 csid680_e008i_rear_epoch0_seq(struct csid_device *csid);
int csid680_e008i_rear_poll_next_epoch0(struct csid_device *csid,
					u32 after_seq,
					unsigned long timeout_us);
u32 csid680_e008i_rear_done_count(struct csid_device *csid);
u32 csid680_e008i_rear_done_overflow(struct csid_device *csid);
u32 csid680_e008i_rear_latch_errors(struct csid_device *csid);
int csid680_e008i_rear_poll_done(struct csid_device *csid,
				 u32 after_count,
				 unsigned long timeout_us);
int csid680_e008i_rear_done_event(struct csid_device *csid,
				  u32 index,
				  struct e008i_rear_done_event *out);

#endif /* CAMSS_E008I_REAR_OBSERVER_H */
