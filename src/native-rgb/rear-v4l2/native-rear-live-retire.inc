/* SPDX-License-Identifier: GPL-2.0-only */
/* First public FULL mapping retirement under an exclusive rear runner.
 * Both exact ten-WM generations and synchronous replacement BL receipts
 * must complete before unmapping the old attachment. No stop facts are
 * fabricated. Auxiliary buffers stay pinned for physical-stop reclamation;
 * no VB2 completion or address requeue occurs here.
 */
#ifndef NATIVE_REAR_LIVE_RETIRE_INC
#define NATIVE_REAR_LIVE_RETIRE_INC
static bool
native_rear_live_full_retired_valid(const struct e008d_rear_dma_set *set,
                                  const struct e007z_rear_frame *frame,
                                  u64 owner)
{
 const struct native_rear_video_lease *l;
 if (!set || !frame || !owner)
  return false;
 l = &set->public_full;
 return set->public_full_retired && !set->retired_aux_stop_proven &&
        set->retired_owner_epoch == owner &&
        set->retired_request_generation == frame->request_generation &&
        frame->active && !frame->faulted && !frame->pending &&
        frame->owner_epoch == owner && frame->request_generation &&
        !set->full.cpu && !set->full.in_flight &&
        set->full.size == NATIVE_REAR_NV12_BYTES &&
        set->full.dma == frame->slot[0].owned_base_iova &&
        frame->slot[1].owned_base_iova ==
          frame->slot[0].owned_base_iova + NATIVE_REAR_NV12_UV_OFFSET &&
        !l->dbuf && !l->attachment && !l->table &&
        !l->acquired && !l->exposed && !l->stop_proven &&
        !l->span.y_iova && !l->span.uv_iova && !l->span.mapped_bytes;
}

static int
native_rear_live_retire_full(struct vfe_device *vfe, struct csid_device *csid,
                            struct e008h_rear_prime_pair *pair,
                            struct e008k_rear_result *result, u32 cursor)
{
 struct native_rear_live_observation observation;
 struct e008d_rear_dma_set *old, *next;
 unsigned int s, i, other, j;
 int ret;

 if (!vfe || !csid || !pair || !result)
  return -EINVAL;
 if (result->live_full_retired || pair->dma[0].public_full_retired ||
     pair->dma[1].public_full_retired)
  return -EALREADY;
 if (!result->both_frames_complete)
  return -EBUSY;
 for (s = 0; s < E008H_REAR_SLOTS; s++) {
  const struct e008d_rear_dma_set *set = &pair->dma[s];
  const struct native_rear_video_lease *l = &set->public_full;
  const struct e007z_rear_frame *f = &pair->frame[s];
  if (!set->allocated || !native_rear_dma_full_valid(set) ||
      !set->full.in_flight || !l->acquired || !l->exposed ||
      l->stop_proven || set->retired_aux_stop_proven ||
      set->retired_owner_epoch || set->retired_request_generation ||
      l->span.y_iova != f->slot[0].owned_base_iova ||
      l->span.uv_iova != f->slot[1].owned_base_iova ||
      f->slot[0].owned_bytes != NATIVE_REAR_NV12_Y_BYTES ||
      f->slot[1].owned_bytes != NATIVE_REAR_NV12_UV_BYTES)
   return -EPROTO;
  for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {
   const struct e008d_rear_aux_buffer *a = &set->aux[i];
   const struct vfe680_e004nu_rear_wm_static *c =
      e008d_rear_contract_for_wm(a->wm);
   int index = e007z_rear_index(a->wm);

   /* Completion belongs to the ledger's allocation, not merely a WM number.
    * Reject stale/foreign allocations before releasing any mapping.
    */
   if (!c || index < 0 || a->wm != e008d_rear_aux_wms[i] || !a->cpu ||
       a->size != c->frame_incr ||
       (u64)a->dma != f->slot[index].owned_base_iova ||
       a->size != f->slot[index].owned_bytes)
    return -EPROTO;
  }
 }
 /* Every coherent allocation must also have its own CPU identity.
  * Ledger span validation independently checks owned DMA spans.
  */
 for (s = 0; s < E008H_REAR_SLOTS; s++)
  for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
   for (other = 0; other <= s; other++)
    for (j = 0; j < E008D_REAR_AUX_COUNT; j++) {
     if (other == s && j >= i)
      break;
     if (pair->dma[s].aux[i].cpu == pair->dma[other].aux[j].cpu)
      return -EADDRINUSE;
    }
 old = &pair->dma[0];
 next = &pair->dma[1];
 if (old->public_full.dbuf == next->public_full.dbuf ||
     old->public_full.attachment == next->public_full.attachment ||
     old->public_full.table == next->public_full.table)
  return -EADDRINUSE;
 /* Perform the actual live hardware/owner/command observation last.
  * This exclusive finite runner never retargets back to the old addresses.
  */
 ret = native_rear_live_replacement_read(vfe, csid, pair, result, cursor,
                                         &observation);
 if (ret)
  return ret;
 dma_buf_unmap_attachment_unlocked(old->public_full.attachment,
                                   old->public_full.table, DMA_FROM_DEVICE);
 dma_buf_detach(old->public_full.dbuf, old->public_full.attachment);
 dma_buf_put(old->public_full.dbuf);
 memset(&old->public_full, 0, sizeof(old->public_full));
 old->full.in_flight = false;
 old->retired_owner_epoch = result->owner_epoch;
 old->retired_request_generation = pair->frame[0].request_generation;
 old->public_full_retired = true;
 result->live_full_retired = true;
 return 0;
}

static void
native_rear_live_retire_full_observe(struct vfe_device *vfe,
                                    struct csid_device *csid,
                                    struct e008h_rear_prime_pair *pair,
                                    struct e008k_rear_result *result,
                                    u32 cursor)
{
 unsigned int i, aux_pinned = 0;
 int ret = native_rear_live_retire_full(vfe, csid, pair, result, cursor);
 for (i = 0; i < E008D_REAR_AUX_COUNT; i++)
  if (pair->dma[0].aux[i].cpu)
   aux_pinned++;
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_LIVE_FULL_RETIRE ret=%d released=%u old_valid=%u next_pinned=%u aux_pinned=%u stop_flags=%u vb2_complete=0 requeue=0\n",
  ret, result->live_full_retired,
  native_rear_live_full_retired_valid(&pair->dma[0], &pair->frame[0],
                                     result->owner_epoch),
  native_rear_video_lease_valid(&pair->dma[1].public_full) &&
    pair->dma[1].full.in_flight,
  aux_pinned,
  (result->csid_quiesced ? 1U : 0U) | (result->bus_stopped ? 2U : 0U) |
  (result->rtcdm_stopped ? 4U : 0U) | (result->source_stopped ? 8U : 0U));
}
#endif
