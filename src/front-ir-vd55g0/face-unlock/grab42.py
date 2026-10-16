#!/usr/bin/env python3
"""Read frames from the IR loopback with OpenCV (as Howdy does) and save the last one as PNG."""
import sys, time, cv2
cap = cv2.VideoCapture(sys.argv[1] if len(sys.argv) > 1 else "/dev/video42", cv2.CAP_V4L2)
print("opened", cap.isOpened(), cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
n = 0
t0 = time.time()
frame = None
while time.time() - t0 < 3:
    ok, f = cap.read()
    if ok:
        n += 1
        frame = f
print("frames", n, "shape", None if frame is None else frame.shape)
if frame is not None:
    g = frame if frame.ndim == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print("mean", round(float(g.mean()), 1))
    cv2.imwrite(sys.argv[2] if len(sys.argv) > 2 else "/root/imx681-test/grab42.png", g)
