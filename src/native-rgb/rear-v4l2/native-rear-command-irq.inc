/* SPDX-License-Identifier: GPL-2.0-only */
/* A generated INLINE IRQ may update last_irq_status after BL_DONE.
 * Preserve BL_DONE in its own release/acquire record before completion wake.
 */
#ifndef NATIVE_REAR_COMMAND_IRQ_INC
#define NATIVE_REAR_COMMAND_IRQ_INC
static void
native_rear_command_irq_record(struct camss_rtcdm *rt, u32 status)
{
 u32 sequence;
 if (!native_rear_bl_status_valid(status) || !READ_ONCE(rt->irq_armed) ||
     READ_ONCE(rt->faulted))
  return;
 sequence = READ_ONCE(rt->diag_fifo_seq);
 if (!sequence || !READ_ONCE(rt->diag_base))
  return;
 WRITE_ONCE(rt->receipt_dma, READ_ONCE(rt->diag_base));
 WRITE_ONCE(rt->receipt_len, READ_ONCE(rt->diag_len_low20));
 WRITE_ONCE(rt->receipt_irq_status, status);
 smp_store_release(&rt->receipt_sequence, sequence);
}

static int
native_rear_command_wait_receipt(struct camss_rtcdm *rt)
{
 unsigned long left;
 u32 sequence;
 left = wait_for_completion_timeout(&rt->completion,
                                  msecs_to_jiffies(CAMSS_RTCDM_WINDOWS_WAIT_MS));
 if (!left)
  return -ETIMEDOUT;
 sequence = smp_load_acquire(&rt->receipt_sequence);
 if (READ_ONCE(rt->faulted) || !READ_ONCE(rt->irq_armed) ||
     !sequence || sequence != READ_ONCE(rt->diag_fifo_seq) ||
     READ_ONCE(rt->receipt_dma) != READ_ONCE(rt->diag_base) ||
     READ_ONCE(rt->receipt_len) != READ_ONCE(rt->diag_len_low20) ||
     !native_rear_bl_status_valid(READ_ONCE(rt->receipt_irq_status)))
  return -EIO;
 return 0;
}
#endif
