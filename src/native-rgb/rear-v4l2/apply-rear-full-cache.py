#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Retain proof-retired FULL mappings per exclusive rear session."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def apply(camss):
 camss=Path(camss)
 def block(s):
  return "\n/* FULL_CACHE_BEGIN */\n#ifdef __KERNEL__\n"+s+"\n#endif\n/* FULL_CACHE_END */\n"
 def edit(name,a,b):
  p=camss/name;s=p.read_text();assert s.count(a)==1,(name,a,s.count(a));p.write_text(s.replace(a,b,1))
 (camss/"native-rear-full-cache.inc").write_bytes((HERE/"native-rear-full-cache.inc").read_bytes())
 edit("native-rear-video-lease.inc","static int __used\nnative_rear_video_lease_get",
      block('static bool native_rear_full_cache_is_active(void);\nstatic int native_rear_full_cache_take(struct dma_buf *,size_t,u64,struct native_rear_video_lease *);')+"static int __used\nnative_rear_video_lease_get")
 edit("native-rear-video-lease.inc",
      " candidate.attachment = dma_buf_attach(candidate.dbuf, vfe->camss->dev);",
      block(""" if (native_rear_full_cache_is_active()) {
  struct dma_buf *requested=candidate.dbuf;
  u64 owner;
  if (!e005y_vfe1_rear_sample_begin(&vfe->camss->e005y_vfe1_owner,true,&owner)) {
   dma_buf_put(requested);
   return -ESTALE;
  }
  ret=native_rear_full_cache_take(requested,vb2_plane_size(vb,0),owner,&candidate);
  if (ret!=-ENOENT) {
   dma_buf_put(requested); /* Temporary lookup reference, not cached ownership. */
   if (ret)
    return ret;
   *lease=candidate;
   return 0;
  }
 }""")+" candidate.attachment = dma_buf_attach(candidate.dbuf, vfe->camss->dev);")
 p=camss/"native-rear-video-lease.inc";p.write_text(p.read_text()+block('#include "native-rear-full-cache.inc"'))
 # Keep original full retirement guards and the last hardware snapshot identical.
 # The hook executes only AFTER that proof. Cache move clears old lease exactly once.
 edit("native-rear-live-retire.inc",
      " dma_buf_unmap_attachment_unlocked(old->public_full.attachment,",
      block(""" ret=native_rear_full_cache_retire(&old->public_full,result->owner_epoch,
                                    pair->frame[0].request_generation);
 if (ret<0)
  return ret;
 if (ret==1) {""")+" dma_buf_unmap_attachment_unlocked(old->public_full.attachment,")
 edit("native-rear-live-retire.inc"," dma_buf_put(old->public_full.dbuf);",
      " dma_buf_put(old->public_full.dbuf);"+block(" }"))
 edit("camss-vfe-e008d-rear-dma.inc",
      "\tset->full.dma = set->public_full.span.y_iova;",
      block(""" ret=native_rear_full_cache_disjoint(&set->public_full,native_rear_full_cache.owner);
 if (ret) {
  e008d_rear_release_partial(vfe,set);
  return ret;
 }""")+"\tset->full.dma = set->public_full.span.y_iova;")
 edit("native-rear-queue.inc"," for (;;) {",
      block(""" ret=native_rear_full_cache_begin(result->owner_epoch);
 if (ret) {
  kfree(next);
  return ret;
 }""")+" for (;;) {")
 edit("native-rear-queue.inc"," kfree(next);\n/* DMA_TIMING_BEGIN */",
      " kfree(next);"+block(" native_rear_full_cache_observe(vfe);")+"\n/* DMA_TIMING_BEGIN */")
 # Admission for all retained cache entries precedes ANY pair/cache release.
 edit("native-rear-reclaim.inc",
      "    /* Validate all retained leases before releasing any output/aux allocation. */",
      block("""    if (native_rear_full_cache_stop_check(owner_epoch,result->csid_quiesced,
          result->bus_stopped,result->rtcdm_stopped,result->source_stopped))
        return -EBUSY;""")+"    /* Validate all retained leases before releasing any output/aux allocation. */")
 edit("native-rear-reclaim.inc",
      "    for (s = 0; s < E008H_REAR_SLOTS; s++) {\n        if (pair->dma[s].public_full_retired)",
      block("""    {
        int cache_ret=native_rear_full_cache_flush(vfe,owner_epoch,result->csid_quiesced,
             result->bus_stopped,result->rtcdm_stopped,result->source_stopped);
        if (cache_ret)
            return cache_ret;
    }""")+"    for (s = 0; s < E008H_REAR_SLOTS; s++) {\n        if (pair->dma[s].public_full_retired)")
 p=camss/"native-rear-session-clean.inc";s=p.read_text()
 anchor=" return "
 pos=s.index(anchor);s=s[:pos]+block(" if (!native_rear_full_cache_idle())\n  return false;")+s[pos:];p.write_text(s)
 return dict(owner_bound_retired_FULL_mapping_cache=True,capacity=4,
             no_cache_admission_before_original_all10_owner_snapshot=True,
             generation_proven_before_take=True,original_pair_allocation_disjoint_proof_unchanged=True,
             cached_mapping_aliases_rejected=True,final_physical_cache_flush_requires_four_stops=True,
             clean_gate_requires_cache_idle=True,uncertain_maps_remain_pinned=True,pixel_bytes_read=0)
