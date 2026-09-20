# E004jc — root-private R4 sidecar and bounded rear→front DMA regression

## Real E004jc result — both physical camera routes PASSED

The uniquely identified candidate boot `c344cd57-8dc8-4a00-a7a0-88c79d238616`
passed both ordered Ubuntu GRUB service gates, exact SHA-pinned camera
package and R4 sidecar preflight, and the real packaged launcher
offline plan. The route progression was `neutral → rear-only → neutral
→ front-only → neutral`. The rear OV13858 produced one byte-exact
hardware colourbar and **eight distinct real optical Bayer10 frames**
at **29.9501 fps**. After a verified neutral handoff, the front IMX681
produced **27 distinct and sequential QC10C frames, each 7,778,304
bytes**, using the exact E004ip mapped-DMA coverage guard module
`4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d`.
Its 24-row producer passed with the `shadow` post-G3 policy and
**zero later native sensor writes**. All three sensors suspended after
the streams, the final graph was neutral, and saved kernel health
showed no Oops, panic or IR-illumination marker.

The one-shot service exited successfully and rebooted to protected
Golden boot `234821d0-ae99-4b66-a452-b7fb3c2376fa`, with saved
Golden `sp11-audio-fullio-v19c`, empty `next_entry`, no camera
module/node and clean tracked Git. The consumed identity was
explicitly checked not to rearm. The unique GRUB entry, service,
boot assets, derived R4 capsule sidecar, optical frames, QC10C frames
and all private root staging were then deleted or retired. Only
redacted metadata is committed: `RESULT.json` and the historically
named no-rearm sentinel `evidence/PRE-CAMERA-ABORT.json` (the latter
does **not** mean E004jc aborted; E004jc **passed**).

**Precisely what was proven:** the bounded *real SP11 V4L2* front QC10C
producer can acquire 27 frames while the new mapped-DMA coverage
check runs in the candidate CAMSS driver, and safe rear-to-front
camera hardware handoff succeeds. This is not a proof that every
future DMA mapping will be contiguous or that a different camera
format is safe. The validated guard is **not yet installed as the
production/default module**.

**Precisely what is still missing:** real front QC10C decoding or
verified hardware ISP output to *genuine linear* NV12, a live rear
Bayer→NV12 delivery service with proper image-quality calibration,
and two ordinary Linux application-facing selectable video endpoints.
Do not mislabel the 27 compressed front frames as webcam-ready NV12
or claim full Windows parity.

2026-09-20. Parent `55e0dd1`. New unique one-shot, not a retry
of consumed E004iq, E004iz or E004ja. Golden v4 is preserved.

## What the immediately preceding real boot established

E004ja's source-locked candidate successfully captured the rear
OV13858 hardware colourbar and eight distinct normal optical 4076×2806
Bayer10 frames at 29.9504 fps. All eight were converted privately
offline to distinct 1920×1080 NV12 frames; GStreamer accepted the
full eight-frame stream. The rear route was neutral before front
discovery. However the front launcher stopped with
`RuntimeError: R4 bootstrap identity` **before streaming**. The
accepted source contains a 41,088-byte derived front R4 bootstrap
capsule, but Git's `*.bin` ignore pattern excludes it from the
git-archive-built canonical 50-file camera package. The source
capsule exactly matches the SHA-256 hardcoded by the accepted
front launcher:

`1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa`

E004ja returned to Golden and was fully retired, including its
private optical frames and transient preview. It proved NOTHING
about the physical new front mapped-DMA guard, which remains
untested until a launcher actually streams.

## Exact corrective change, independently testable without hardware

E004jc rebuilds the same accepted canonical three-sensor module/DTB
package and the same E004ip QC10C-only mapped-DMA guard module.
No production CAMSS source or Golden kernel/DTB/initrd is changed.
The source-pinned installer verifies the original package's exact
manifest SHA
`11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646`
and unchanged accepted module, plus the candidate module SHA
`4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d`.
The installer verifies the **separate original source** R4 capsule
is a regular, non-symlink 41,088-byte file with exact pinned SHA,
proves it was absent from the Git-archive-built package, and
copies it to the root-private candidate package as a **separately
SHA-verified 0600 sidecar**. It does not reclassify a missing
package file as if it were included in the canonical 50-file
manifest. The ignored capsule is never committed, published
or exported.

Before arming, the installer launches the real **packaged**
front launcher in a hardware-free `--topology-file` dry-run
against the accepted archived unified media graph. It asserts
`execute=false`, the exact expected R4 digest, 27-frame
QC10C source, unchanged shadow policy, the exact candidate
R4 path and **no output directory created**. The dry-run plan
is stored in root-private staging. The arming script verifies
the sidecar, package, module and dry-run plan again; the candidate
root service independently checks the R4 size/hash and plan
BEFORE any camera module or sensor is touched. Fourteen offline
positive/negative tests passed on protected Golden; none
requires opening a camera.

## Unique bounded candidate, no IR

A unique GRUB `next_entry` boots the protected Golden
kernel/initrd with the previously accepted three-sensor
camera-capable DTB. Persistent Golden `saved_entry` stays
`sp11-audio-fullio-v19c`. The scoped systemd service runs only
when its exact candidate kernel marker is present, waits for
both stock GRUB writer services to complete with actual
successful and ordered execution timestamps, verifies the
source-locked E004iy reversible ordering drop-in, exact
candidate package and no active camera process, and writes
a one-attempt consumed marker before camera activation. It
automatically reboots to protected Golden on success,
failure or bounded timeout; the identity must never be
rearmed.

On a clean idle unified graph, or the exact previously
observed idle `rear-only` state, the candidate explicitly
proves a neutral graph and three suspended sensors before
capture. It repeats the accepted bounded rear hardware
colourbar/normal eight-frame Bayer10 sequence and
neutralizes the rear route. Then it launches ONLY the
existing front IMX681 RGB QC10C route with
`--post-g3-write-policy shadow` for 27 frames through
the new DMA-mapping guard, checking ordered frame payloads,
sensor suspension, neutral final route and kernel health.

The front bytes remain **compressed QC10C, not usable
linear NV12**; this experiment cannot complete the
front desktop camera without independently proven
decompression or a safe true linear ISP output. The
rear output remains an uncalibrated offline-preview
colour proxy, not a registered virtual desktop camera.
No IR sensor stream, physical IR illumination,
PMIC/firmware write, SecurePD/Windows Hello signing
or unapproved native front post-G3 writes are permitted.
All optical bytes remain private and must be deleted
after redacted post-Golden evidence collection.

## Run offline tests first

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jc-rear-front-r4-sidecar-one-shot \
  -p test_two_rgb_one_shot.py -v
```

Only a separately recorded **real on-machine one-shot result**
may establish whether E004ip's mapped-DMA guard accepts
actual vb2 DMA mappings and whether both live camera paths
hand off in the same bounded boot.
