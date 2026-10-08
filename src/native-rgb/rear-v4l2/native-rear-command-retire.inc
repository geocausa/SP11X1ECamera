/* SPDX-License-Identifier: GPL-2.0-only */
/* Finite exclusive rear transaction: retire all completed startup commands.
 * No command resubmission, ledger reuse, early VB2 delivery or address requeue.
 */
#ifndef NATIVE_REAR_COMMAND_RETIRE_INC
#define NATIVE_REAR_COMMAND_RETIRE_INC
struct native_rear_command_cpu_span { const void *cpu; size_t bytes; };

static int
native_rear_command_allocations_check(const struct e008k_rear_request *req,
                                     const struct e008h_rear_prime_pair *pair,
                                     u64 owner)
{
 struct native_rear_command_cpu_span spans[E007Y_STARTUP_PACKETS * 3];
 unsigned int p, i, s, j, count = 0;
 int ret;
 if (!req || !req->commands || !pair || !owner)
  return -EINVAL;
 if (req->commands->live_retired || req->commands->retired_owner ||
     req->commands->retired_BL_count ||
     !native_rear_command_zero(&req->commands->retired_last,
                               sizeof(req->commands->retired_last)))
  return -EPROTO;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
  const struct e008l_rear_packet_dma *a = &req->commands->packet[p];
  size_t expected;
  ret = e008l_rear_packet_sizing(p, &expected);
  if (ret)
   return ret;
  if (a->slab_bytes != expected || !a->slab_dma ||
      !vfe680_x1e_dma_span_32bit(a->slab_dma, a->slab_bytes) ||
      a->out.dmi_count != e007y_startup_variants[p].dmi_count)
   return -EPROTO;
  spans[count++] = (struct native_rear_command_cpu_span){a->slab_cpu, a->slab_bytes};
  spans[count++] = (struct native_rear_command_cpu_span){a->dmi,
                                      a->out.dmi_count * sizeof(*a->dmi)};
  spans[count++] = (struct native_rear_command_cpu_span){a->dynamic, sizeof(*a->dynamic)};
  for (s = 0; s < E008H_REAR_SLOTS; s++) {
   const struct e008d_rear_dma_set *set = &pair->dma[s];
   const struct e007z_rear_frame *frame = &pair->frame[s];
   if (!set->allocated || frame->owner_epoch != owner)
    return -ESTALE;
   for (j = 0; j < E007Z_REAR_WMS; j++)
    if (e007z_rear_spans_overlap(a->slab_dma, a->slab_bytes,
                     frame->slot[j].owned_base_iova, frame->slot[j].owned_bytes))
     return -EADDRINUSE;
   if (!set->public_full_retired) {
    if (!native_rear_dma_full_valid(set) ||
        !vfe680_x1e_dma_span_32bit(set->full.dma,
                                 set->public_full.span.mapped_bytes))
     return -EPROTO;
    if (e007z_rear_spans_overlap(a->slab_dma, a->slab_bytes,
                               set->full.dma, set->public_full.span.mapped_bytes))
     return -EADDRINUSE;
   }
  }
 }
 /* All twelve CPU allocations are independent, including cross-type aliases. */
 for (i = 0; i < count; i++)
  for (j = 0; j < i; j++)
   if (native_rear_memory_overlap(spans[i].cpu, spans[i].bytes,
                                 spans[j].cpu, spans[j].bytes))
    return -EADDRINUSE;
 for (s = 0; s < E008H_REAR_SLOTS; s++) {
  const struct e008d_rear_dma_set *set = &pair->dma[s];
  const struct e007z_rear_frame *frame = &pair->frame[s];
  if (set->auxiliary_live_retired) {
   if (s != 0 || !native_rear_live_aux_retired_valid(set, frame, owner))
    return -EPROTO;
   continue;
  }
  for (j = 0; j < E008D_REAR_AUX_COUNT; j++) {
   const struct e008d_rear_aux_buffer *aux = &set->aux[j];
   const struct vfe680_e004nu_rear_wm_static *c =
    e008d_rear_contract_for_wm(aux->wm);
   int index = e007z_rear_index(aux->wm);
   if (!c || index < 0 || aux->wm != e008d_rear_aux_wms[j] || !aux->cpu ||
       aux->size != c->frame_incr || aux->dma != frame->slot[index].owned_base_iova ||
       aux->size != frame->slot[index].owned_bytes)
    return -EPROTO;
   for (i = 0; i < count; i++)
    if (native_rear_memory_overlap(spans[i].cpu, spans[i].bytes,
                                  aux->cpu, aux->size))
     return -EADDRINUSE;
  }
 }
 /* Reject aliases before dereferencing command descriptor allocations. */
 return native_rear_validate_prepared_commands(req->commands);
}

