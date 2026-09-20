# Ordinary Linux camera development

User-selected direction, 2026-09-20: practical RGB and ordinary-memory IR
processing alongside the still-blocked protected Windows-equivalence goal.

## Desktop inventory

Run `python3 tools/camera-desktop-status.py` (or `--json`). It queries
package/service presence and lists device nodes. It never starts capture.
Golden normally exposes no cameras; this is not itself a regression.
Desktop prerequisites now include the installed GStreamer libcamera plugin.

## Offline IR preview

`src/sp11-camera-hlos-worker/sp11-offline-preview.py --help` describes the
exporter. Input is ordinary nonprotected, neutral NV12 at 644x604, 1..16
frames. Supply an existing native `sp11-offline-nv12-stream.c` executable
in a user-owned /tmp directory through `--worker`. The unchanged worker is
compiled together with the eight `sp11-parity-worker`/SWABF/SWASF core
source files used by the E004hi verifier; the E004ie regression demonstrates
the exact build and export end to end. No signing is needed for this ARM64
userspace executable.

Example with your own already-prepared ordinary offline input and worker:

```sh
python3 src/sp11-camera-hlos-worker/sp11-offline-preview.py \
  --input /tmp/session/input.nv12 --worker /tmp/session/worker \
  --output /tmp/session/preview.y4m --playback-fps 30
gst-launch-1.0 filesrc location=/tmp/session/preview.y4m ! y4mdec ! videoconvert ! autovideosink
```

Preview files contain the processed image data and are deliberately retained
for viewing; delete them when no longer needed. Cadence is for playback only.
No camera, illuminator, protected buffer, face model or login interface is
opened by the exporter. Full transaction success is required before export.

## Work remaining

1. Front RGB: convert accepted ISP-processed 10-bit QC10C/TP10-UBWC YUV
   into a standard desktop format. It is neither Bayer RAW nor linear NV12.
   The current 27-frame launcher is not a continuous webcam. The installed
   EGL driver advertises compressed NV12 but only linear P030/P010; exact
   QC10C import and conversion remain unproven. Run
   `python3 tools/camera-gpu-import-status.py` to inspect current support.
2. Validate fresh RGB-only candidate capture, then repeated use, switching,
   suspend and application integration, preserving Golden.
3. IR: use offline previews for ordinary pixel work; useful live scene signal
   and independently validated illumination safety remain unresolved.
4. Keep passwords/security keys for login. Preview and face-model experiments
   provide neither liveness nor secure biometric authentication.

## Separate linear-NV12 offline candidate — E004ih

Qualcomm's public VFE BUS ver3 code has a distinct noncompressed NV12 FULL
Y/C format case. A source-locked, fail-closed offline experiment proposes
2560x1440 NV12 in 5,529,600 contiguous bytes at a *proposed* 2560-byte
stride and verifies that original QC10C files are unchanged (10 tests PASS).
The exact SP11 VFE1 uncompressed programming, pixel output and lifecycle
are NOT proven; there is no executable NV12 camera mode yet. See
`experiments/E004-front-ir-vd55g0/e004ih-linear-nv12-isp-authority/README.md`.
No new camera boot or IR change is authorized by this specification.

## Conversion implementation finding — E004ig

Official Mesa 26.0.8 and current upstream Freedreno snapshots explain the
missing compressed P030 advertisement: the generic DRI format mapping is
not backed by a TP10 texture/layout path in the inspected implementation.
A modifier-list edit or routine Mesa upgrade is not a demonstrated fix.
Next inspect a separate linear-YUV ISP output candidate, preserving the
accepted QC10C parity path, before any new camera runtime. Full details and
source hashes are in E004ig. No conversion implementation is claimed.
