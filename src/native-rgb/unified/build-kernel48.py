#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Unified camss 48 = merged 47 + a statistics node shared by both cameras.

Front and rear both route through VFE1 and publish frame statistics on
msm_vfe1_stats, the front as QXS1 and the rear as QXR1. In 47 the node mode was
fixed at registration (rear won). Here the node advertises every mode the loaded
trials allow and S_FMT selects it while the queue is idle; the default stays
front when the front trial is loaded.
Usage: build-kernel48.py   (then build-unified.sh on the output)
"""
import shutil
from pathlib import Path

P = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel")
SRC = P / "native-rgb-unified-47"
OUT = P / "native-rgb-unified-48"
KEEP = (".c", ".h", ".inc")


def rep(path, a, b):
    t = path.read_text()
    assert t.count(a) == 1, (path.name, a[:70], t.count(a))
    path.write_text(t.replace(a, b))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ("camss", "imx681", "ov13858"):
        (OUT / sub).mkdir(parents=True)
        for f in (SRC / sub).iterdir():
            if f.is_file() and (f.suffix in KEEP or f.name in ("Makefile", "Kconfig")) and not f.name.endswith(".mod.c"):
                shutil.copy2(f, OUT / sub / f.name)
    m = OUT / "camss/native-front-meta.inc"
    rep(m, " bool streaming, rear;\n", " bool streaming, rear, front_ok, rear_ok;\n")
    rep(m,
        " if (fmt->index)\n  return -EINVAL;\n struct native_front_meta *meta=video_drvdata(file);\n"
        " fmt->pixelformat = meta->rear?NATIVE_REAR_STATS_MAGIC:NATIVE_FRONT_STATS_MAGIC;\n",
        " struct native_front_meta *meta=video_drvdata(file);\n"
        " u32 modes[2];\n unsigned int n = 0;\n"
        " if (meta->front_ok)\n  modes[n++] = NATIVE_FRONT_STATS_MAGIC;\n"
        " if (meta->rear_ok)\n  modes[n++] = NATIVE_REAR_STATS_MAGIC;\n"
        " if (fmt->index >= n)\n  return -EINVAL;\n"
        " fmt->pixelformat = modes[fmt->index];\n")
    rep(m,
        " struct native_front_meta *meta = video_drvdata(file);\n if (vb2_is_busy(&meta->queue))\n  return -EBUSY;\n"
        " return native_front_meta_format(file, fh, fmt);\n",
        " struct native_front_meta *meta = video_drvdata(file);\n"
        " if (fmt->type != V4L2_BUF_TYPE_META_CAPTURE)\n  return -EINVAL;\n"
        " if (vb2_is_busy(&meta->queue))\n  return -EBUSY;\n"
        " /* Both cameras share this node: the requested statistics layout selects the mode. */\n"
        " if (fmt->fmt.meta.dataformat == NATIVE_REAR_STATS_MAGIC && meta->rear_ok)\n  meta->rear = true;\n"
        " else if (fmt->fmt.meta.dataformat == NATIVE_FRONT_STATS_MAGIC && meta->front_ok)\n  meta->rear = false;\n"
        " return native_front_meta_format(file, fh, fmt);\n")
    rep(m,
        " bool rear=camss_x1e_rear_generation_trial_allowed(video->camss) &&\n"
        "  video==&video->camss->vfe[1].line[VFE_LINE_PIX].video_out;\n"
        " if (!rear && (!camss_x1e_native_front_meta_trial_allowed(video->camss) ||\n"
        "     !video_is_x1e_front_pix(video)))\n  return 0;\n",
        " bool rear=camss_x1e_rear_generation_trial_allowed(video->camss) &&\n"
        "  video==&video->camss->vfe[1].line[VFE_LINE_PIX].video_out;\n"
        " bool front=camss_x1e_native_front_meta_trial_allowed(video->camss) &&\n"
        "  video_is_x1e_front_pix(video);\n"
        " if (!rear && !front)\n  return 0;\n")
    rep(m, " meta->rear = rear;\n", " meta->rear_ok = rear;\n meta->front_ok = front;\n meta->rear = rear && !front;\n")
    # The front parameter queue gate must not block the rear (same VFE1 node,
    # identified by its exact 4K NV12 format).
    rep(OUT / "camss/camss-video.c",
        "\tif (video_is_x1e_front_pix(video) &&\n\t    camss_x1e_native_front_param_queue_trial_allowed(video->camss) &&\n",
        "\tif (video_is_x1e_front_pix(video) && !camss_x1e_rear_public_trial_allowed(video) &&\n"
        "\t    camss_x1e_native_front_param_queue_trial_allowed(video->camss) &&\n")
    # VFE1 PIX output geometry follows the requesting camera: exact 4K NV12 is
    # the rear, everything else the front 2560x1440 (when the front stack is
    # loaded). The rear keeps its two-buffer streaming minimum; the front none.
    v = OUT / "camss/camss-video.c"
    rear_enum = ("\tif (fsize->pixel_format == V4L2_PIX_FMT_NV12 &&\n\t    video_is_x1e_front_pix(video) &&\n"
                 "\t    camss_x1e_rear_generation_trial_allowed(video->camss)) {\n\t\tfsize->type")
    rep(v, rear_enum, rear_enum.replace("camss_x1e_rear_generation_trial_allowed(video->camss)) {",
        "camss_x1e_rear_generation_trial_allowed(video->camss) &&\n"
        "\t    !camss_x1e_native_front_param_queue_trial_allowed(video->camss)) {"))
    rear_try = ("\tif (fi->pixelformat == V4L2_PIX_FMT_NV12 &&\n\t    video_is_x1e_front_pix(video) &&\n"
                "\t    camss_x1e_rear_generation_trial_allowed(video->camss)) {\n\t\tpix_mp->width")
    rep(v, rear_try, rear_try.replace("camss_x1e_rear_generation_trial_allowed(video->camss)) {",
        "camss_x1e_rear_generation_trial_allowed(video->camss) &&\n"
        "\t    ((width == NATIVE_REAR_NV12_WIDTH && height == NATIVE_REAR_NV12_HEIGHT) ||\n"
        "\t     !camss_x1e_native_front_param_queue_trial_allowed(video->camss))) {"))
    rep(v, "\tvideo->active_fmt = *f;\n\n\treturn 0;\n}\n",
        "\tvideo->active_fmt = *f;\n"
        "\tif (video_is_x1e_front_pix(video) &&\n"
        "\t    camss_x1e_rear_generation_trial_allowed(video->camss))\n"
        "\t\tvideo->vb2_q.min_queued_buffers =\n"
        "\t\t\tcamss_x1e_rear_public_trial_allowed(video) ? 2 : 0;\n"
        "\n\treturn 0;\n}\n")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
