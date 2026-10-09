#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Daily boot: load the rear camera stack and route it (idempotent, no capture, no reboot).

Runs from sp11-camera-daily.service only when the kernel command line carries
sp11_camera_daily=1. Also loads the v4l2loopback webcam device (/dev/video50) fed by sp11-webcam.
Writes /run/sp11-camera/ready (media device, sensor) on success.
"""
import json, os, re, runpy, subprocess, sys, time
from pathlib import Path
D = Path("/var/lib/sp11-camera-daily")
MARKER = "sp11_camera_daily=1"
RUN = Path("/run/sp11-camera")
H = runpy.run_path(str(D / "helpers60.py"))


def run(args, timeout=25):
    return subprocess.check_output([str(x) for x in args], text=True, stderr=subprocess.STDOUT, timeout=timeout)


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def main():
    need(MARKER in Path("/proc/cmdline").read_text().split(), "not the daily camera boot entry")
    RUN.mkdir(mode=0o755, exist_ok=True)
    loaded = Path("/proc/modules").read_text()
    if not re.search(r"^qcom_camss ", loaded, re.M):
        for m in ["i2c_qcom_cci", "mc", "videodev", "v4l2_async", "v4l2_fwnode", "videobuf2_common", "videobuf2_memops",
                  "videobuf2_v4l2", "videobuf2_dma_sg", "videobuf2_vmalloc", "v4l2_cci"]:
            run(["modprobe", m])
        run(["insmod", D / "modules/qcom-camss.ko", "e004j_ir_dphy_windows_parity=1", "native_linear_nv12_trial=1",
             "native_front_owner_trial=1", "native_front_queue_trial=1", "native_front_meta_trial=1",
             "native_front_params_trial=1", "native_front_profile_trial=1", "native_front_sof_trial=1",
             "native_rear_generation_trial=1"])
        for name in ["ov13858", "imx681", "sp11-vd55g0"]:
            run(["insmod", D / ("modules/" + name + ".ko")])
    for _ in range(400):
        st = H["states"]()
        if all(x["bound"] for x in st.values()):
            break
        time.sleep(0.05)
    need(all(x["bound"] for x in st.values()), "sensors not bound")
    classify = runpy.run_path(str(D / "route-contract.py"))["classify"]
    parse = runpy.run_path(str(D / "discover-unified.py"))["parse_entities"]
    cands = []
    for media in Path("/dev").glob("media*"):
        g = run(["media-ctl", "-d", media, "-p"])
        if "ov13858 " in g and "imx681 " in g:
            cands.append((str(media), g))
    need(len(cands) == 1, "one camera graph")
    media, g = cands[0]
    phase, _ = classify(g)
    if phase != "rear-pix-only":
        need(phase in ("neutral", "rear-only"), "unexpected route " + phase)
        if phase == "rear-only":
            run(["media-ctl", "-d", media, "-l", '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'])
            run(["media-ctl", "-d", media, "-l", '"msm_csiphy1":1 -> "msm_csid0":0 [0]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csiphy1":1 -> "msm_csid1":0 [1]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csid1":4 -> "msm_vfe1_pix":0 [1]'])
    ents = parse(run(["media-ctl", "-d", media, "-p"]))
    rear = [n for n in ents if re.fullmatch(r"ov13858 [0-9]+-0010", n)]
    need(len(rear) == 1, "unique rear sensor")
    pads = [(rear[0], 0), ("msm_csiphy1", 0), ("msm_csiphy1", 1), ("msm_csid1", 0), ("msm_csid1", 4), ("msm_vfe1_pix", 0), ("msm_vfe1_pix", 1)]
    for n, pad in pads:
        run(["media-ctl", "-d", media, "-V", f'"{n}":{pad} [fmt:SGRBG10_1X10/4064x2286 field:none]'])
    g = run(["media-ctl", "-d", media, "-p"])
    need(classify(g)[0] == "rear-pix-only", "rear PIX route")
    H["validate_formats"](g, pads)
    if not re.search(r"^v4l2loopback ", Path("/proc/modules").read_text(), re.M):
        run(["insmod", D / "modules/v4l2loopback.ko", "video_nr=50", "card_label=SP11 Rear Camera",
             "exclusive_caps=1", "max_buffers=8"])
    (RUN / "ready").write_text(json.dumps(dict(media=media, sensor=rear[0], time=time.time())) + "\n")
    print("SP11_CAMERA_DAILY_READY", media)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("SP11_CAMERA_DAILY_FAILED", e, file=sys.stderr)
        sys.exit(1)
