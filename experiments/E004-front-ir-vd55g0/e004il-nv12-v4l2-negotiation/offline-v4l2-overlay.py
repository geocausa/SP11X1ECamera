#!/usr/bin/env python3
"""E004il offline-only, exact-source overlay for independent NV12 V4L2 negotiation.

Builds ONLY in an uninstalled scratch copy. Production PIX remains QC10C.
No register writes, camera open, EEPROM, kernel install or boot changes.
"""
from pathlib import Path
import hashlib
import json
import sys

EXPECTED = {
 "camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
 "camss-video.c":"c046b3156f5507755fd6df6cc5398ea1513ce4365ee1feb9395828f2495121ac",
 "camss-vfe-680.c":"5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec",
}
def one(source, original, replacement, why):
    n=source.count(original)
    if n != 1:
        raise ValueError(f"{why}: expected exact unique anchor, got {n}")
    return source.replace(original,replacement,1)

def patch_vfe(text):
    a="""static const struct camss_format_info formats_pix_x1e80100[] = {
\t{ MEDIA_BUS_FMT_SRGGB10_1X10, 10, V4L2_PIX_FMT_QC10C, 1,
\t  PER_PLANE_DATA(0, 1, 1, 1, 1, 10) },
};"""
    b="""static const struct camss_format_info formats_pix_x1e80100[] = {
\t{ MEDIA_BUS_FMT_SRGGB10_1X10, 10, V4L2_PIX_FMT_QC10C, 1,
\t  PER_PLANE_DATA(0, 1, 1, 1, 1, 10) },
\t/* E004il: alternate format is negotiable, but STREAMON is unsupported. */
\t{ MEDIA_BUS_FMT_SRGGB10_1X10, 10, V4L2_PIX_FMT_NV12, 1,
\t  PER_PLANE_DATA(0, 1, 1, 2, 3, 8) },
};"""
    return one(text,a,b,"isolated X1E front format list")

