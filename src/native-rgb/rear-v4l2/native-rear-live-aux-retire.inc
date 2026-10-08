/* SPDX-License-Identifier: GPL-2.0-only */
/* Retire the first completed request's eight auxiliary output allocations.
 * This finite exclusive runner never programs the old generation again.
 * Command arenas and both ledgers remain owned until physical stop.
 */
#ifndef NATIVE_REAR_LIVE_AUX_RETIRE_INC
#define NATIVE_REAR_LIVE_AUX_RETIRE_INC
static bool
native_rear_live_aux_retired_valid(const struct e008d_rear_dma_set *set,
                                 const struct e007z_rear_frame *frame,
                                 u64 owner)
{
 unsigned int i;
 if (!set || !set->allocated || !set->auxiliary_live_retired ||
     !native_rear_live_full_retired_valid(set, frame, owner))
  return false;
 for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
  if (set->aux[i].cpu || set->aux[i].dma || set->aux[i].size ||
      set->aux[i].wm)
   return false;
 return true;
}

static int
native_rear_live_retire_aux(struct vfe_device *vfe, struct csid_device *csid,
                           struct e008h_rear_prime_pair *pair,
                           struct e008k_rear_result *result, u32 cursor)
{
 struct native_rear_live_observation observation;
 const struct e008d_rear_dma_set *next;
 unsigned int i;
 int ret;
 if (!vfe || !csid || !pair || !result)
  return -EINVAL;
 if (result->live_aux_retired || pair->dma[0].auxiliary_live_retired ||
     pair->dma[1].auxiliary_live_retired)
  return -EALREADY;
 if (!result->both_frames_complete || !result->live_full_retired ||
     !native_rear_live_full_retired_valid(&pair->dma[0], &pair->frame[0],
                                         result->owner_epoch))
  return -EBUSY;
 next = &pair->dma[1];
 if (next->public_full_retired || next->retired_aux_stop_proven ||
     next->retired_owner_epoch || next->retired_request_generation ||
     !native_rear_dma_full_valid(next) || !next->full.in_flight ||
     !next->public_full.exposed || next->public_full.stop_proven ||
     next->public_full.span.y_iova != pair->frame[1].slot[0].owned_base_iova ||
     next->public_full.span.uv_iova != pair->frame[1].slot[1].owned_base_iova ||
     pair->frame[1].slot[0].owned_bytes != NATIVE_REAR_NV12_Y_BYTES ||
     pair->frame[1].slot[1].owned_bytes != NATIVE_REAR_NV12_UV_BYTES)
  return -EPROTO;
 ret = native_rear_live_aux_bindings_check(pair);
 if (ret)
  return ret;
 /* Last guard observes exact completed generations, synchronous command
  * receipts, exclusive owner and all ten replacement WM addresses while live.
  */
 ret = native_rear_live_replacement_read(vfe, csid, pair, result, cursor,
                                        &observation);
 if (ret)
  return ret;
 for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
  e008d_rear_aux_release(vfe, &pair->dma[0].aux[i]);
 pair->dma[0].auxiliary_live_retired = true;
 result->live_aux_retired = true;
 return 0;
}

static void
native_rear_live_retire_aux_observe(struct vfe_device *vfe,
                                   struct csid_device *csid,
                                   struct e008h_rear_prime_pair *pair,
                                   struct e008k_rear_result *result, u32 cursor)
{
 unsigned int i, next_aux_pinned = 0;
 int ret = native_rear_live_retire_aux(vfe, csid, pair, result, cursor);
 for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
  if (pair->dma[1].aux[i].cpu)
   next_aux_pinned++;
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_LIVE_AUX_RETIRE ret=%d released=%u old_valid=%u next_aux_pinned=%u next_FULL_pinned=%u stop_flags=%u vb2_complete=0 requeue=0\n",
  ret, result->live_aux_retired ? E008D_REAR_AUX_COUNT : 0,
  native_rear_live_aux_retired_valid(&pair->dma[0], &pair->frame[0],
                                    result->owner_epoch),
  next_aux_pinned,
  native_rear_video_lease_valid(&pair->dma[1].public_full) &&
    pair->dma[1].full.in_flight,
  (result->csid_quiesced ? 1U : 0U) | (result->bus_stopped ? 2U : 0U) |
  (result->rtcdm_stopped ? 4U : 0U) | (result->source_stopped ? 8U : 0U));
}
#endif
