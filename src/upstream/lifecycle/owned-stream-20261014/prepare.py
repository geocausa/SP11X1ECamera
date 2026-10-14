#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Port retained lifecycle ownership into an isolated MMAP/RDI candidate."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path(__file__).resolve().parents[4]
Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
P=B/'candidate-27/tpg-qual01/source'
C=B/'candidate-28/lifecycle-qual01'
S=C/'source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,data):
 if path.exists():path.unlink()
 path.write_text(data)
def main():
 if not __debug__:raise RuntimeError("Optimized Python disables required preparation guards")
 head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
 subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-golden','--require-no-camera-process','--expect-head',head,'--expect-origin',head],check=True)
 assert not C.exists()
 pins=json.loads((R/'src/upstream/platform/front-graph-20261013/manifest.json').read_text())['output_source_sha256']
 pins['drivers/media/platform/qcom/camss/camss-tpg.c']='653b5767b130d947245cbee6799b148fa5d0b8d9114288d2f70ca855b9542b14'
 for n,h in pins.items():assert sha(P/n)==h,n
 C.mkdir(parents=True)
 shutil.copytree(P,S,copy_function=os.link,symlinks=True,
   ignore=shutil.ignore_patterns('*.o','*.ko','*.cmd','*.mod','*.mod.c','Module.symvers','modules.order'))
 path=S/'drivers/media/platform/qcom/camss'
 write(path/'camss-video-lifecycle.h',(Q/'camss-video-lifecycle.h').read_text())
 p=path/'camss-video.h';s=p.read_text()
 s=s.replace('struct camss_buffer {','struct camss_video_dma_hold;\n\nstruct camss_buffer {',1)
 s=s.replace('\tvoid *meta;','\tvoid *meta;\n\tstruct camss_video_dma_hold *dma_hold;',1)
 s=s.replace('struct camss_video {','#include "camss-video-lifecycle.h"\n\nstruct camss_video {',1)
 s=s.replace('\tstruct media_pipeline pipe;','\tstruct media_pipeline pipe;\n\tstruct camss_video_lifecycle lifecycle;\n\tstruct list_head dma_holds;\n\tbool pipeline_started;\n\tbool pm_held;\n\tbool module_held;',1)
 write(p,s)
 p=path/'camss.h';s=p.read_text().replace('\tbool legacy_phy;','\tbool legacy_phy;\n\t/* Serializes the X1E RDI owner and permanent stream-fault latch. */\n\tstruct mutex stream_guard;\n\tstruct camss_video *stream_owner;\n\tbool stream_fault;',1);write(p,s)
 p=path/'camss.c';s=p.read_text().replace('\tcamss->res = of_device_get_match_data(dev);','\tcamss->res = of_device_get_match_data(dev);\n\tmutex_init(&camss->stream_guard);',1);s=s.replace('MODULE_LICENSE("GPL v2");','MODULE_LICENSE("GPL v2");\nMODULE_IMPORT_NS("DMA_BUF");');write(p,s)
 p=path/'camss-video.c';s=p.read_text()
 s=s.replace('#include <linux/slab.h>','#include <linux/slab.h>\n#include <linux/dma-buf.h>\n#include <linux/module.h>',1)
 marker='static int video_buf_init('
 s=s.replace(marker,(Q/'video-owned-helpers.c.inc').read_text()+'\n'+marker,1)
 start=s.index('static int video_buf_init');end=s.index('static int video_buf_prepare',start)
 part=s[start:end].replace('\treturn 0;','\treturn video_dma_hold_get(video, vb, buffer);',1);s=s[:start]+part+s[end:]
 start=s.index('static int video_buf_prepare');end=s.index('static void video_buf_queue',start)
 part=s[start:end].replace('\tfor (i = 0;', '\tif (READ_ONCE(video->camss->stream_fault))\n\t\treturn -EIO;\n\n\tfor (i = 0;',1);s=s[:start]+part+s[end:]
 start=s.index('static void video_buf_queue');end=s.index('static int video_check_format',start)
 part=s[start:end].replace('\tvideo->ops->queue_buffer(video, buffer);','\tif (READ_ONCE(video->camss->stream_fault)) {\n\t\tvb2_buffer_done(vb, VB2_BUF_STATE_ERROR);\n\t\treturn;\n\t}\n\n\tvideo->ops->queue_buffer(video, buffer);',1);s=s[:start]+part+s[end:]
 start=s.index('static int video_prepare_streaming');end=s.index('static int video_start_streaming',start)
 replacement=(Q/'video-owned-prepare.c.inc').read_text()+'\n'
 s=s[:start]+replacement+s[end:]
 start=s.index('static int video_start_streaming');end=s.index('static void video_stop_streaming',start)
 part=s[start:end].replace('\tstruct v4l2_subdev *subdev;','\tstruct v4l2_subdev *subdev;\n\tvoid *stages[CAMSS_VIDEO_MAX_SUBDEVS];',1)
 part=part.replace('\tret = video_check_format(video);','\tvideo->pipeline_started = true;\n\n\tret = video_check_format(video);',1)
 part=part.replace('\tentity = &vdev->entity;',"""	if (video_owned_lifecycle(video)) {
		ret = video_collect_subdevs(video, stages);
		if (ret <= 0) {
			ret = ret ? ret : -ENOLINK;
			goto error;
		}
		video_mark_dma_exposed(video);
		ret = camss_video_start_owned(&video->lifecycle, stages, ret,
					      video, video_owned_stage_call);
		if (ret) {
			if (video->lifecycle.fault) {
				video_lifecycle_fault(video);
				goto flush_buffers;
			}
			goto error;
		}
		return 0;
	}

	entity = &vdev->entity;""",1)
 part=part.replace('\tvideo_device_pipeline_stop(vdev);','\tvideo_device_pipeline_stop(vdev);\n\tvideo->pipeline_started = false;',1)
 s=s[:start]+part+s[end:]
 start=s.index('static void video_stop_streaming');end=s.index('static void video_unprepare_streaming',start)
 part=s[start:end].replace('\tentity = &vdev->entity;',"""	if (video_owned_lifecycle(video)) {
		ret = video_stop_owned(video);
		if (ret)
			video_lifecycle_fault(video);
		if (!video->lifecycle.fault && video->pipeline_started) {
			video_device_pipeline_stop(vdev);
			video->pipeline_started = false;
		}
		/* Detach IRQ-visible queue pointers; independent DMA holds persist. */
		video->ops->flush_buffers(video, VB2_BUF_STATE_ERROR);
		return;
	}

	entity = &vdev->entity;""",1);s=s[:start]+part+s[end:]
 start=s.index('static void video_unprepare_streaming');end=s.index('static const struct vb2_ops msm_video_vb2_q_ops',start)
 s=s[:start]+(Q/'video-owned-unprepare.c.inc').read_text()+'\n'+s[end:]
 s=s.replace('\t.buf_init        = video_buf_init,','\t.buf_init        = video_buf_init,\n\t.buf_cleanup     = video_buf_cleanup,',1)
 s=s.replace('\tmutex_init(&video->q_lock);','\tmutex_init(&video->q_lock);\n\tINIT_LIST_HEAD(&video->dma_holds);',1)
 needle='\tq->timestamp_flags = V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC;'
 s=s.replace(needle,'\tif (video->camss->res->version == CAMSS_X1E80100 && !meta)\n\t\tq->io_modes = VB2_MMAP | VB2_READ;\n'+needle,1)
 write(p,s)
 names=['camss-video.c','camss-video.h','camss.h','camss.c']
 patch='Subject: [PATCH] media: qcom: camss: retain owned RDI stages and DMA on faults\n\nAdapt retained native acquired-state unwind and safe-release gating to the\nstandard X1E RDI path. Keep MMAP allocator references independently of VB2\nqueue ownership. Hold graph, power and module references on stop faults.\nImported DMA-BUF and PIX admission remain outside this qualification scope.\n\n---\n'
 for n in names:
  d=subprocess.run(['diff','-u','--label','a/drivers/media/platform/qcom/camss/'+n,'--label','b/drivers/media/platform/qcom/camss/'+n,str(P/'drivers/media/platform/qcom/camss'/n),str(path/n)],capture_output=True,text=True);assert d.returncode==1;patch+=d.stdout
 d=subprocess.run(['diff','-u','--label','/dev/null','--label','b/drivers/media/platform/qcom/camss/camss-video-lifecycle.h','/dev/null',str(path/'camss-video-lifecycle.h')],capture_output=True,text=True);assert d.returncode==1;patch+=d.stdout
 (C/'lifecycle.patch').write_text(patch)
 for n,h in pins.items():assert sha(P/n)==h,n
 (C/'PREPARED.json').write_text(json.dumps({'status':'PREPARED_OWNED_RDI_LIFECYCLE_SOURCE_ONLY','source_head':head,'parent_preserved':True,'installed':False,'source_sha256':{n:sha(path/n) for n in names+['camss-video-lifecycle.h']}},indent=2)+'\n')
 print('prepared',C)
if __name__=='__main__':main()
