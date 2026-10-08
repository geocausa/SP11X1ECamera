/* SPDX-License-Identifier: GPL-2.0-only */
/* Rear completion event queue: one IRQ producer and one runner consumer.
 * Release/acquire publication protects complete scalar snapshots. A slot is
 * reused only after the runner consumes its exact sequence/owner event.
 * Overflow or malformed history is fatal; this grants no live image DMA
 * retirement and does not alter any hardware IRQ acknowledgement.
 */
#ifndef NATIVE_REAR_EVENT_QUEUE_INC
#define NATIVE_REAR_EVENT_QUEUE_INC

static void e008i_rear_latch_buf_done(struct csid_device *csid, u32 status)
{
 struct e008i_rear_done_event *evt;
 u64 owner;
 u32 produced, consumed;
 int ret;
 if (!csid_e004ns_rear_ipp_mode0(csid) ||
     !(status & E008I_REAR_BUF_DONE_MASK))
  return;
 owner = READ_ONCE(csid->e008i_rear_owner_epoch);
 produced = READ_ONCE(csid->e008i_rear_done_count);
 consumed = smp_load_acquire(&csid->native_rear_done_consumed);
 if (!owner || produced == U32_MAX || consumed > produced ||
     produced - consumed >= E008I_REAR_DONE_DEPTH) {
  WRITE_ONCE(csid->e008i_rear_done_overflow,
             READ_ONCE(csid->e008i_rear_done_overflow) + 1);
  return;
 }
 evt = &csid->e008i_rear_done[produced % E008I_REAR_DONE_DEPTH];
 evt->owner_epoch = owner;
 evt->sequence = produced + 1;
 evt->raw_buf_done_status = status;
 evt->wm_mask = 0;
 evt->reserved = 0;
 ret = vfe680_e008i_rear_snapshot_addr_status0(&csid->camss->vfe[1],
           status, &evt->wm_mask, evt->addr_status0);
 if (ret) {
  WRITE_ONCE(csid->e008i_rear_latch_errors,
             READ_ONCE(csid->e008i_rear_latch_errors) + 1);
  memset(evt, 0, sizeof(*evt));
  return;
 }
 smp_store_release(&csid->e008i_rear_done_count, produced + 1);
}
static void e008i_rear_latch_ipp(struct csid_device *csid, u32 status)
{
 u32 count;
 if (!csid_e004ns_rear_ipp_mode0(csid) || !(status & CSID_IPP_CAMIF_EPOCH0))
  return;
 count = READ_ONCE(csid->e008i_rear_epoch0_count);
 if (count == U32_MAX) {
  WRITE_ONCE(csid->e008i_rear_latch_errors,
             READ_ONCE(csid->e008i_rear_latch_errors) + 1);
  return;
 }
 WRITE_ONCE(csid->e008i_rear_epoch0_count, count + 1);
}
int csid680_e008i_rear_reset(struct csid_device *csid, u64 owner)
{
 if (!csid || !csid_e004ns_rear_ipp_mode0(csid) || !owner || !csid->irq)
  return -EINVAL;
 /* Existing contract: exclusive owner, before rear IRQ masks are armed. */
 synchronize_irq(csid->irq);
 memset(csid->e008i_rear_done, 0, sizeof(csid->e008i_rear_done));
 WRITE_ONCE(csid->e008i_rear_owner_epoch, owner);
 WRITE_ONCE(csid->e008i_rear_epoch0_count, 0);
 WRITE_ONCE(csid->e008i_rear_done_count, 0);
 WRITE_ONCE(csid->native_rear_done_consumed, 0);
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
                                     u32 after, unsigned long timeout)
{
 u32 count;
 int ret;
 if (!csid || !timeout || !csid_e004ns_rear_ipp_mode0(csid) ||
     !READ_ONCE(csid->e008i_rear_owner_epoch))
  return -EINVAL;
 if (after == U32_MAX || READ_ONCE(csid->e008i_rear_done_overflow) ||
     READ_ONCE(csid->e008i_rear_latch_errors))
  return -EOVERFLOW;
 ret = read_poll_timeout(READ_ONCE, count, count != after, 10, timeout,
                        false, csid->e008i_rear_epoch0_count);
 if (ret)
  return ret;
 if (READ_ONCE(csid->e008i_rear_done_overflow) ||
     READ_ONCE(csid->e008i_rear_latch_errors))
  return -EOVERFLOW;
 return count == after + 1 ? 0 : -EPROTO;
}
u32 csid680_e008i_rear_done_count(struct csid_device *csid)
{
 if (!csid || !csid_e004ns_rear_ipp_mode0(csid))
  return 0;
 return smp_load_acquire(&csid->e008i_rear_done_count);
}
u32 csid680_e008i_rear_done_overflow(struct csid_device *csid)
{
 return csid ? READ_ONCE(csid->e008i_rear_done_overflow) : U32_MAX;
}
u32 csid680_e008i_rear_latch_errors(struct csid_device *csid)
{
 return csid ? READ_ONCE(csid->e008i_rear_latch_errors) : U32_MAX;
}
int csid680_e008i_rear_poll_done(struct csid_device *csid, u32 after,
                               unsigned long timeout)
{
 u32 count;
 int ret;
 if (!csid || !timeout || !csid_e004ns_rear_ipp_mode0(csid) ||
     !READ_ONCE(csid->e008i_rear_owner_epoch))
  return -EINVAL;
 if (after == U32_MAX || READ_ONCE(csid->e008i_rear_done_overflow) ||
     READ_ONCE(csid->e008i_rear_latch_errors))
  return -EOVERFLOW;
 ret = read_poll_timeout(smp_load_acquire, count, count > after, 10, timeout,
                        false, &csid->e008i_rear_done_count);
 if (ret)
  return ret;
 return READ_ONCE(csid->e008i_rear_done_overflow) ||
        READ_ONCE(csid->e008i_rear_latch_errors) ? -EOVERFLOW : 0;
}
int csid680_e008i_rear_done_event(struct csid_device *csid, u32 index,
                                struct e008i_rear_done_event *out)
{
 u32 count, consumed;
 if (!csid || !out || !csid_e004ns_rear_ipp_mode0(csid))
  return -EINVAL;
 if (READ_ONCE(csid->e008i_rear_done_overflow) ||
     READ_ONCE(csid->e008i_rear_latch_errors))
  return -EOVERFLOW;
 count = smp_load_acquire(&csid->e008i_rear_done_count);
 consumed = READ_ONCE(csid->native_rear_done_consumed);
 if (consumed > count || count - consumed > E008I_REAR_DONE_DEPTH)
  return -EPROTO;
 if (index < consumed)
  return -ESTALE;
 if (index >= count)
  return -ENOENT;
 *out = csid->e008i_rear_done[index % E008I_REAR_DONE_DEPTH];
 if (!out->owner_epoch || out->owner_epoch != READ_ONCE(csid->e008i_rear_owner_epoch) ||
     out->sequence != index + 1 || !out->wm_mask ||
     (out->wm_mask & ~((1U << E008I_REAR_WMS) - 1)) || out->reserved ||
     !(out->raw_buf_done_status & E008I_REAR_BUF_DONE_MASK))
  return -EPROTO;
 return 0;
}
/* The caller has processed every WM in the copied record against its exact
 * consumed-IOVA ledger. Do not advance on observation/ledger failure. This
 * release grants only event-array reuse, never buffer/command DMA release.
 */
int csid680_e008i_rear_retire_event(struct csid_device *csid, u32 index,
                                  u64 owner)
{
 struct e008i_rear_done_event evt;
 int ret;
 if (!csid || !owner || owner != READ_ONCE(csid->e008i_rear_owner_epoch) ||
     index != READ_ONCE(csid->native_rear_done_consumed))
  return -ESTALE;
 ret = csid680_e008i_rear_done_event(csid, index, &evt);
 if (ret)
  return ret;
 smp_store_release(&csid->native_rear_done_consumed, index + 1);
 return 0;
}
#endif