static int
native_rear_live_retire_commands(struct vfe_device *vfe, struct csid_device *csid,
                                struct e008h_rear_prime_pair *pair,
                                struct e008k_rear_request *req,
                                struct e008k_rear_result *result, u32 cursor)
{
 struct native_rear_live_observation observation;
 struct native_rear_bl_receipt last;
 struct e008l_rear_command_set *set;
 u32 completed = 0;
 unsigned int p;
 int ret;
 if (!vfe || !vfe->camss || !csid || !pair || !req ||
     !req->commands || !result)
  return -EINVAL;
 set = req->commands;
 if (result->live_commands_retired || set->live_retired)
  return -EALREADY;
 if (!result->both_frames_complete || !result->live_full_retired ||
     !result->live_aux_retired ||
     !native_rear_live_aux_retired_valid(&pair->dma[0], &pair->frame[0],
                                         result->owner_epoch))
  return -EBUSY;
 ret = native_rear_command_allocations_check(req, pair, result->owner_epoch);
 if (ret)
  return ret;
 ret = native_rear_command_receipts_check(req, result, &completed);
 if (ret)
  return ret;
 last = set->packet[E007Y_STARTUP_PACKETS - 1].receipt[5];
 ret = native_rear_live_replacement_read(vfe, csid, pair, result, cursor,
                                        &observation);
 if (ret)
  return ret;
 ret = e008k_rear_rtcdm_receipt_current(vfe->camss, &last);
 if (ret)
  return ret;
 /* All guards precede the first release; this runner never submits again. */
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
  e008l_rear_packet_release(vfe, &set->packet[p]);
 set->retired_owner = result->owner_epoch;
 set->retired_BL_count = completed;
 set->retired_last = last;
 set->live_retired = true;
 result->live_commands_retired = true;
 return 0;
}

static void
native_rear_live_retire_commands_observe(struct vfe_device *vfe,
                                        struct csid_device *csid,
                                        struct e008h_rear_prime_pair *pair,
                                        struct e008k_rear_request *req,
                                        struct e008k_rear_result *result,
                                        u32 cursor)
{
 unsigned int p, pinned = 0;
 int ret = native_rear_live_retire_commands(vfe, csid, pair, req, result, cursor);
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
  if (req->commands->packet[p].slab_cpu)
   pinned++;
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_COMMAND_RETIRE ret=%d released=%u retired_valid=%u command_arenas_pinned=%u owner=%llu BL_complete=%u stop_flags=%u vb2_complete=0 requeue=0\n",
  ret, result->live_commands_retired ? E007Y_STARTUP_PACKETS : 0,
  native_rear_live_commands_retired_valid(req->commands, result->owner_epoch),
  pinned, result->owner_epoch, req->commands->retired_BL_count,
  (result->csid_quiesced ? 1U : 0U) | (result->bus_stopped ? 2U : 0U) |
  (result->rtcdm_stopped ? 4U : 0U) | (result->source_stopped ? 8U : 0U));
}
#endif
