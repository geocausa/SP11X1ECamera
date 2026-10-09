#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Aggregate DMA operation timing; no lifetime, pixel-read or hardware changes."""
from pathlib import Path
def apply(camss):
 camss=Path(camss)
 def edit(name,a,b):
  p=camss/name;s=p.read_text();assert s.count(a)==1,(name,a,s.count(a));p.write_text(s.replace(a,b,1))
 def instrumentation(text):
  return "\n/* DMA_TIMING_BEGIN */\n#ifdef __KERNEL__\n"+text+"\n#endif\n/* DMA_TIMING_END */\n"
 definition="""struct native_rear_dma_timing {
 u64 full_get_ns, aux_alloc_ns, full_put_ns, aux_zero_ns, aux_free_ns;
 u32 full_get_calls, aux_alloc_calls, full_put_calls, aux_free_calls;
};
/* Only the exclusive rear worker writes this diagnostic. Queue reset excludes
 * startup and the single final queue log precedes physical stop/reclamation.
 * No IRQ producer, release predicate or control decision reads these fields.
 */
static struct native_rear_dma_timing native_rear_dma_timing;"""
 edit("camss-vfe-e008d-rear-dma.inc","#define E008D_REAR_AUX_COUNT 8",
      "#define E008D_REAR_AUX_COUNT 8"+instrumentation(definition))
 edit("camss-vfe-e008d-rear-dma.inc",
      "\tmemset(aux->cpu, 0, aux->size);\n\tdma_free_coherent(vfe->camss->dev, aux->size, aux->cpu, aux->dma);",
      instrumentation(" u64 zero_tick = ktime_get_ns(), free_tick;")+
      "\tmemset(aux->cpu, 0, aux->size);"+
      instrumentation(" native_rear_dma_timing.aux_zero_ns += ktime_get_ns() - zero_tick;\n free_tick = ktime_get_ns();")+
      "\tdma_free_coherent(vfe->camss->dev, aux->size, aux->cpu, aux->dma);"+
      instrumentation(" native_rear_dma_timing.aux_free_ns += ktime_get_ns() - free_tick;\n native_rear_dma_timing.aux_free_calls++;"))
 # Restrict allocation additions to the public path, not the coherent FULL path.
 p=camss/"camss-vfe-e008d-rear-dma.inc";s=p.read_text()
 i=s.index("native_rear_public_dma_alloc(");prefix=s[:i];body=s[i:]
 a="\tret = native_rear_video_lease_get(vfe,\n\t\t&vfe->line[VFE_LINE_PIX].video_out, buffer, &set->public_full);"
 assert body.count(a)==1
 body=body.replace(a,instrumentation(" u64 get_tick = ktime_get_ns(), alloc_tick;")+a+
     instrumentation(" native_rear_dma_timing.full_get_ns += ktime_get_ns() - get_tick;\n native_rear_dma_timing.full_get_calls++;"),1)
 a="\tfor (i = 0; i < E008D_REAR_AUX_COUNT; i++) {"
 assert body.count(a)==1
 body=body.replace(a,instrumentation(" alloc_tick = ktime_get_ns();")+a,1)
 a="\n\tset->allocated = true;"
 assert body.count(a)==1
 body=body.replace(a,instrumentation(" native_rear_dma_timing.aux_alloc_ns += ktime_get_ns() - alloc_tick;\n native_rear_dma_timing.aux_alloc_calls += E008D_REAR_AUX_COUNT;")+a,1)
 p.write_text(prefix+body)
 edit("native-rear-live-retire.inc",
      " dma_buf_unmap_attachment_unlocked(old->public_full.attachment,",
      instrumentation(" u64 put_tick = ktime_get_ns();")+
      " dma_buf_unmap_attachment_unlocked(old->public_full.attachment,")
 edit("native-rear-live-retire.inc",
      " dma_buf_put(old->public_full.dbuf);",
      " dma_buf_put(old->public_full.dbuf);"+
      instrumentation(" native_rear_dma_timing.full_put_ns += ktime_get_ns() - put_tick;\n native_rear_dma_timing.full_put_calls++;"))
 edit("native-rear-queue.inc"," for (;;) {",
      instrumentation(" memset(&native_rear_dma_timing, 0, sizeof(native_rear_dma_timing));")+" for (;;) {")
 log=' dev_info(vfe->camss->dev,\n  "NATIVE_REAR_DMA_TIMING full_get_ns=%llu aux_alloc_ns=%llu full_put_ns=%llu aux_zero_ns=%llu aux_free_ns=%llu full_get_calls=%u aux_alloc_calls=%u full_put_calls=%u aux_free_calls=%u scope=1 pixel_bytes_read=0\\n",\n  native_rear_dma_timing.full_get_ns, native_rear_dma_timing.aux_alloc_ns,\n  native_rear_dma_timing.full_put_ns, native_rear_dma_timing.aux_zero_ns, native_rear_dma_timing.aux_free_ns,\n  native_rear_dma_timing.full_get_calls, native_rear_dma_timing.aux_alloc_calls,\n  native_rear_dma_timing.full_put_calls, native_rear_dma_timing.aux_free_calls);'
 edit("native-rear-queue.inc"," kfree(next);"," kfree(next);"+instrumentation(log))
 return dict(aggregate_operation_timing_only=True,exclusive_worker_scope=True,
             queue_reset_excludes_startup=True,final_log_precedes_stop=True,
             no_release_or_control_authority=True,per_frame_logging=False,pixel_bytes_read=0)
