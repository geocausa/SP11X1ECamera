/* SPDX-License-Identifier: GPL-2.0-only */
/* Persistent exclusive rear output queue with fixed startup ISP policy.
 * A generation is delivered only after all10 replacement consumed addresses
 * prove that the ISP has moved on. Startup commands are already retired.
 */
#ifndef NATIVE_REAR_QUEUE_INC
#define NATIVE_REAR_QUEUE_INC

static void native_rear_queue_complete(struct camss_video *video,
                                       unsigned int slot, bool live, bool success)
{
 struct camss_buffer *buffer = video->native_rear_inflight[slot];
 if (!buffer)
  return;
 video->native_rear_inflight[slot] = NULL; /* Before callback/requeue. */
 if (success) {
  vb2_set_plane_payload(&buffer->vb.vb2_buf, 0, NATIVE_REAR_NV12_BYTES);
  buffer->vb.sequence = video->native_rear_completed++;
  buffer->vb.vb2_buf.timestamp = ktime_get_ns();
  if (live)
   video->native_rear_live_completed++;
  vb2_buffer_done(&buffer->vb.vb2_buf, VB2_BUF_STATE_DONE);
 } else {
  vb2_buffer_done(&buffer->vb.vb2_buf, VB2_BUF_STATE_ERROR);
 }
}

static int
native_rear_queue_drain(struct csid_device *csid, struct e008h_rear_prime_pair *pair,
                        u64 owner, u32 *cursor)
{
 u32 count;
 int ret;
 if (csid680_e008i_rear_done_overflow(csid) ||
     csid680_e008i_rear_latch_errors(csid))
  return -EOVERFLOW;
 count = csid680_e008i_rear_done_count(csid);
 while (*cursor < count) {
  struct e008i_rear_done_event event;
  unsigned int i;
  ret = csid680_e008i_rear_done_event(csid, *cursor, &event);
  if (ret)
   return ret;
  if (event.owner_epoch != owner)
   return -ESTALE;
  for (i = 0; i < E008I_REAR_WMS; i++) {
   if (!(event.wm_mask & BIT(i)))
    continue;
   ret = e008h_rear_observe_consumed(pair, owner, event.raw_buf_done_status,
                                    e008i_rear_wm[i], event.addr_status0[i]);
   if (ret && ret != -EALREADY)
    return ret;
  }
  ret = csid680_e008i_rear_retire_event(csid, *cursor, owner);
  if (ret)
   return ret;
  (*cursor)++;
 }
 return 0;
}

/* All retained FULL mapping tails and coherent allocations are disjoint,
 * not merely their image portions. No allocation has been exposed yet.
 */
static int native_rear_queue_allocations_check(struct e008h_rear_prime_pair *pair)
{
 unsigned int s, i, other, j;
 int ret = e008h_rear_validate_pair_disjoint(pair);
 if (ret)
  return ret;
 for (s = 0; s < 2; s++) {
  const struct e008d_rear_dma_set *d = &pair->dma[s];
  const struct native_rear_video_lease *l = &d->public_full;
  if (!native_rear_dma_full_valid(d) ||
      !vfe680_x1e_dma_span_32bit(d->full.dma, l->span.mapped_bytes))
   return -EPROTO;
  if (pair->dma[0].public_full.dbuf == pair->dma[1].public_full.dbuf)
   return -EADDRINUSE;
  for (other = 0; other < 2; other++) {
   const struct e007z_rear_frame *frame = &pair->frame[other];
   for (i = 0; i < E007Z_REAR_WMS; i++) {
    if (s == other && i < 2)
     continue; /* Y/UV are the two portions of this FULL mapping. */
    if (e007z_rear_spans_overlap(d->full.dma, l->span.mapped_bytes,
              frame->slot[i].owned_base_iova, frame->slot[i].owned_bytes))
     return -EADDRINUSE;
   }
  }
  for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {
   const struct e008d_rear_aux_buffer *a = &d->aux[i];
   const struct vfe680_e004nu_rear_wm_static *c = e008d_rear_contract_for_wm(a->wm);
   int index = e007z_rear_index(a->wm);
   if (!c || index < 0 || a->wm != e008d_rear_aux_wms[i] || !a->cpu ||
       a->size != c->frame_incr || a->dma != pair->frame[s].slot[index].owned_base_iova ||
       a->size != pair->frame[s].slot[index].owned_bytes)
    return -EPROTO;
   for (other = 0; other <= s; other++)
    for (j = 0; j < E008D_REAR_AUX_COUNT; j++) {
     if (other == s && j >= i)
      break;
     if (native_rear_memory_overlap(a->cpu, a->size,
                     pair->dma[other].aux[j].cpu, pair->dma[other].aux[j].size))
      return -EADDRINUSE;
    }
  }
 }
 return 0;
}

