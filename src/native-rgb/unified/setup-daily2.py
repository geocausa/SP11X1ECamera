#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""SP11 cameras, daily boot: load the unified camera stack (front imx681 + rear
ov13858 on one camss module) and the two webcam loopback devices.

Runs from sp11-camera-daily2.service only when the kernel command line carries
sp11_camera_daily2=1. No capture, no reboot. Private firmware is read from
/var/lib/sp11-camera-daily2/firmware through firmware_class.path, so nothing
is installed under /lib/firmware. Writes /run/sp11-camera/ready on success.
"""
import json, re, subprocess, sys, time
from pathlib import Path

D = Path("/var/lib/sp11-camera-daily2")
MARKER = "sp11_camera_daily2=1"
RUN = Path("/run/sp11-camera")
CAMSS_PARAMS = (D / "camss-params.txt").read_text().split()
LOOPBACK = ["devices=2", "video_nr=50,51", 'card_label="SP11 Front Camera,SP11 Rear Camera"',
            "exclusive_caps=1,1", "max_buffers=4"]


def run(args, timeout=25):
    return subprocess.check_output([str(x) for x in args], text=True, stderr=subprocess.STDOUT, timeout=timeout)


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def sensors():
    found = {}
    for path in Path("/sys/bus/i2c/devices").glob("*-*"):
        c = path / "of_node/compatible"
        if c.exists():
            v = c.read_bytes().rstrip(b"\0")
            if v in (b"sony,imx681", b"ovti,ov13858", b"microsoft,sp11-vd55g0"):
                found[v.decode()] = path
    return found


def bound():
    s = sensors()
    return len(s) == 3 and all((p / "driver").is_symlink() for p in s.values())


def graph():
    for media in sorted(Path("/dev").glob("media*")):
        try:
            g = run(["media-ctl", "-d", media, "-p"])
        except Exception:
            continue
        if "imx681 " in g and "ov13858 " in g and "msm_vfe1_params" in g:
            return str(media), g
    return None, None


def main():
    need(MARKER in Path("/proc/cmdline").read_text().split(), "not the daily camera boot entry")
    RUN.mkdir(mode=0o755, exist_ok=True)
    loaded = Path("/proc/modules").read_text()
    if not re.search(r"^qcom_camss ", loaded, re.M):
        for m in ["i2c_qcom_cci", "mc", "videodev", "v4l2_async", "v4l2_fwnode", "videobuf2_common",
                  "videobuf2_memops", "videobuf2_v4l2", "videobuf2_dma_sg", "videobuf2_vmalloc", "v4l2_cci"]:
            run(["modprobe", m])
        run(["insmod", D / "modules/qcom-camss.ko", *CAMSS_PARAMS])
        for name in ["ov13858", "imx681", "sp11-vd55g0"]:
            run(["insmod", D / ("modules/" + name + ".ko")])
    if not re.search(r"^v4l2loopback ", Path("/proc/modules").read_text(), re.M):
        run(["insmod", D / "modules/v4l2loopback.ko", *LOOPBACK])
    for _ in range(400):
        if bound():
            break
        time.sleep(0.05)
    need(bound(), "sensors not bound")
    media = None
    for _ in range(100):
        media, g = graph()
        if media:
            break
        time.sleep(0.1)
    need(media, "complete camera media graph")
    for dev in ("/dev/video50", "/dev/video51"):
        need(Path(dev).exists(), "loopback " + dev)
    (RUN / "ready").write_text(json.dumps(dict(media=media, time=time.time())) + "\n")
    print("SP11_CAMERA_DAILY2_READY", media)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("SP11_CAMERA_DAILY2_FAILED", e, file=sys.stderr)
        sys.exit(1)
