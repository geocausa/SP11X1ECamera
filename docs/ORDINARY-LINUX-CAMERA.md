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

## Real rear optical NV12 preview, front bootstrap packaging gate — E004ja

The distinct, consumed E004ja one-shot successfully captured the rear
OV13858 hardware colourbar plus **eight distinct real normal-scene Bayer10
frames** at 29.9504 fps; the rear-to-front handoff route was neutral.
The eight normal optical Bayer frames were privately converted to eight
distinct 1920×1080 NV12 previews on Golden; the real eight-frame output
was accepted by GStreamer. Mean conversion-only time was 3.4232 ms per
frame, and the batch I/O+conversion average was 5.8776 ms per frame.
This is a fast **uncalibrated offline colour proxy**, not yet a live
ordinary Linux camera endpoint. The optical frames and previews were
kept private on SP11 then deleted after non-sensitive evidence collection.

The front QC10C launcher stopped **before streaming**, because the
accepted package's git-archive staging excludes the pinned 41,088-byte
`r4-bootstrap.bin` through `*.bin` ignore. The local accepted file
exists and hashes to the exact launcher-pinned digest; a new candidate
must stage it independently as a private, separately verified sidecar,
then prove a launcher dry-run without hardware before attempting live
front capture. The E004ja one-shot and private system assets were
retired; the physical QC10C DMA guard remains untested. The E004iy
reversible GRUB writer ordering passed again on E004ja and remained
installed. See E004ja README and RESULT.json.

## First combined rear/front candidate — E004iz consumed before streaming

The new E004iz one-shot verified that both GRUB writer services completed
successfully and in the intended order on a real camera-capable candidate
boot, then loaded the exact accepted camera package with the new front
QC10C mapped-DMA guard and discovered the media topology. The initial
idle graph unexpectedly had **both rear links already enabled** and
both front links disabled (`rear-only`); the script had expected neutral
and therefore stopped before any front or rear frame. Its cleanup
explicitly returned the graph to neutral, and the automatic reboot
returned to protected Golden with no loaded camera modules. E004iz's
identity and all private boot/package staging were retired, never
rearmed. A new independent candidate must recognize only the verified
idle rear-only or neutral graph, explicitly neutralize it and prove
neutral before starting the accepted rear-to-front sequence. The
front real DMA guard and normal rear optical output remain physically
untested by E004iz. See E004iz README/RESULT.json.

## Reversible GRUB writer serialization — E004iy

After the disposable-file E004ix race reproducer, a scoped removable
`grub2-common.service` drop-in now requests and waits for the stock
`grub-initrd-fallback.service` to finish before writing the shared
GRUB environment. The original Ubuntu commands, persistent Golden boot
and kernel/DTB/initrd remain unchanged. A controlled real service start
and an ordinary Golden cold reboot both completed with BOTH GRUB services
successful and in the intended order. No transient environment-read
failure appeared on that reboot; its Golden GRUB environment bytes
matched the pre-install private snapshot. This is **one** Golden reboot
and does not prove indefinitely reliable boot behaviour or authorize
unbounded camera access. The ordering drop-in is still installed with
an independent rollback script and no camera or one-shot boot armed.
See E004iy README and RESULT.json.

## GRUB writer concurrency reproduced without touching Golden — E004iw/E004ix

E004iw's new camera-free candidate proved that a **read-only GRUB
environment check can pass after both stock GRUB writer services reach
terminal state**, and returned to Golden. But `grub2-common.service`
failed an environment read during that candidate boot **and during the
next normal Golden boot**, while `grub-initrd-fallback.service` finished.
E004ix reproduced transient GRUB read/write failures on separately
created **/tmp environment fixtures**: 120 simultaneous-reader/writer
trials produced two reader and two writer failures; the 120 serialized
controls had zero failures. The Golden GRUB environment checksum stayed
unchanged. A minimal proposed service ordering has been verified on
**disposable copies of the stock units only** and is NOT installed.
This supports a writer-concurrency hypothesis; it does not conclusively
establish the cause of the earlier E004iq camera-boot failure or certify
a corrected physical capture boot. Both live RGB camera paths remain
gated. See E004iw and E004ix README/RESULT evidence.