/* Only the zero-allocation retired old slot may be replaced. The current
 * complete generation is copied without releasing its mapping or ledger.
 */
static int native_rear_queue_prepare(struct vfe_device *vfe,
                                     const struct e008h_rear_prime_pair *pair,
                                     struct e008h_rear_prime_pair *next,
                                     struct camss_buffer *buffer, u64 owner)
{
 struct e007z_rear_binding bindings[E007Z_REAR_WMS];
 int ret;
 if (!vfe || !pair || !next || !buffer || !owner || !pair->enabled ||
     pair->faulted || !pair->ledgers_bound ||
     !native_rear_live_aux_retired_valid(&pair->dma[0], &pair->frame[0], owner) ||
     !e008h_rear_both_complete(pair, owner) ||
     pair->frame[1].request_generation >= U64_MAX - 1)
  return -EBUSY;
 memset(next, 0, sizeof(*next));
 next->dma[0] = pair->dma[1];
 next->addr[0] = pair->addr[1];
 next->frame[0] = pair->frame[1];
 next->allocated = next->enabled = next->ledgers_bound = true;
 next->slot0_preloaded_disabled = pair->slot0_preloaded_disabled;
 next->programmed[0] = true;
 ret = native_rear_public_dma_alloc(vfe, &next->dma[1], buffer);
 if (ret)
  return ret;
 ret = e008d_rear_build_addresses(vfe, &next->dma[1], &next->addr[1]);
 if (ret)
  goto fail;
 ret = e008h_rear_build_binding(next, 1, bindings);
 if (ret)
  goto fail;
 ret = e007z_rear_bind(&next->frame[1], owner,
                      next->frame[0].request_generation + 1, bindings);
 if (ret)
  goto fail;
 ret = native_rear_queue_allocations_check(next);
 if (ret)
  goto fail;
 return 0;
fail:
 /* Only the fresh unexposed set belongs to this cleanup path. */
 e008d_rear_release_partial(vfe, &next->dma[1]);
 memset(&next->dma[0], 0, sizeof(next->dma[0])); /* Copied, not owned. */
 return ret;
}

