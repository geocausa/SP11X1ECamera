#!/usr/bin/env python3
"""Trial-only metadata-output integration, checked exact anchors; no installation."""
from pathlib import Path
def apply(camss):
 def edit(name,old,new):
  p=camss/name;t=p.read_text()
  if t.count(old)!=1: raise ValueError(f"parameter queue anchor drift: {name}: {old[:90]}")
  p.write_text(t.replace(old,new,1))
 edit("camss.h","bool camss_x1e_native_front_params_trial_allowed(struct camss *camss);","bool camss_x1e_native_front_param_queue_trial_allowed(struct camss *camss);\nbool camss_x1e_native_front_params_trial_allowed(struct camss *camss);")
 edit("camss.c",'#include "native-front-params-kernel.inc"','''static bool native_front_param_queue_trial;
module_param(native_front_param_queue_trial, bool, 0400);
MODULE_PARM_DESC(native_front_param_queue_trial, "Native front META_OUTPUT parameters (trial ABI subset)");
bool camss_x1e_native_front_param_queue_trial_allowed(struct camss *camss)
{
 return native_front_param_queue_trial && camss_x1e_native_front_profile_trial_allowed(camss);
}
#include "native-front-params-kernel.inc"''')
 edit("camss-video.h","struct camss_video {","struct native_front_param_queue;\nstruct camss_video {\n\tstruct native_front_param_queue *native_param_queue;\n\tatomic_t native_param_queue_ready;")
 edit("camss-video.c",'#include "native-front-meta.inc"','#include "native-front-meta.inc"\n#include "native-front-param-queue.inc"')
 edit("camss-video.c","\tvideo->native_params_profile = NULL;","\tvideo->native_params_profile = NULL;\n\tvideo->native_param_queue = NULL;\n\tatomic_set(&video->native_param_queue_ready, 0);")
 edit("camss-video.c","if (camss_x1e_native_front_params_trial_allowed(video->camss))\n\t\t\tv4l2_ctrl_new_custom","if (camss_x1e_native_front_params_trial_allowed(video->camss) &&\n\t\t    !camss_x1e_native_front_param_queue_trial_allowed(video->camss))\n\t\t\tv4l2_ctrl_new_custom")
 edit("camss-video.c","\tret = video_device_pipeline_alloc_start(vdev);","""\tif (video_is_x1e_front_pix(video) &&
\t    camss_x1e_native_front_param_queue_trial_allowed(video->camss) &&
\t    !atomic_read(&video->native_param_queue_ready)) {
\t\tret = -EPIPE;
\t\tgoto flush_buffers;
\t}
\tret = video_device_pipeline_alloc_start(vdev);""")
 edit("camss-video.c","""\tret = native_front_meta_register(video);
\tif (ret) {
\t\tvb2_video_unregister_device(vdev);
\t\treturn ret;
\t}""","""\tret = native_front_meta_register(video);
\tif (!ret) {
\t\tret = native_front_param_register(video);
\t\tif (ret)
\t\t\tnative_front_meta_unregister(video);
\t}
\tif (ret) {
\t\tvb2_video_unregister_device(vdev);
\t\treturn ret;
\t}""")
 edit("camss-video.c","\tnative_front_meta_unregister(video);\n\tvb2_video_unregister_device(&video->vdev);","\tnative_front_param_unregister(video);\n\tnative_front_meta_unregister(video);\n\tvb2_video_unregister_device(&video->vdev);")
 return {"transport":"META_OUTPUT_QCIP_GAMMA256_SUBSET","default_enabled":False,"hardware_access":False}
