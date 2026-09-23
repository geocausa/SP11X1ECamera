/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E004nv: rear six-group candidate based on same-SP11 OEM driver event
 * dispatch (qccamisp8380.sys SHA64463b4d...) AND Windows rear VFE1 WM16.
 * Source-only, no caller. STATIC driver event branch does NOT prove BF
 * event was exercised in a live rear stream, or that metadata is valid.
 *
 * E004nu's per-WM pending mask is retained as a conservative allocator
 * safety model. OEM Windows uses independent per-GROUP FIFOs, so retire
 * a set of write masters together ONLY after a source-backed group event.
 */
#ifndef VFE680_E004NV_REAR_SIX_GROUP_INC
#define VFE680_E004NV_REAR_SIX_GROUP_INC

#define VFE680_E004NV_REAR_GROUP_COUNT		6U
#define VFE680_E004NV_VIDEO_WM_MASK		0x000fU
#define VFE680_E004NV_AEC_BHIST_WM_MASK		0x0030U
#define VFE680_E004NV_TINTLESS_WM_MASK		0x0040U
#define VFE680_E004NV_AWB_WM_MASK		0x0080U
#define VFE680_E004NV_BF_WM16_MASK		0x0100U
#define VFE680_E004NV_RS_WM_MASK		0x0200U

/* Event ID->FIFO index is proven by qccamisp8380.sys disassembly.
 * The assignment of rear-only group8 BF to active WM16 BAF is a static
 * association; a live rear BF completion has NOT yet been captured.
 */
struct vfe680_e004nv_rear_group {
	u8 event_id;
	u8 fifo_index;
	u16 wm_mask;
};

static const struct vfe680_e004nv_rear_group
vfe680_e004nv_rear_groups[VFE680_E004NV_REAR_GROUP_COUNT] __used = {
	{ .event_id = 0x03U, .fifo_index = 0U,
	  .wm_mask = VFE680_E004NV_VIDEO_WM_MASK },
	{ .event_id = 0x0dU, .fifo_index = 5U,
	  .wm_mask = VFE680_E004NV_AEC_BHIST_WM_MASK },
	{ .event_id = 0x0eU, .fifo_index = 6U,
	  .wm_mask = VFE680_E004NV_TINTLESS_WM_MASK },
	{ .event_id = 0x10U, .fifo_index = 7U,
	  .wm_mask = VFE680_E004NV_AWB_WM_MASK },
	{ .event_id = 0x0fU, .fifo_index = 8U,
	  .wm_mask = VFE680_E004NV_BF_WM16_MASK },
	{ .event_id = 0x12U, .fifo_index = 9U,
	  .wm_mask = VFE680_E004NV_RS_WM_MASK },
};
static_assert(ARRAY_SIZE(vfe680_e004nv_rear_groups) ==
	      VFE680_E004NV_REAR_GROUP_COUNT);
static_assert((VFE680_E004NV_VIDEO_WM_MASK |
	       VFE680_E004NV_AEC_BHIST_WM_MASK |
	       VFE680_E004NV_TINTLESS_WM_MASK |
	       VFE680_E004NV_AWB_WM_MASK |
	       VFE680_E004NV_BF_WM16_MASK |
	       VFE680_E004NV_RS_WM_MASK) ==
	      VFE680_E004NU_REAR_CLIENTS_MASK);

/* Offline-only mapping. Do not fabricate six independent hardware
 * WM interrupts from the single aggregated VIDEO or BF group event.
 */
static int __used
vfe680_e004nv_rear_group_for_event(u8 event_id,
				   const struct vfe680_e004nv_rear_group **group)
{
	unsigned int i;

	if (!group)
		return -EINVAL;
	*group = NULL;
	for (i = 0; i < ARRAY_SIZE(vfe680_e004nv_rear_groups); i++) {
		if (vfe680_e004nv_rear_groups[i].event_id == event_id) {
			*group = &vfe680_e004nv_rear_groups[i];
			return 0;
		}
	}
	return -ENOENT;
}

/* This models ONLY logical ownership after an independently verified
 * event ID has been obtained. There is NO active ISR or hardware caller.
 * All clients in a group are retired together, regardless of order of
 * arrival among different groups. Repeated/unknown events fail closed.
 */
static int __used
vfe680_e004nv_rear_frame_ack_group(struct vfe680_e004nu_rear_frame *frame,
				   u8 verified_event_id)
{
	const struct vfe680_e004nv_rear_group *group;
	int ret;

	if (!frame || !frame->active || !frame->surface ||
	    !frame->surface->in_flight)
		return -EINVAL;
	ret = vfe680_e004nv_rear_group_for_event(verified_event_id, &group);
	if (ret)
		return ret;
	if ((frame->pending & group->wm_mask) != group->wm_mask)
		return -EALREADY;

	frame->pending &= ~group->wm_mask;
	return 0;
}

/* Reuse E004nu's conservative all-client plus independent BUS-stop
 * requirement; a guessed stop Boolean is never sufficient in a live
 * kernel and no such source-backed caller exists yet.
 */
static int __used
vfe680_e004nv_rear_frame_retire(struct vfe680_e004nu_rear_frame *frame,
				bool independently_verified_bus_stopped)
{
	return vfe680_e004nu_rear_frame_retire(
		frame, independently_verified_bus_stopped);
}

static int __used
vfe680_e004nv_rear_runtime_authorization(struct vfe_device *vfe)
{
	if (!vfe680_e004nt_rear_4k_target(vfe))
		return -EINVAL;

	/* No live rear BF group8 event, no group FIFO HW validation, no
	 * rear RT-CDM/IQ/3A and no safe rollback: never arm the ISP.
	 */
	return -EOPNOTSUPP;
}
#endif /* VFE680_E004NV_REAR_SIX_GROUP_INC */
