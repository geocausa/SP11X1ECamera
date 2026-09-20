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

## One combined, non-runnable NV12 kernel build — E004im

E004im builds the alternate V4L2 negotiation and the separately checked
kernel-native Y/UV DMA planner together in a single disposable SP11 ARM64
CAMSS module. Exact source-hash and geometry consistency checks and seven
negative integration tests PASS. QC10C stays first/default, NV12 STREAMON
fails before pipeline PM and the planner remains without runtime callers.
The module is not installed. Real linear ISP output and compression reset
are still open hardware gates. See E004im README.

## DMA-contiguous NV12 buffer gate — E004io

The next strictly uninstalled Golden-v4 kernel build strengthens the
experimental NV12 buffer planner against an overlooked scatter-gather DMA
hazard. Current vb2_dma_sg logic records the DMA address of the first SG
segment, but a large V4L2 allocation does not guarantee one continuous
DMA-mapped span for the 5,529,600-byte linear Y+UV image. E004io therefore
requires one **mapped** DMA segment with at least the entire image's byte
length, matching DMA base and computed UV offset. Eight offline positive/
mutation tests and a complete scratch ARM64 kernel build PASS. This may
reject valid multi-segment maps conservatively. No device DMA mapping
was actually exercised, and the stage remains uninstalled with NV12
STREAMON blocked before media power. ISP linear output and safe UBWC
reset still need separate physical proof. See E004io README.

## Kernel-compiled FULL Y/C NV12 dry-run plan — E004in

The next uninstalled SP11 kernel build combines the proposed NV12 V4L2 queue,
validated kernel-native Y/UV DMA plan and a **data-only** WM0/WM1 FULL
configuration proposal (image geometry, explicit Y/C strides, generic public
packer 3, per-client frame increments and DMA image addresses). Seven
positive/negative tests and the full ARM64 Golden-v4 scratch build PASS.
There are no new hardware call sites, and NV12 streaming remains blocked
before pipeline power. The real VFE680 global-reset callback is a no-op
completion; the accepted bus-stop function disables WMs without clearing
UBWC MODE_CFG. Explicit SP11 compression-state reset/verification and
RAW10-to-8-bit ISP output authority remain required before any real NV12
frames. See E004in README.

## Separate NV12 V4L2 negotiation, hard streaming gate — E004il

The exact-source-locked E004il experimental kernel overlay adds a proposed
2560x1440 single-memory-plane NV12 format to the dedicated X1E80100 front
PIX format table **after** the accepted QC10C default, with exact format
negotiation and discrete framesize metadata. Both the pipeline-PM prepare
stage and stream-start stage reject this NV12 format with EOPNOTSUPP *before*
any new camera power, pipeline or MMIO activity. Seven offline source/negative
tests and a complete scratch SP11 ARM64 kernel module build PASS. It is NOT
installed or enabled and the new format has not been tested via a real
video-device IOCTL. Real ISP linear output and safe UBWC reset remain
unproven. See E004il README.

## Kernel-native, uninstalled linear-NV12 planner — E004ik

A separate fail-closed SP11 kernel-sidecar source now compiles into a
**disposable/uninstalled** CAMSS kernel module against the actual Golden v4
build ABI. It explicitly rejects the existing QC10C video queue even if its
buffer has sufficient bytes, and checks an independently negotiated NV12
queue, exact geometry and stride, active frame, DMA alignment and both Y/UV
32-bit bounds. The sidecar has no active callers, format advertisements,
MMIO writes or module install; authorization always returns EOPNOTSUPP.
Six offline static/negative tests PASS. It is not yet a working NV12
capture mode: the SP11-specific linear ISP/BUS/UBWC transition remains
unproven. See E004ik README.

## Windows WinRT 1920x1080 NV12 target and offline bridge — E004ij

A previously overlooked SHA-pinned original SP11 Windows holder log establishes
an actual successful WinRT front Color/VideoRecord reader with NV12 1920x1080.
This is the app-facing format of that holder, not proof of stock Camera UI's
default resolution. Distinguish it from sensor RAW10 3840x2160 and internal
processed QC10C 2560x1440 FULL output. The offline-only E004ij prototype
converts two synthetic 2560x1440 linear-NV12 frames to two 1920x1080 NV12
frames through installed GStreamer. Both frames retained their distinct
constant Y and neutral UV; all six tests PASS. The converter **cannot** read
compressed QC10C. Actual linear ISP image capture/colourimetry and webcam
application integration remain unproven. See E004ij README.

## Offline linear-NV12 buffer implementation — E004ii

A separate fail-closed ARM64 C component now calculates the proposed NV12
Y/UV buffer and both FULL-client DMA addresses, rejecting undersized or
out-of-32-bit allocations and mismatched/compressed plans. Public Qualcomm
BUS ver3 source is SHA-pinned and confirms an uncompressed NV12 packer (3)
separate from TP10 (11). Twenty-six C/ASan/UBSan checkpoints and three
public-source-verifier Python tests PASS on SP11. This is offline code,
not a driver, physical frame or final Windows application resolution.
The actual SP11 bus programming and clean UBWC-to-linear state transition
still need independent authority. See E004ii README.

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
