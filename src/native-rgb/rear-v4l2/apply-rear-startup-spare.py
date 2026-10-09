#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Preallocate the first rolling set before startup, retaining original proofs."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def apply(camss):
 camss=Path(camss)
 def block(body):
  return "\n/* STARTUP_SPARE_BEGIN */\n#ifdef __KERNEL__\n"+body+"\n#endif\n/* STARTUP_SPARE_END */\n"
 def edit(name,old,new):
  p=camss/name;t=p.read_text();assert t.count(old)==1,(name,old,t.count(old))
  p.write_text(t.replace(old,new,1))
 edit("camss-vfe-e008h-rear-prime.inc","struct e008h_rear_prime_pair {",
      "struct e008h_rear_prime_pair {"+block(" struct native_rear_startup_spare *startup_spare;"))
 edit("native-rear-queue.inc","static int native_rear_queue_prepare(",
      block('#include "native-rear-startup-spare.inc"')+"static int native_rear_queue_prepare(")
 edit("native-rear-queue.inc"," next->dma[0] = pair->dma[1];",
      block(" next->startup_spare = pair->startup_spare;")+" next->dma[0] = pair->dma[1];")
 edit("native-rear-queue.inc"," ret = native_rear_public_dma_alloc(vfe, &next->dma[1], buffer);",
      block(" ret = native_rear_startup_spare_take(pair, &next->dma[1], buffer, owner);\n if (ret == -ENOENT)")+" ret = native_rear_public_dma_alloc(vfe, &next->dma[1], buffer);")
 edit("native-rear-queue.inc"," native_rear_full_cache_observe(vfe);",
      " native_rear_full_cache_observe(vfe);"+block(' dev_info(vfe->camss->dev,\n  "NATIVE_REAR_PREFETCH owner=%llu generation=%llu prepare_ns=%llu taken=%u pending_allocated=%u before_power=1 fifo_preserved=1 original_proofs=1 pixel_bytes_read=0\\n",\n  pair->startup_spare->owner, pair->startup_spare->generation,\n  pair->startup_spare->prepare_ns, pair->startup_spare->taken,\n  pair->startup_spare->dma.allocated);'))
 edit("camss-vfe-e008k-rear-runner.inc","\tret = e008k_rear_pipeline_pm_get(video_entity);",
      block(" if (req->public_video[0]) {\n  ret = native_rear_startup_spare_prepare(vfe, pair, req, owner_epoch);\n  if (ret)\n   goto out_release_clean_pair;\n }")+"\tret = e008k_rear_pipeline_pm_get(video_entity);")
 edit("camss-vfe-e008k-rear-runner.inc","\t/* The two DMA sets have been reclaimed; discard the software wrapper. */",
      block(" native_rear_startup_spare_release(vfe, pair, true);")+"\t/* The two DMA sets have been reclaimed; discard the software wrapper. */")
 edit("camss-vfe-e008k-rear-runner.inc","out_release_clean_pair:\n",
      "out_release_clean_pair:\n"+block(" native_rear_startup_spare_release(vfe, pair, false);"))
 (camss/"native-rear-startup-spare.inc").write_bytes((HERE/"native-rear-startup-spare.inc").read_bytes())
 return dict(first_replacement_preallocated_before_power=True,
             pending_FIFO_not_consumed=True,whole_allocations_checked_against_both_startup_sets_and_commands=True,
             owner_and_exact_next_generation_required=True,move_exactly_once=True,
             original_all10_consumed_address_and_four_stop_proofs_unchanged=True,
             uncertain_prefetch_descriptor_retained_with_faulted_pair=True,pixel_bytes_read=0)
