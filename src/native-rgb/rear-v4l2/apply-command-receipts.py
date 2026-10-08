#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bind serialized FIFO0 BL_DONE receipts to the exact command allocation.
This overlay observes eligibility only: command arenas remain pinned to stop.
"""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1: raise RuntimeError("command receipt source anchor drift")
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 for name in ("native-rear-command-receipt.h","native-rear-command-receipts.inc",
              "native-rear-command-observe.inc"):
  (camss/name).write_bytes((HERE/name).read_bytes())
 p=camss/"camss-vfe-e008l-rear-command-dma.inc";t=p.read_text()
 t=once(t,"struct e008l_rear_packet_dma {",'#include "native-rear-command-receipt.h"\n\nstruct e008l_rear_packet_dma {')
 t=once(t,"\tbool submitted;","""\tbool submitted;
 u64 receipt_owner, receipt_request;
 void *receipt_slab_cpu;
 dma_addr_t receipt_slab_dma;
 size_t receipt_slab_bytes;
 struct e007y_rear_dmi_target *receipt_dmi;
 struct e006g_rear_dynamic_payloads *receipt_dynamic;
 u8 receipt_count;
 struct native_rear_bl_receipt receipt[E007Y_MAX_BL];""")
 t=once(t,"\tbool hardware_exposed;","\tbool hardware_exposed;\n bool receipt_faulted;")
 p.write_text(t)
 p=camss/"camss-e008k-rear-bridge.h";t=p.read_text()
 t=once(t,"#include <linux/types.h>",'#include <linux/types.h>\n#include "native-rear-command-receipt.h"')
 anchor="int e008k_rear_rtcdm_submit_bl(struct camss *camss, u32 dma, u16 bytes);"
 t=once(t,anchor,anchor+"""
int e008k_rear_rtcdm_submit_bl_receipt(struct camss *, u32, u16,
                                     struct native_rear_bl_receipt *);
int e008k_rear_rtcdm_receipt_current(struct camss *,
                                    const struct native_rear_bl_receipt *);""")
 p.write_text(t)
 # Fill receipt while the original submit mutex still owns the completion.
 p=camss/"camss.c";t=p.read_text()
 old="static int camss_rtcdm1_windows_fifo0_commit(struct camss *camss,\n\t\t\t\t\t     u32 base, u32 len_low20)"
 new='#include "native-rear-command-receipt.h"\n\nstatic int camss_rtcdm1_windows_fifo0_commit_receipt(struct camss *camss,\n u32 base, u32 len_low20, struct native_rear_bl_receipt *receipt)'
 t=once(t,old,new)
 start=t.index(new);end=t.index("\nstatic void camss_rtcdm1_windows_stop(",start)
 fn=t[start:end]
 fn=once(fn,"\tif (!rt->present || !rt->base)","\tif (receipt)\n\t\tmemset(receipt, 0, sizeof(*receipt));\n\tif (!rt->present || !rt->base)")
 fn=once(fn,"\treinit_completion(&rt->completion);",""" if (receipt && READ_ONCE(rt->diag_fifo_seq) == U32_MAX) {
  ret = -EOVERFLOW;
  goto out_unlock;
 }
\treinit_completion(&rt->completion);""")
 fn=once(fn,"out_unlock:\n\tmutex_unlock(&rt->lock);","""out_unlock:
 if (!ret && receipt) {
  synchronize_irq(rt->irq);
  if (!READ_ONCE(rt->irq_armed) || READ_ONCE(rt->faulted) ||
      READ_ONCE(rt->last_irq_status) != CAMSS_RTCDM_IRQ_BL_DONE ||
      READ_ONCE(rt->diag_base) != base ||
      READ_ONCE(rt->diag_len_low20) != len_low20 ||
      !READ_ONCE(rt->diag_fifo_seq) ||
      len_low20 >= U16_MAX) {
   ret = -EPROTO;
  } else {
   receipt->sequence = READ_ONCE(rt->diag_fifo_seq);
   receipt->dma = base;
   receipt->bytes = len_low20 + 1;
   receipt->irq_status = READ_ONCE(rt->last_irq_status);
   receipt->complete = true;
  }
 }
