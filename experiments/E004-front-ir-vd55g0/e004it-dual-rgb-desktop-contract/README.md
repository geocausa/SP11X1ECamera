# E004it — one front/rear RGB desktop readiness contract (offline)

2026-09-20. Parent: `aa345a2`. SP11 Golden-v4 Linux. No camera
capture, driver installation, new boot or GRUB mutation occurred.

## Why this is a separate step

The accepted physical rear OV13858 path is V4L2 `pgAA` / GRBG10 Bayer,
4076x2806, stride 5104, 14,321,824 bytes per frame. The E004is
**previously captured real rear colour bar** successfully produced a
private 1920x1080 NV12 frame through an uncalibrated Bayer-tile
preview and ordinary GStreamer video conversion. This establishes an
**offline frame-format path only**.

The accepted physical front IMX681 path is V4L2 `Q10C`, Qualcomm
TP10/UBWC **compressed processed YUV**, 2560x1440, 7,778,304 bytes.
It is NOT Bayer or linear NV12. E004ij converted only **synthetic
already-linear** NV12; an actual front-camera linear output or
independently verified QC10C decoder and safe UBWC state transition
are not available. A standard Linux application **cannot yet use
either camera as a reliable front/rear selectable live webcam**.

The earlier E004dz rear->neutral->front hardware one-shot proves a
particular bounded camera handoff, NOT sustained application-level
selection, automatic resource arbitration, simultaneous camera
streaming, standard app-facing endpoints or image-quality parity.

## Actual E004it changes

`src/sp11-camera-stack/rgb-desktop-output-contract.json` declares
two **distinct, pinned source formats**, their separate conversion
evidence, a common future 1920x1080/NV12 target, and per-camera
capability gates. Explicit `false` flags prevent a diagnostic from
advertising an unproven live app endpoint, QC10C as linear NV12,
default installation, protected IR illumination or Windows Hello
admission.

The existing read-only `tools/camera-desktop-status.py` now
validates this joint contract against the original
`src/front-imx681/desktop-output-contract.json` and the E004is
previous-rear-frame evidence. The user-visible and JSON diagnostic
report **both** camera profiles by sensor/physical source FOURCC,
independently identify rear **offline** real-colourbar NV12 and front
**synthetic-only** already-linear NV12 scaling, and keep both
application endpoints and live switching `NOT_VERIFIED`.
The script continues to inspect current packages, desktop services
and /dev node presence **without opening a camera, starting
services, loading a module or changing video devices**.

Current SP11 Golden diagnostic: standard libcamera/GStreamer/PipeWire
and portal packages are installed; required user services are active,
but no camera media/video nodes are exposed on protected Golden.
The present kernel does not provide a `v4l2loopback` module; no
virtual webcam was created or advertised. A virtual-device solution
must be separately built and validated, and its existence alone
cannot solve front QC10C decode or optical IQ.

## Validation and safety limitations

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004it-dual-rgb-desktop-contract \
  -p 'test_dual_contract.py' -v
python3 tools/camera-desktop-status.py --json
```

Fourteen offline tests PASS on SP11. Positive tests verify both
independent source/target shapes and read-only user/JSON status;
negative tests reject wrong rear geometry, missing rear conversion
evidence, wrong front FOURCC, misleading QC10C-as-Bayer/NV12 flags,
false claims of front/rear app readiness or switching, incorrect
NV12 output size, premature default-install permission and a
modified historical rear proof checksum.

This is **not** a two-camera live app, kernel capture or new colour
processing algorithm. The real rear offline preview remains
uncalibrated; no front real NV12 desktop frame has been produced.
E004iq's original QC10C DMA-guard physical regression was consumed
during a pre-camera GRUB-environment failure. E004ir only supplied an
uninstalled diagnostic hypothesis. Do not rearm E004iq or enable
IR illumination/protected authentication on the strength of this
desktop-status contract.

## Next implementation gates

Rear: produce calibrated colour from actual normal-scene rear Bayer
frames; verify bounded continuous image processing and correct
orientation, colour and frame cadence; expose an ordinary video
application endpoint with exact source identity. Front: first prove
safe uncompressed output or real QC10C decompression, then use the
validated downstream NV12 path for genuine front frames and add its
own video endpoint. Lastly verify user-facing selection/switching,
shared ISP ownership, repeated starts/stops, suspend and recovery
for **both** cameras before considering a reversible installation.
