#!/usr/bin/env python3
"""SP11 IR camera -> 8-bit grey v4l2loopback device, with the IR LED armed only while running.

Pipeline: VD55G0 (vd55g1 driver, LED in hardware strobe on GPIO1) -> CAMSS CSIPHY0/CSID0/VFE0 RDI0
(Y10P 644x604) -> this script -> /dev/video<N> (GREY 644x604) for Howdy/OpenCV.
LED: PM8550 flash via its V4L2 flash subdev, Windows-equivalent drive (700 mA total, 10 ms cut-off,
~0.86 ms pulses from exposure=100 lines). Disarms on exit, on SIGTERM/SIGINT/SIGHUP and on --seconds.

Usage: sp11-ir-bridge.py [--out /dev/video42] [--seconds N] [--gain 16] [--exposure 100]"""
import argparse, fcntl, os, re, signal, struct, subprocess, sys, time
import numpy as np

W, H, BPL = 644, 604, 816
FRAME = BPL * H
VIDIOC_S_CTRL = 0xc008561c
VIDIOC_G_CTRL = 0xc008561b
VIDIOC_S_FMT = 0xc0d05605
V4L2_BUF_TYPE_VIDEO_OUTPUT = 2
V4L2_PIX_FMT_GREY = 0x59455247
LED_MODE, STROBE_SOURCE, TIMEOUT, INTENSITY, FAULT = 0x009c0901, 0x009c0902, 0x009c0906, 0x009c0907, 0x009c090a

class Stop(Exception):
    pass

def on_signal(signum, frame):
    raise Stop(signum)

def sh(*a):
    return subprocess.run(a, check=True, capture_output=True, text=True).stdout

def find_media():
    for m in sorted(os.listdir("/dev")):
        if m.startswith("media"):
            p = "/dev/" + m
            try:
                if "msm_csid0" in sh("media-ctl", "-d", p, "-p"):
                    return p
            except subprocess.CalledProcessError:
                pass
    sys.exit("no CAMSS media device")

def ioctl_ctrl(fd, cid, val):
    fcntl.ioctl(fd, VIDIOC_S_CTRL, struct.pack("Ii", cid, val))

def get_ctrl(fd, cid):
    return struct.unpack("Ii", fcntl.ioctl(fd, VIDIOC_G_CTRL, struct.pack("Ii", cid, 0)))[1]

def set_out_format(fd):
    # struct v4l2_format (208 bytes): type, then v4l2_pix_format
    pix = struct.pack("IIIIIIII", W, H, V4L2_PIX_FMT_GREY, 1, W, W * H, 8, 0)  # field NONE=1, colorspace RAW? use 8=SRGB
    buf = struct.pack("I", V4L2_BUF_TYPE_VIDEO_OUTPUT) + b"\0" * 4 + pix
    buf = buf.ljust(208, b"\0")
    fcntl.ioctl(fd, VIDIOC_S_FMT, bytearray(buf))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/dev/video42")
    ap.add_argument("--seconds", type=float, default=0)
    ap.add_argument("--gain", type=int, default=16)
    ap.add_argument("--exposure", type=int, default=100)
    ap.add_argument("--current-ua", type=int, default=700000)
    ap.add_argument("--gamma", type=float, default=0.6)
    a = ap.parse_args()
    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(sig, on_signal)

    M = find_media()
    txt = sh("media-ctl", "-d", M, "-p")
    sn = re.search(r"entity \d+: (vd55g\S* \S+) \(", txt).group(1)
    S = sh("media-ctl", "-d", M, "-e", sn).strip()
    FL = sh("media-ctl", "-d", M, "-e", "sp11-ir-illuminator").strip()
    V = sh("media-ctl", "-d", M, "-e", "msm_vfe0_video0").strip()
    sh("media-ctl", "-d", M, "-l", '"msm_csiphy0":1->"msm_csid0":0[1], "msm_csid0":1->"msm_vfe0_rdi0":0[1]')
    for e in ['"%s":0' % sn, '"msm_csiphy0":0', '"msm_csiphy0":1', '"msm_csid0":0', '"msm_csid0":1',
              '"msm_vfe0_rdi0":0', '"msm_vfe0_rdi0":1']:
        sh("media-ctl", "-d", M, "-V", "%s[fmt:Y10_1X10/%dx%d field:none]" % (e, W, H))
    sh("v4l2-ctl", "-d", V, "--set-fmt-video=width=%d,height=%d,pixelformat=Y10P" % (W, H))
    sh("v4l2-ctl", "-d", S, "--set-ctrl", "auto_exposure=1")
    sh("v4l2-ctl", "-d", S, "--set-ctrl", "exposure=%d,analogue_gain=%d" % (a.exposure, a.gain))

    out = os.open(a.out, os.O_WRONLY)
    set_out_format(out)
    fl = os.open(FL, os.O_RDWR)
    cap = None
    n = 0
    t0 = time.monotonic()
    lo, hi = 16.0, 80.0
    try:
        sh("v4l2-ctl", "-d", S, "--set-ctrl", "led_mode=1")      # sensor GPIO1 -> strobe
        ioctl_ctrl(fl, TIMEOUT, 10000)
        ioctl_ctrl(fl, INTENSITY, a.current_ua)
        ioctl_ctrl(fl, STROBE_SOURCE, 1)
        ioctl_ctrl(fl, LED_MODE, 1)                                # PMIC armed for hardware strobe
        print("armed %s -> %s fault=%#x" % (V, a.out, get_ctrl(fl, FAULT)), flush=True)
        cap = subprocess.Popen(["v4l2-ctl", "-d", V, "--stream-mmap=4", "--stream-to=-", "--stream-poll"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
        buf = bytearray()
        while True:
            if a.seconds and time.monotonic() - t0 > a.seconds:
                break
            chunk = cap.stdout.read(FRAME - len(buf))
            if not chunk:
                break
            buf += chunk
            if len(buf) < FRAME:
                continue
            raw = np.frombuffer(bytes(buf), dtype=np.uint8).reshape(H, BPL)[:, :805]
            buf = bytearray()
            msb = raw.reshape(H, -1, 5)[:, :, :4].reshape(H, -1).astype(np.float32)  # top 8 of 10 bits
            p1, p99 = np.percentile(msb[::4, ::4], (1, 99.5))
            lo = 0.9 * lo + 0.1 * p1
            hi = 0.9 * hi + 0.1 * max(p99, p1 + 8)
            norm = np.clip((msb - lo) / (hi - lo), 0, 1)
            img = (np.power(norm, a.gamma) * 255).astype(np.uint8)
            os.write(out, img.tobytes())
            n += 1
    except Stop as e:
        print("signal %s" % e, flush=True)
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        if cap and cap.poll() is None:
            cap.terminate()
            try:
                cap.wait(3)
            except subprocess.TimeoutExpired:
                cap.kill()
        try:
            ioctl_ctrl(fl, STROBE_SOURCE, 0)
            ioctl_ctrl(fl, LED_MODE, 0)
            print("disarmed fault=%#x frames=%d %.1f fps" % (get_ctrl(fl, FAULT), n,
                  n / max(time.monotonic() - t0, 0.001)), flush=True)
        finally:
            os.close(fl)
            subprocess.run(["v4l2-ctl", "-d", S, "--set-ctrl", "led_mode=0"])
            os.close(out)

if __name__ == "__main__":
    main()