## Camera-free boot diagnostic status — E004iv

The original QC10C DMA-guard one-shot E004iq aborted at a GRUB environment
read before camera activation. A new camera-free E004iv one-shot established
that the two GRUB environment writers can be ordered to **finish before**
the diagnostic service starts. E004iv's root-owned script then failed an
unrelated Git ownership check **before reaching the GRUB read**; it created
no camera attempt and the automatic service reboot returned to Golden.
A read-only owner-scoped Git command was subsequently tested on Golden;
it does not set a global trusted directory. The E004iv identity and
all temporary boot assets are retired. The original GRUB failure root
cause and real QC10C DMA guard remain unproven. No new front/rear video
endpoint is implied; see E004iv README and RESULT.json.

## Fast bounded rear Bayer-to-NV12 offline batch — E004iu

The E004is rear Bayer-to-NV12 preview was functionally correct but
needed roughly 53–56 ms per archived colour-bar frame on SP11, too slow
for a single-threaded 30 fps pipeline. E004iu adds a separately
validated, **uncalibrated** C11 nearest-Bayer-tile colour proxy. It
reads actual accepted 4076x2806, stride-5104 `pgAA` rear frame
payloads and outputs real 1920x1080 NV12 bytes. A 27-frame offline
batch of **27 repetitions of one previously captured rear test-pattern
frame**, not fresh optical captures, averaged approximately 3.0 ms
conversion time or 5.2 ms including that batch's input/output file
operations per frame; its resulting 27-frame NV12 stream passed
GStreamer. Fifteen source/colour/sanitizer/IO/batch regression tests
pass. These timings exclude compiling the offline helper, live sensor
acquisition and application presentation. No full spatial demosaic,
calibrated IQ, **live 30 fps camera** or app device is proven; front
QC10C compressed data cannot use this Bayer converter. A new
privacy-controlled normal rear sample, proper colour processing and
a separate standard rear video endpoint are still necessary. See
E004iu README/RESULT.json.

## Both RGB cameras: source-aware desktop readiness — E004it

The read-only `python3 tools/camera-desktop-status.py --json` now reports
**rear OV13858 and front IMX681 independently**. A new shared output
contract validates the accepted rear `pgAA`/GRBG10 frame against E004is
real archived-rear-to-NV12 offline evidence, and the accepted front
`Q10C` compressed surface against its existing exact hardware contract.
The diagnostic reports both possible future 1920x1080 NV12 application
endpoints as `NOT_VERIFIED`; a synthetic-only front linear NV12 scaler
is NOT mistaken for a working QC10C decoder or a real front stream.
Fourteen positive and negative tests pass, including rejection of false
live-device, switching and default-install claims. SP11 already has its
libcamera/GStreamer/PipeWire prerequisites, but no cameras are exposed
on protected Golden, and the running kernel lacks v4l2loopback.
No kernel/video/IR module is loaded and the read-only diagnostic opens
no camera. See E004it README and `src/sp11-camera-stack/rgb-desktop-output-contract.json`.

## Rear RGB ordinary-video prototype — E004is

The accepted OV13858 rear path already captured 4076x2806 GRBG10 packed
Bayer at an aligned 5104-byte stride and approximately 30 fps; its
14,321,824-byte colour-bar frame and eight normal frames are documented
in E004dz. E004is now **unpacks a checksum-verified previously captured
rear colour-bar frame**, builds a basic 2x2 Bayer-tile colour proxy,
centre-crops to 16:9 and writes private 1920x1080 NV12. A real
GStreamer `rawvideoparse ! videoconvert ! fakesink` pipeline accepted
that frame. Nine offline tests pass, including packed-bit order,
colour layout, incorrect-format rejection and file isolation. The
preview is not colour-calibrated or full demosaic, and no live desktop
video device or sustained throughput is claimed. The previously accepted
front QC10C compressed format cannot be fed to this rear converter;
front's E004ij scaler needs genuine linear NV12 not yet available
from the SP11 front ISP. Both cameras still need standard app-facing
devices, repeatable selection and per-camera IQ/PM/cadence checks.
See E004is README/RESULT.json.

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