def patch_video(text):
    text=one(text,
"""#define CAMSS_X1E80100_QC10C_SIZEIMAGE\t\t0x76b000""",
"""#define CAMSS_X1E80100_QC10C_SIZEIMAGE\t\t0x76b000
/* E004il: proposed alternate, NOT a supported hardware output mode. */
#define CAMSS_X1E80100_NV12_WIDTH\t\t2560
#define CAMSS_X1E80100_NV12_HEIGHT\t\t1440
#define CAMSS_X1E80100_NV12_STRIDE\t\t2560
#define CAMSS_X1E80100_NV12_SIZEIMAGE\t\t5529600""",
"new non-default geometry constants")
    text=one(text,
"""static bool video_is_x1e_front_pix(struct camss_video *video)
{""",
"""static bool video_is_x1e_front_pix(struct camss_video *video)
{""",
"front helper exists") # identity; helper name must exist exactly
    text=one(text,
"""\tif (f->pixelformat == V4L2_PIX_FMT_QC10C) {
\t\tif (mbus->width != CAMSS_X1E80100_QC10C_WIDTH ||""",
"""\t/* Only the X1E RAW10->PIX front format can reach this alternate. */
\tif (f->pixelformat == V4L2_PIX_FMT_NV12 &&
\t    f->code == MEDIA_BUS_FMT_SRGGB10_1X10) {
\t\tif (mbus->width != CAMSS_X1E80100_NV12_WIDTH ||
\t\t    mbus->height != CAMSS_X1E80100_NV12_HEIGHT)
\t\t\treturn -EINVAL;
\t\tpix->num_planes = 1;
\t\tpix->plane_fmt[0].bytesperline = CAMSS_X1E80100_NV12_STRIDE;
\t\tpix->plane_fmt[0].sizeimage = CAMSS_X1E80100_NV12_SIZEIMAGE;
\t\treturn 0;
\t}
\tif (f->pixelformat == V4L2_PIX_FMT_QC10C) {
\t\tif (mbus->width != CAMSS_X1E80100_QC10C_WIDTH ||""",
"media bus conversion")
    text=one(text,
"""\tif (fsize->pixel_format == V4L2_PIX_FMT_QC10C) {
\t\tfsize->type = V4L2_FRMSIZE_TYPE_DISCRETE;""",
"""\tif (fsize->pixel_format == V4L2_PIX_FMT_NV12 &&
\t    video_is_x1e_front_pix(video)) {
\t\tfsize->type = V4L2_FRMSIZE_TYPE_DISCRETE;
\t\tfsize->discrete.width = CAMSS_X1E80100_NV12_WIDTH;
\t\tfsize->discrete.height = CAMSS_X1E80100_NV12_HEIGHT;
\t\treturn 0;
\t}
\tif (fsize->pixel_format == V4L2_PIX_FMT_QC10C) {
\t\tfsize->type = V4L2_FRMSIZE_TYPE_DISCRETE;""",
"front NV12 discrete frame geometry")
    text=one(text,
"""\tif (fi->pixelformat == V4L2_PIX_FMT_QC10C) {
\t\tpix_mp->width = CAMSS_X1E80100_QC10C_WIDTH;""",
"""\tif (fi->pixelformat == V4L2_PIX_FMT_NV12 &&
\t    video_is_x1e_front_pix(video)) {
\t\tpix_mp->width = CAMSS_X1E80100_NV12_WIDTH;
\t\tpix_mp->height = CAMSS_X1E80100_NV12_HEIGHT;
\t\tpix_mp->num_planes = 1;
\t\tpix_mp->plane_fmt[0].bytesperline = CAMSS_X1E80100_NV12_STRIDE;
\t\tpix_mp->plane_fmt[0].sizeimage = CAMSS_X1E80100_NV12_SIZEIMAGE;
\t\tgoto set_colorimetry;
\t}
\tif (fi->pixelformat == V4L2_PIX_FMT_QC10C) {
\t\tpix_mp->width = CAMSS_X1E80100_QC10C_WIDTH;""",
"isolated NV12 S/TRY_FMT")
    text=one(text,
"""\tif (video->line_based && pix_mp->pixelformat != V4L2_PIX_FMT_QC10C)""",
"""\tif (video->line_based && pix_mp->pixelformat != V4L2_PIX_FMT_QC10C &&
\t    !(video_is_x1e_front_pix(video) &&
\t      pix_mp->pixelformat == V4L2_PIX_FMT_NV12))""",
"prevent generic line-based clamps from altering exact proposed NV12")
    text=one(text,
"""static int video_prepare_streaming(struct vb2_queue *q)
{
\tstruct camss_video *video = vb2_get_drv_priv(q);
\tstruct video_device *vdev = &video->vdev;
\tint ret;

\tret = v4l2_pipeline_pm_get(&vdev->entity);""",
"""static int video_prepare_streaming(struct vb2_queue *q)
{
\tstruct camss_video *video = vb2_get_drv_priv(q);
\tstruct video_device *vdev = &video->vdev;
\tint ret;

\t/* E004il: block even pipeline PM for the unproven alternate mode. */
\tif (video_is_x1e_front_pix(video) &&
\t    video->active_fmt.fmt.pix_mp.pixelformat == V4L2_PIX_FMT_NV12)
\t\treturn -EOPNOTSUPP;

\tret = v4l2_pipeline_pm_get(&vdev->entity);""",
"block power-up before any alternate streaming")
    text=one(text,
"""static int video_start_streaming(struct vb2_queue *q, unsigned int count)
{
\tstruct camss_video *video = vb2_get_drv_priv(q);
\tstruct video_device *vdev = &video->vdev;
\tstruct media_entity *entity;
\tstruct media_pad *pad;
\tstruct v4l2_subdev *subdev;
\tint ret;

\tret = video_device_pipeline_alloc_start(vdev);""",
"""static int video_start_streaming(struct vb2_queue *q, unsigned int count)
{
\tstruct camss_video *video = vb2_get_drv_priv(q);
\tstruct video_device *vdev = &video->vdev;
\tstruct media_entity *entity;
\tstruct media_pad *pad;
\tstruct v4l2_subdev *subdev;
\tint ret;

\t/* E004il: defence in depth if vb2 prepare_streaming is bypassed. */
\tif (video_is_x1e_front_pix(video) &&
\t    video->active_fmt.fmt.pix_mp.pixelformat == V4L2_PIX_FMT_NV12) {
\t\tret = -EOPNOTSUPP;
\t\tgoto flush_buffers;
\t}

\tret = video_device_pipeline_alloc_start(vdev);""",
"block alternate stream before pipeline allocation")
    return text

def patch(source_root, dest_root):
    manifest={}
    for name,sha in EXPECTED.items():
        source=source_root/name
        destination=dest_root/name
        raw=source.read_bytes()
        actual=hashlib.sha256(raw).hexdigest()
        if actual != sha:
            raise ValueError(f"accepted source drift {name}: {actual}")
        if not destination.is_file() or hashlib.sha256(destination.read_bytes()).hexdigest() != sha:
            raise ValueError(f"scratch copy mismatch: {name}")
        text=raw.decode("utf8")
        new=(patch_vfe(text) if name=="camss-vfe.c" else
             patch_video(text) if name=="camss-video.c" else text)
        destination.write_text(new)
        manifest[name]={"accepted_sha256":sha,"overlay_sha256":hashlib.sha256(new.encode()).hexdigest(),
                        "modified":new!=text}
    return manifest

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: offline-v4l2-overlay.py ACCEPTED_CAMSS_SOURCE SCRATCH_CAMSS_COPY")
    print(json.dumps(patch(Path(sys.argv[1]),Path(sys.argv[2])),sort_keys=True,indent=2))
