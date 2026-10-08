/* SPDX-License-Identifier: GPL-2.0-only */
/* Read-only eligibility observation; keep all four command arenas until stop. */
#ifndef NATIVE_REAR_COMMAND_OBSERVE_INC
#define NATIVE_REAR_COMMAND_OBSERVE_INC
static void
native_rear_command_receipts_observe(struct vfe_device *vfe,
                                    struct csid_device *csid,
                                    const struct e008h_rear_prime_pair *pair,
                                    struct e008k_rear_request *req,
                                    const struct e008k_rear_result *result,
                                    u32 cursor)
{
 struct native_rear_live_observation observation;
 u32 completed = 0;
 unsigned int p, pinned = 0;
 int ret = native_rear_command_receipts_check(req, result, &completed);
 if (!ret)
  ret = native_rear_live_replacement_read(vfe, csid, pair, result, cursor,
                                         &observation);
 if (!ret) {
  const struct e008l_rear_packet_dma *last =
   &req->commands->packet[E007Y_STARTUP_PACKETS - 1];
  ret = e008k_rear_rtcdm_receipt_current(vfe->camss,
                         &last->receipt[last->receipt_count - 1]);
 }
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
  if (req->commands->packet[p].slab_cpu)
   pinned++;
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_COMMAND_RECEIPTS ret=%d packets=%u BL_complete=%u first_seq=1 last_seq=%u command_arenas_pinned=%u live_release=0 rewrite=0 requeue=0\n",
  ret, ret ? 0 : E007Y_STARTUP_PACKETS, completed, completed, pinned);
}
#endif
