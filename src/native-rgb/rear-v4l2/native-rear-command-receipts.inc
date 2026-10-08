/* SPDX-License-Identifier: GPL-2.0-only */
/* Exact serialized command receipts. No live free/rewrite/requeue authority. */
#ifndef NATIVE_REAR_COMMAND_RECEIPTS_INC
#define NATIVE_REAR_COMMAND_RECEIPTS_INC
static int
native_rear_submit_receipted_packet(struct camss *camss,
                                   struct e008k_rear_request *req,
                                   unsigned int packet, u64 owner)
{
 struct e008l_rear_command_set *set;
 struct e008l_rear_packet_dma *p;
 unsigned int i;
 u32 expected = 1;
 int ret;
 if (!camss || !req || !req->commands || !owner ||
     packet >= E007Y_STARTUP_PACKETS)
  return -EINVAL;
 set = req->commands;
 if (set->receipt_faulted)
  return -EIO;
 p = &set->packet[packet];
 if (p->receipt_count || p->receipt_owner || p->receipt_request ||
     p->receipt_slab_cpu || p->receipt_slab_dma || p->receipt_slab_bytes ||
     p->receipt_dmi || p->receipt_dynamic)
  return -EALREADY;
 ret = native_rear_validate_prepared_commands(set);
 if (ret)
  return ret;
 if (!set->hardware_exposed ||
     req->packet_request_id[packet] != set->packet_request_id[packet])
  return -ESTALE;
 for (i = 0; i < E007Y_MAX_BL; i++)
  if (p->receipt[i].sequence || p->receipt[i].dma ||
      p->receipt[i].bytes || p->receipt[i].irq_status ||
      p->receipt[i].complete)
   return -EALREADY;
 if (packet) {
  struct e008l_rear_packet_dma *prior = &set->packet[packet - 1];
  if (prior->receipt_count != prior->out.bl_count ||
      !prior->receipt_count || prior->receipt_owner != owner ||
      prior->receipt[prior->receipt_count - 1].sequence == U32_MAX)
   return -ESTALE;
  expected = prior->receipt[prior->receipt_count - 1].sequence + 1;
 }
 p->receipt_owner = owner;
 p->receipt_request = set->packet_request_id[packet];
 p->receipt_slab_cpu = p->slab_cpu;
 p->receipt_slab_dma = p->slab_dma;
 p->receipt_slab_bytes = p->slab_bytes;
 p->receipt_dmi = p->dmi;
 p->receipt_dynamic = p->dynamic;
 for (i = 0; i < p->out.bl_count; i++) {
  struct native_rear_bl_receipt receipt = {0};
  ret = e008k_rear_rtcdm_submit_bl_receipt(camss, p->out.bl[i].dma,
                                         p->out.bl[i].bytes, &receipt);
  if (ret || !receipt.complete || receipt.sequence != expected ||
      receipt.dma != p->out.bl[i].dma ||
      receipt.bytes != p->out.bl[i].bytes ||
      !native_rear_bl_status_valid(receipt.irq_status)) {
   set->receipt_faulted = true; /* A touched FIFO never retries. */
   return ret ? ret : -EPROTO;
  }
  p->receipt[i] = receipt;
  p->receipt_count++;
  expected++;
 }
 return 0;
}

static int
native_rear_command_receipts_check(const struct e008k_rear_request *req,
                                  const struct e008k_rear_result *result,
                                  u32 *completed)
{
 const struct e008l_rear_command_set *set;
 u32 sequence = 1, count = 0;
 unsigned int p, i;
 int ret;
 if (!completed)
  return -EINVAL;
 *completed = 0;
 if (!req || !req->commands || !result || !result->owner_epoch)
  return -EINVAL;
 set = req->commands;
 if (set->receipt_faulted || !set->hardware_exposed)
  return -EIO;
 ret = native_rear_validate_prepared_commands(set);
 if (ret)
  return ret;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
  const struct e008l_rear_packet_dma *a = &set->packet[p];
  if (!result->packet_submitted[p] ||
      req->packet_request_id[p] != set->packet_request_id[p] ||
      a->receipt_owner != result->owner_epoch ||
      a->receipt_request != set->packet_request_id[p] ||
      a->receipt_slab_cpu != a->slab_cpu ||
      a->receipt_slab_dma != a->slab_dma ||
      a->receipt_slab_bytes != a->slab_bytes ||
      a->receipt_dmi != a->dmi || a->receipt_dynamic != a->dynamic ||
      a->receipt_count != a->out.bl_count)
   return -ESTALE;
  for (i = 0; i < E007Y_MAX_BL; i++) {
   const struct native_rear_bl_receipt *r = &a->receipt[i];
   if (i >= a->out.bl_count) {
    if (r->sequence || r->dma || r->bytes || r->irq_status || r->complete)
     return -EPROTO;
    continue;
   }
   if (!r->complete || r->sequence != sequence++ ||
       r->dma != a->out.bl[i].dma || r->bytes != a->out.bl[i].bytes ||
       !native_rear_bl_status_valid(r->irq_status))
    return -EPROTO;
   count++;
  }
 }
 if (count != 22)
  return -EPROTO;
 *completed = count;
 return 0;
}
#endif