\tmutex_unlock(&rt->lock);""")
 t=t[:start]+fn+t[end:]
 wrapper="""
static int camss_rtcdm1_windows_fifo0_commit(struct camss *camss,
                                          u32 base, u32 len_low20)
{
 return camss_rtcdm1_windows_fifo0_commit_receipt(camss, base, len_low20, NULL);
}
"""
 t=once(t,"\nstatic void camss_rtcdm1_windows_stop(",wrapper+"\nstatic void camss_rtcdm1_windows_stop(")
 p.write_text(t)
 p=camss/"camss-e008k-rear-rtcdm-bridge.inc";t=p.read_text()
 anchor="void e008k_rear_rtcdm_stop_close(struct camss *camss)"
 extra="""int e008k_rear_rtcdm_submit_bl_receipt(struct camss *camss, u32 dma,
                                     u16 bytes, struct native_rear_bl_receipt *r)
{
 if (!r)
  return -EINVAL;
 memset(r, 0, sizeof(*r));
 if (!camss || !dma || !bytes)
  return -EINVAL;
 return camss_rtcdm1_windows_fifo0_commit_receipt(camss, dma, bytes - 1, r);
}

int e008k_rear_rtcdm_receipt_current(struct camss *camss,
                                    const struct native_rear_bl_receipt *r)
{
 struct camss_rtcdm *rt;
 int ret = 0;
 if (!camss || !r || !r->complete || !r->sequence || !r->dma ||
     !r->bytes || r->irq_status != CAMSS_RTCDM_IRQ_BL_DONE ||
     !camss->rtcdm1.present || !camss->rtcdm1.base)
  return -EINVAL;
 rt = &camss->rtcdm1;
 mutex_lock(&rt->lock);
 synchronize_irq(rt->irq);
 if (!READ_ONCE(rt->irq_armed) || READ_ONCE(rt->faulted) ||
     READ_ONCE(rt->diag_fifo_seq) != r->sequence ||
     READ_ONCE(rt->diag_base) != r->dma ||
     READ_ONCE(rt->diag_len_low20) != r->bytes - 1U ||
     READ_ONCE(rt->last_irq_status) != CAMSS_RTCDM_IRQ_BL_DONE)
  ret = -ESTALE;
 mutex_unlock(&rt->lock);
 return ret;
}

"""
 t=once(t,anchor,extra+anchor);p.write_text(t)
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 start=t.index("static int\ne008k_rear_submit_packet(")
 end=t.index("static int\ne008k_rear_validate_prepared_packets(",start)
 t=t[:start]+"""#include "native-rear-command-receipts.inc"
#include "native-rear-command-observe.inc"

static int
e008k_rear_submit_packet(struct camss *camss, struct e008k_rear_request *req,
                         unsigned int packet, u64 owner)
{
 return native_rear_submit_receipted_packet(camss, req, packet, owner);
}

"""+t[end:]
 for i in range(4):
  t=once(t,f"e008k_rear_submit_packet(camss, &req->commands->packet[{i}].out)",
           f"e008k_rear_submit_packet(camss, req, {i}, owner_epoch)")
 anchor="  native_rear_live_retire_aux_observe(vfe, csid, pair, result, done_cursor);"
 t=once(t,anchor,anchor+"\n native_rear_command_receipts_observe(vfe, csid, pair, req, result, done_cursor);")
 p.write_text(t)
 return {"exact_serialized_22_BL_receipts":True,"allocation_request_owner_binding":True,
         "receipt_capture_under_FIFO_mutex":True,"live_command_observation_only":True,
         "live_command_free_rewrite_or_requeue":False,"commands_retained_until_stop":True,
         "hardware_contract":"existing serialized synchronous FIFO0 BL_DONE; software sequence is not a hardware request ID"}
