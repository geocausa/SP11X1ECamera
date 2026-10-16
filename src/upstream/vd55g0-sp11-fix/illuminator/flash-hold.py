#!/usr/bin/env python3
"""Arm the IR LED (V4L2 flash subdev, external/hardware strobe) only while a command runs.
The v4l2-flash core resets the strobe source to software when the subdev is closed, so the
arming must hold the file open. SIGTERM/SIGHUP/SIGINT are turned into exceptions so the
explicit disarm always runs; closing the file disarms as a second line of defence.
Usage: flash-hold.py <flash-subdev> <timeout_us> <intensity_uA> -- <command...>"""
import fcntl, os, signal, struct, subprocess, sys
VIDIOC_S_CTRL = 0xc008561c
VIDIOC_G_CTRL = 0xc008561b
LED_MODE, STROBE_SOURCE, TIMEOUT, INTENSITY, FAULT = 0x009c0901, 0x009c0902, 0x009c0906, 0x009c0907, 0x009c090a

class Stop(Exception):
    pass

def on_signal(signum, frame):
    raise Stop(signum)

for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
    signal.signal(sig, on_signal)

dev, tmo, inten = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cmd = sys.argv[sys.argv.index("--") + 1:]
fd = os.open(dev, os.O_RDWR)

def s(cid, val):
    fcntl.ioctl(fd, VIDIOC_S_CTRL, struct.pack("Ii", cid, val))

def g(cid):
    return struct.unpack("Ii", fcntl.ioctl(fd, VIDIOC_G_CTRL, struct.pack("Ii", cid, 0)))[1]

rc = 1
child = None
try:
    s(TIMEOUT, tmo)
    s(INTENSITY, inten)
    s(STROBE_SOURCE, 1)
    s(LED_MODE, 1)   # flash mode + external source -> PMIC channels armed for the hardware strobe
    print("armed: mode=%d source=%d timeout=%d intensity=%d fault=%#x" %
          (g(LED_MODE), g(STROBE_SOURCE), g(TIMEOUT), g(INTENSITY), g(FAULT)), flush=True)
    child = subprocess.Popen(cmd)
    rc = child.wait()
except Stop as e:
    print("signal %s: stopping" % e, flush=True)
    if child and child.poll() is None:
        child.terminate()
finally:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    try:
        s(STROBE_SOURCE, 0)
        s(LED_MODE, 0)
        print("disarmed: mode=%d source=%d fault=%#x" % (g(LED_MODE), g(STROBE_SOURCE), g(FAULT)), flush=True)
    finally:
        os.close(fd)
sys.exit(rc)
