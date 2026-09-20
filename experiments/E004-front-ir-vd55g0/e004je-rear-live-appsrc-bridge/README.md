# E004je — rear Bayer10 into real GStreamer application stream (offline)

2026-09-20. Parent `138ea05`. Protected SP11 Golden remained booted and
no camera/media/V4L2 device was opened or installed during this
experiment. This is a **source-only, bounded application-stream
prototype**, NOT a released selectable webcam and NOT proof that its
capture-input half has been tested live.

The previous E004ja hardware boot captured eight **distinct real normal
optical** rear OV13858 Bayer10 frames at 29.9504fps, and E004iu converted
them offline to eight distinct 1920×1080 NV12 frames accepted by
GStreamer. E004jc subsequently proved real 8-rear→27-front QC10C
same-boot capture with the mapped-DMA guard. The new objective is to
replace disk-backed bulk rear conversion with a bounded byte stream
into an actual GStreamer application.

## Implemented bounded transport

`rear-bayer-stdin-to-nv12.c` compiles in the **exact E004iu C colour
proxy conversion source**, so a single accepted rear hardware
colourbar yields the same deterministic NV12 SHA-256 as the prior
offline converter: `86f496416883d7728675802c70a0c83adb10d1a02591a56de1fe45cc3e223d0b`.
It reads exactly N 14,321,824-byte full GRBG10p `pgAA` frames
from STDIN, writes exactly N 3,110,400-byte 1920×1080 NV12 frames
to STDOUT, requires EOF after that bound, refuses a TTY and invalid
bounds and puts metadata **only on STDERR**. The framing guarantee
applies when the upstream V4L2 producer itself stops at N buffers
and the shell uses `pipefail`.

`nv12-appsrc-consumer.py` reads exactly N full NV12 frames from a
byte stream; for each, it constructs an actual GStreamer appsrc
buffer with 30fps PTS/duration and sends it through
`appsrc → queue → videoconvert → I420 appsink`. The application
receiver validates every resulting buffer length, PTS, total count,
EOS and pipeline errors. A bounded queue applies backpressure.
No intermediate NV12 or raw optical files are required; pixels are
not logged. This proves a real GStreamer in-process **application
consumer**, not a V4L2 virtual camera device discoverable by Zoom,
Firefox, Chromium or arbitrary applications.

## Actual SP11 offline validation

The one-frame archived accepted rear **test pattern** was piped through
both stages and the application returned PASS. Nine tests passed:
exact accepted colourbar/NV12 hash parity, end-to-end one-frame
GStreamer delivery, eight-frame bounded streaming with the archived
test pattern repeated (not fresh optical capture), and negative
missing/extra bytes, front-QC10C-sized input, bad count and no
hardware/boot APIs. The eight-frame pipe exercises reader/writer
backpressure without a bulk NV12 output file. It does not measure
live sensor latency, real camera-to-display cadence or proper
image quality. The colour proxy remains uncalibrated and does not
perform demosaicing, noise removal, black-level or white-balance
calibration.

Compile and run offline, with **only** the previously accepted
rear hardware test-pattern fixture:

```sh
D=$(mktemp -d /tmp/sp11-e004je-test.XXXXXX)
gcc -O3 -std=c11 -Wall -Wextra -Werror -pedantic \
  -fno-fast-math -ffp-contract=off \
  experiments/E004-front-ir-vd55g0/e004je-rear-live-appsrc-bridge/rear-bayer-stdin-to-nv12.c \
  -lm -o "$D/rear-bayer-stdin-to-nv12"
cat experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw |
  "$D/rear-bayer-stdin-to-nv12" --frames 1 |
  /usr/bin/python3 experiments/E004-front-ir-vd55g0/e004je-rear-live-appsrc-bridge/nv12-appsrc-consumer.py --frames 1
rm -rf -- "$D"
```

Next physical gate: on a separately source-locked, uniquely bounded
candidate boot, use `v4l2-ctl --stream-mmap=4 --stream-count=8
--stream-to=-` for the **proven rear OV13858 pgAA V4L2 node**,
then pipe into the two tested stages with shell `pipefail` and
unconditional Golden return. Only the real hardware run can prove
this exact producer→GStreamer chain. Later work still needs a
normal app-discoverable rear endpoint and calibrated ISP/demosaic,
and independently decoded or genuine linear ISP front NV12.
