#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Candidate-only two-generation standard V4L2 queue, no new ioctl command ABI."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("public streaming anchor drift: "+a[:100])
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss);hook=camss/"native-rear-generation-hook.inc";t=hook.read_text()
 t=once(t,"int camss_x1e_rear_generation_once(struct camss_video *video)",
 """static int native_rear_public_once(struct camss_video *video,
 struct camss_buffer *buffers[2], struct native_rear_startup_result *output)""")
 t=once(t," if (video->vb2_q.streaming || READ_ONCE(video->x1e_pix_live_active) ||\n     READ_ONCE(video->x1e_pix_worker_started) || READ_ONCE(video->x1e_pix_runner_pinned)) {",
 """ if (!buffers || !buffers[0] || !buffers[1] || buffers[0] == buffers[1] ||
     !READ_ONCE(video->x1e_pix_worker_started) ||
     READ_ONCE(video->x1e_pix_runner_pinned)) {""")
 t=once(t," request.sensor = media_entity_to_v4l2_subdev(sensor_pad->entity);",
 """ request.public_video[0] = buffers[0];
 request.public_video[1] = buffers[1];
 request.sensor = media_entity_to_v4l2_subdev(sensor_pad->entity);""")
 t=once(t," mutex_unlock(&native_rear_generation_lock);\n return ret;",
        " *output = result;\n mutex_unlock(&native_rear_generation_lock);\n return ret;")
 t+="""\n/* Historical one-use S_CTRL cannot trigger this public candidate. */
int camss_x1e_rear_generation_once(struct camss_video *video)
{
 return -EOPNOTSUPP;
}
#include "native-rear-public-worker.inc"
"""
 hook.write_text(t);(camss/"native-rear-public-worker.inc").write_bytes((HERE/"native-rear-public-worker.inc").read_bytes())
 p=camss/"camss.h";t=p.read_text();anchor="int camss_x1e_rear_generation_once(struct camss_video *video);"
 t=once(t,anchor,anchor+"""
bool camss_x1e_rear_public_trial_allowed(struct camss_video *video);
int camss_x1e_rear_public_start(struct camss_video *video, unsigned int count);
void camss_x1e_rear_public_join(struct camss_video *video);""");p.write_text(t)
 p=camss/"camss-video.c";t=p.read_text()
 t=once(t,'#include "native-front-params.h"','#include "native-front-params.h"\n#include "native-rear-nv12-layout.h"')
 # Candidate selects rear output by its private opt-in. Maintained front remains unchanged.
 anchor="\tif (fsize->pixel_format == V4L2_PIX_FMT_NV12 &&\n\t    video_is_x1e_front_pix(video)) {"
 t=once(t,anchor,"""\tif (fsize->pixel_format == V4L2_PIX_FMT_NV12 &&
\t    video_is_x1e_front_pix(video) &&
\t    camss_x1e_rear_generation_trial_allowed(video->camss)) {
\t\tfsize->type = V4L2_FRMSIZE_TYPE_DISCRETE;
\t\tfsize->discrete.width = NATIVE_REAR_NV12_WIDTH;
\t\tfsize->discrete.height = NATIVE_REAR_NV12_HEIGHT;
\t\treturn 0;
\t}
"""+anchor)
 anchor="\tif (fi->pixelformat == V4L2_PIX_FMT_NV12 &&\n\t    video_is_x1e_front_pix(video)) {"
 t=once(t,anchor,"""\tif (fi->pixelformat == V4L2_PIX_FMT_NV12 &&
\t    video_is_x1e_front_pix(video) &&
\t    camss_x1e_rear_generation_trial_allowed(video->camss)) {
\t\tpix_mp->width = NATIVE_REAR_NV12_WIDTH;
\t\tpix_mp->height = NATIVE_REAR_NV12_HEIGHT;
\t\tpix_mp->num_planes = 1;
\t\tpix_mp->plane_fmt[0].bytesperline = NATIVE_REAR_NV12_STRIDE;
\t\tpix_mp->plane_fmt[0].sizeimage = NATIVE_REAR_NV12_BYTES;
\t\tgoto set_colorimetry;
\t}
"""+anchor)
 # Standard queue enters the public worker after media pipeline admission.
 anchor="\tif (video_is_x1e_front_pix(video)) {\n\t\tif (camss_x1e_native_front_meta_trial_allowed"
 t=once(t,anchor,"""\tif (camss_x1e_rear_public_trial_allowed(video)) {
\t\tret = camss_x1e_rear_public_start(video, count);
\t\tif (ret < 0)
\t\t\tgoto error;
\t\treturn 0;
\t}
"""+anchor)
 a=t.index("static void video_stop_streaming(struct vb2_queue *q)");b=t.index("static void video_unprepare_streaming",a);part=t[a:b]
 anchor="\tif (video_is_x1e_front_pix(video) && video->x1e_pix_runner_pinned)"
 part=once(part,anchor,"""\tif (camss_x1e_rear_public_trial_allowed(video)) {
\t\tcamss_x1e_rear_public_join(video);
\t\tvideo_device_pipeline_stop(vdev);
\t\tvideo->ops->flush_buffers(video, VB2_BUF_STATE_ERROR);
\t\treturn;
\t}

"""+anchor)
 t=t[:a]+part+t[b:];p.write_text(t)
 return dict(standard_STREAMON_STREAMOFF_and_QBUF_DQBUF_connected=True,
  bounded_generation_count=2,legacy_single_use_S_CTRL_disabled=True,
  continuous_or_libcamera_integration_proven=False)