static int
native_rear_queue_run(struct vfe_device *vfe, struct csid_device *csid,
                      struct e008h_rear_prime_pair *pair,
                      struct e008k_rear_request *req,
                      struct e008k_rear_result *result, u32 *cursor)
{
 struct camss_video *video = &vfe->line[VFE_LINE_PIX].video_out;
 struct e008h_rear_prime_pair *next;
 struct native_rear_live_observation observation;
 struct camss_buffer *buffer;
 unsigned int idle = 0;
 int ret;
 if (!req->public_video[0] || !result->live_commands_retired ||
     !native_rear_live_commands_retired_valid(req->commands, result->owner_epoch) ||
     !result->live_full_retired || !result->live_aux_retired ||
     !native_rear_live_aux_retired_valid(&pair->dma[0], &pair->frame[0],
                                         result->owner_epoch) ||
     !video->native_rear_inflight[0] || !video->native_rear_inflight[1])
  return -EPROTO;
 ret = native_rear_queue_drain(csid, pair, result->owner_epoch, cursor);
 if (ret)
  return ret;
 ret = native_rear_live_replacement_read(vfe, csid, pair, result, *cursor, &observation);
 if (ret)
  return ret;
 native_rear_queue_complete(video, 0, true, true);
 next = kzalloc(sizeof(*next), GFP_KERNEL);
 if (!next)
  return -ENOMEM;
 for (;;) {
  unsigned long flags;
  u32 epoch;
  if (video->native_rear_completed == U32_MAX) {
   ret = -EOVERFLOW;
   break;
  }
  /* Service IRQ records even under starvation; no silent event overflow. */
  ret = native_rear_queue_drain(csid, pair, result->owner_epoch, cursor);
  if (ret)
   break;
  if (READ_ONCE(video->x1e_pix_stop_requested)) {
   ret = 0;
   break;
  }
  spin_lock_irqsave(&vfe->output_lock, flags);
  buffer = vfe_buf_get_pending(&vfe->line[VFE_LINE_PIX].output);
  spin_unlock_irqrestore(&vfe->output_lock, flags);
  if (!buffer) {
   if (++idle >= 1000) {
    result->queue_starved = true;
    ret = 0; /* Complete current evidence permits ordinary four-stage stop. */
    break;
   }
   usleep_range(500, 1000);
   continue;
  }
  idle = 0;
  if (buffer == video->native_rear_inflight[1]) {
   /* Return only through the worker; never publish twice. */
   ret = -EADDRINUSE;
   break;
  }
  video->native_rear_inflight[0] = buffer;
  ret = native_rear_queue_prepare(vfe, pair, next, buffer, result->owner_epoch);
  if (ret)
   break;
  /* Drain and re-observe the current target before dropping the old ledger.
   * Allocator reuse of a retired address cannot consume stale queued events.
   */
  ret = native_rear_queue_drain(csid, pair, result->owner_epoch, cursor);
  if (!ret)
   ret = native_rear_live_replacement_read(vfe, csid, pair, result, *cursor, &observation);
  if (ret) {
   e008d_rear_release_partial(vfe, &next->dma[1]);
   break;
  }
  epoch = csid680_e008i_rear_epoch0_seq(csid);
  ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch, req->epoch_timeout_us);
  if (ret) {
   e008d_rear_release_partial(vfe, &next->dma[1]);
   break;
  }
  /* Move ownership once. Any subsequent exposure failure remains pinned. */
  *pair = *next;
  memset(next, 0, sizeof(*next));
  video->native_rear_inflight[0] = video->native_rear_inflight[1];
  video->native_rear_inflight[1] = buffer;
  result->live_full_retired = result->live_aux_retired = false;
  result->both_frames_complete = false;
  ret = native_rear_video_lease_expose(&pair->dma[1].public_full);
  if (ret)
   break;
  pair->programmed[1] = true; /* Any partial MMIO exposure stays tracked. */
  pair->dma[1].full.in_flight = true;
  ret = e008h_rear_write_slot_addresses(vfe, pair, 1);
  if (!ret)
   ret = e008h_rear_check_slot_addresses(vfe, pair, 1, true);
  if (ret) {
   pair->faulted = true;
   break;
  }
  ret = csid680_native_rear_output_update(csid, result->owner_epoch);
  if (ret)
   break;
  result->queue_updates++;
  result->queue_handoffs++;
  ret = e008k_rear_collect_done(csid, pair, result->owner_epoch,
                               req->done_timeout_us, cursor);
  if (ret)
   break;
  result->both_frames_complete = true;
  ret = native_rear_live_retire_full(vfe, csid, pair, result, *cursor);
  if (!ret)
   ret = native_rear_live_retire_aux(vfe, csid, pair, result, *cursor);
  if (ret)
   break;
  native_rear_queue_complete(video, 0, true, true);
  result->epoch0_seq = csid680_e008i_rear_epoch0_seq(csid);
  result->done_events = *cursor;
  if (result->queue_handoffs == U32_MAX) {
   ret = -EOVERFLOW;
   break;
  }
 }
 kfree(next);
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_QUEUE ret=%d live_completed=%u handoffs=%u output_updates=%u cursor=%u starved=%u command_resubmissions=0 cpu_pixel_copy=0\n",
  ret, video->native_rear_live_completed, result->queue_handoffs, result->queue_updates, *cursor, result->queue_starved);
 return ret;
}
#endif
