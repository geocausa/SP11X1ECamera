#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Rear metadata integration for a fresh single-use candidate; no runtime action."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("rear statistics anchor drift: "+a[:90])
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 (camss/'native-rear-stats.h').write_bytes((HERE/'native-rear-stats.h').read_bytes())
 (camss/'native-rear-statistics-copy.inc').write_bytes((HERE/'native-rear-statistics-copy.inc').read_bytes())
 p=camss/'camss-video.h';t=p.read_text()
 t=once(t,'struct native_front_meta *native_meta;','struct native_front_meta *native_meta;\n\tu64 native_rear_statistics_tick;')
 anchor='void camss_x1e_front_meta_complete(struct camss_video *video,'
 t=once(t,anchor,'int camss_x1e_rear_meta_publish(struct camss_video *,u64,u64,u32,u64,\n const void *const [6],const size_t [6]);\n'+anchor)
 p.write_text(t)
 p=camss/'native-front-meta.inc';t=p.read_text()
 t=once(t,'#include "native-front-stats.h"','#include "native-front-stats.h"\n#include "native-rear-stats.h"')
 t=once(t,' bool streaming;',' bool streaming, rear;')
 t=once(t,' if (*planes)\n  return *planes == 1 && sizes[0] >= NATIVE_FRONT_STATS_BYTES ? 0 : -EINVAL;\n *planes = 1;\n sizes[0] = NATIVE_FRONT_STATS_BYTES;',
 ' struct native_front_meta *meta=vb2_get_drv_priv(q);\n unsigned int bytes=meta->rear?NATIVE_REAR_STATS_BYTES:NATIVE_FRONT_STATS_BYTES;\n if (*planes)\n  return *planes == 1 && sizes[0] >= bytes ? 0 : -EINVAL;\n *planes = 1;\n sizes[0] = bytes;')
 t=once(t,' if (vb2_plane_size(vb, 0) < NATIVE_FRONT_STATS_BYTES || !vb2_plane_vaddr(vb, 0))',
 ' struct native_front_meta *meta=vb2_get_drv_priv(vb->vb2_queue);\n unsigned int bytes=meta->rear?NATIVE_REAR_STATS_BYTES:NATIVE_FRONT_STATS_BYTES;\n if (vb2_plane_size(vb, 0) < bytes || !vb2_plane_vaddr(vb, 0))')
 t=once(t,' fmt->pixelformat = NATIVE_FRONT_STATS_MAGIC;',' struct native_front_meta *meta=video_drvdata(file);\n fmt->pixelformat = meta->rear?NATIVE_REAR_STATS_MAGIC:NATIVE_FRONT_STATS_MAGIC;')
 t=once(t,' if (fmt->type != V4L2_BUF_TYPE_META_CAPTURE)',' struct native_front_meta *meta=video_drvdata(file);\n if (fmt->type != V4L2_BUF_TYPE_META_CAPTURE)')
 t=once(t,' fmt->fmt.meta.dataformat = NATIVE_FRONT_STATS_MAGIC;\n fmt->fmt.meta.buffersize = NATIVE_FRONT_STATS_BYTES;',
 ' fmt->fmt.meta.dataformat = meta->rear?NATIVE_REAR_STATS_MAGIC:NATIVE_FRONT_STATS_MAGIC;\n fmt->fmt.meta.buffersize = meta->rear?NATIVE_REAR_STATS_BYTES:NATIVE_FRONT_STATS_BYTES;')
 t=once(t,' if (!camss_x1e_native_front_meta_trial_allowed(video->camss) ||\n     !video_is_x1e_front_pix(video))',
 ' bool rear=camss_x1e_rear_generation_trial_allowed(video->camss) &&\n  video==&video->camss->vfe[1].line[VFE_LINE_PIX].video_out;\n if (!rear && (!camss_x1e_native_front_meta_trial_allowed(video->camss) ||\n     !video_is_x1e_front_pix(video)))')
 t=once(t,' meta->owner = video;',' meta->owner = video;\n meta->rear = rear;')
 t+='\n'+(HERE/'native-rear-meta-publish.inc').read_text()
 p.write_text(t)
 p=camss/'native-rear-live-aux-retire.inc';t=p.read_text()
 t=once(t,'#define NATIVE_REAR_LIVE_AUX_RETIRE_INC','#define NATIVE_REAR_LIVE_AUX_RETIRE_INC\n#ifdef __KERNEL__\n#include "native-rear-stats.h"\n#include "native-rear-statistics-copy.inc"\n#endif')
 anchor=' for (i = 0; i < E008D_REAR_AUX_COUNT; i++)\n  e008d_rear_aux_release(vfe, &pair->dma[0].aux[i]);'
 t=once(t,anchor,'#ifdef __KERNEL__\n ret = native_rear_statistics_before_aux_release(vfe,pair,result,cursor);\n if (ret)\n  return ret;\n#endif\n'+anchor)
 p.write_text(t)
 p=camss/'native-rear-queue.inc';t=p.read_text()
 t=once(t,'  buffer->vb.vb2_buf.timestamp = ktime_get_ns();',
 '#ifdef __KERNEL__\n  buffer->vb.vb2_buf.timestamp = video->native_rear_statistics_tick;\n  video->native_rear_statistics_tick = 0;\n#else\n  buffer->vb.vb2_buf.timestamp = ktime_get_ns();\n#endif')
 p.write_text(t)
 p=camss/'native-rear-public-worker.inc';t=p.read_text()
 anchor=' video->native_rear_completed = video->native_rear_live_completed = 0;'
 t=once(t,anchor,anchor+'\n video->native_rear_statistics_tick = 0;\n camss_x1e_rear_meta_reset(video);')
 # Remaining tails have no pre-free statistics envelope. Cancel instead of
 # publishing a successful image with a nonexistent statistics association.
 t=once(t,'  bool success = !ret && !READ_ONCE(video->x1e_pix_stop_requested);','  bool success = false; /* Final tails lack paired pre-free statistics. */')
 p.write_text(t)
 # Reset metadata identity before the exclusive worker publishes any frame.
 p=camss/'camss-video.h';t=p.read_text()
 t=once(t,'int camss_x1e_rear_meta_publish(', 'void camss_x1e_rear_meta_reset(struct camss_video *);\nint camss_x1e_rear_meta_publish(')
 p.write_text(t)
 p=camss/'native-front-meta.inc';t=p.read_text()
 t+='\nvoid camss_x1e_rear_meta_reset(struct camss_video *video)\n{\n native_front_meta_reset(video);\n}\n'
 p.write_text(t)

 p=camss/'camss-vfe-e008k-rear-runner.inc';t=p.read_text()
 anchor='\tif (!e008h_rear_both_complete(pair, owner_epoch))\n\t\treturn -EBUSY;'
 diagnostic="""#ifdef __KERNEL__
 dev_info(camss->dev,
  "NATIVE_REAR_STOP_ADMISSION both=%u ledgers=%u faulted=%u programmed0=%u programmed1=%u active0=%u active1=%u fault0=%u fault1=%u pending0=%u pending1=%u owner0=%llu owner1=%llu expected_owner=%llu generation0=%llu generation1=%llu\\n",
  e008h_rear_both_complete(pair, owner_epoch),pair->ledgers_bound,pair->faulted,
  pair->programmed[0],pair->programmed[1],pair->frame[0].active,pair->frame[1].active,
  pair->frame[0].faulted,pair->frame[1].faulted,pair->frame[0].pending,pair->frame[1].pending,
  pair->frame[0].owner_epoch,pair->frame[1].owner_epoch,owner_epoch,
  pair->frame[0].request_generation,pair->frame[1].request_generation);
#endif
"""
 t=once(t,anchor,diagnostic+anchor)
 # Stop upstream packet production after exact pair completion.
 # All CSID/BUS/CDM/source guards still precede any DMA release.
 block='\t/* Preserve accepted E008c source stop order: CSIPHY then sensor. */\n\tstop_ret = e008k_rear_subdev_stream(&csiphy->subdev, false);\n\tif (!stop_ret)\n\t\t*csiphy_streaming = false;\n\tret = e008k_rear_subdev_stream(sensor, false);\n\tif (!ret)\n\t\t*sensor_streaming = false;\n\tif (stop_ret || ret)\n\t\treturn stop_ret ? stop_ret : ret;\n\tresult->source_stopped = true;\n'
 anchor='\tret = csid680_e008a_rear_quiesce(csid, true);'
 t=once(t,block,"");t=once(t,anchor,block+"\n"+anchor)
 p.write_text(t)
 return dict(statistics_copy_before_aux_zero_free=True,original_replacement_proof_unchanged=True,
  image_pixel_copy=False,opaque_allocated_capacities=True,final_unpaired_tails_cancelled=True,
  automatic_exposure=False,hardware_qualified=False)