## Read-only boot-environment diagnostic — E004ir

Review of the consumed E004iq candidate boot found that two systemd GRUB
services which modify grubenv started in the same second as the failed
camera preflight; this is a plausible but unproven scheduling hazard. The
original invalid environment bytes were not retained. E004ir supplies an
**uninstalled, diagnostic-only** unit ordered after both GRUB writers and
a read-only script that rejects unreadable GRUB state, a non-Golden saved
default, a still-armed or absent next_entry and mismatched candidate boot
markers. Eleven temporary-fixture tests and systemd-analyze verification
passed on SP11. This does not authorize a replacement one-shot, and it
cannot establish the cause of the prior invalid GRUB environment. See
E004ir README/RESULT.json. No camera or boot configuration was changed.

## E004iq QC10C-only physical one-shot — pre-camera abort, retired

The unique E004iq candidate booted on SP11 but its dedicated service failed
at the initial `grub-editenv` preflight (`invalid environment block`). The
service triggered the configured reboot into protected Golden; the consumed
candidate captured **zero frames** and never loaded its camera module or
reached real mapped-DMA validation. The one-shot identity, private staging
root and service were retired; the original QC10C driver is unchanged. The
candidate-only boot-environment read failure is not explained by the valid
Golden GRUB state after return, and this identity must **not** be rerun.
See E004iq `evidence/PRE-CAMERA-ABORT.json` and `RESULT.json`. The next
candidate must establish the boot rollback/preflight contract independently
before a new unique test identity can be justified. NV12 linear output and
UBWC-state reset remain separate open gates.

## Separate bounded QC10C-only physical regression candidate — E004iq

A provenance-correct rebuild reproduced the accepted hardware module hashes
using the originally recorded kernel source frontend, and the resulting
current stack manifest matches the already validated E004id 50-file package.
E004iq additionally compiled a QC10C-only module with the *sole* code delta
being the E004ip mapped DMA-coverage guard in `camss.c`. Unlike earlier
uninstalled E004io combined scratch modules, this candidate does **not**
advertise the proposed NV12 format. A unique, non-default, strictly
one-shot front-RGB test is prepared with a root-owned private package,
source-pinned 27-frame `shadow` launcher and an automatic return to the
persistent Golden GRUB default after success, failure or timeout.
At the offline preparation checkpoint, no boot was armed, camera opened or
new module installed; a live mapped-buffer/optical result is **not** yet
claimed. IR illumination/login are excluded and ISP linear NV12 plus
compression-state reset are independently unresolved. See E004iq README.

## QC10C mapped-DMA safety candidate — E004ip

Source review found the already accepted front QC10C capture path checks the
V4L2 allocation length and 32-bit base/end but does not establish that the
entire 7,778,304-byte compressed surface is covered by a continuous
*device-mapped* DMA address range. An E004ip scratch-only kernel patch now
checks actual mapped scatter-gather entries for complete adjacent DMA
coverage, supporting multiple contiguous DMA segments and rejecting gaps,
short mappings, zero-length entries and stale cached DMA bases. The exact
inserted C guard passed ten synthetic cases each under GCC and Clang
ASan/UBSan, with six source-integrity/negative tests and a full ARM64
Golden-v4 uninstalled CAMSS module build PASS. This is NOT yet the accepted
QC10C driver: real SP11 mapped-buffer behavior and bounded live capture
regression remain to be verified before installing this candidate.
NV12 STREAMON remains blocked and separate ISP/UBWC linear-output authority
is unchanged. See E004ip README.

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
