# E004ja — bounded rear Bayer then front QC10C, idle-rear normalization

## Actual E004ja outcome — rear real frames and NV12 pass; front packaging gate failed

The single E004ja candidate boot `5c89b663-0a87-4108-80ce-c53b44987e52` passed the ordered GRUB-writer and source-lock gates, started with a **neutral** graph, captured one byte-exact rear hardware colourbar frame, then **eight distinct real rear optical Bayer10 frames** at 29.9504 fps. It neutralized the rear route before front discovery and retained a neutral final graph. On Golden return `841a0a8a-a718-4e79-bc56-6041674e55e3`, the private real eight-frame Bayer stream was converted offline to eight distinct 1920x1080 NV12 preview frames (SHA-256 `467c093db022a72044839826142a24d4f3f7bd0242c9f0e88aacf29cdad7cfff`) at 3.4232 ms average conversion alone, 5.8776 ms including batch input/output; a real GStreamer NV12 consumer accepted all eight. This is a **basic uncalibrated offline colour proxy**, not a calibrated or live webcam. Raw optical frames were kept private on SP11 and must be deleted after evidence collection.

The **front RGB QC10C test never reached streaming**: the accepted launcher rejected `R4 bootstrap identity` because its required 41,088-byte `userspace/iq/authority/r4-bootstrap.bin` was absent from the Git-archive-built package. The original local accepted file matches the launcher SHA-256 `1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa`, but is excluded by the repository's `*.bin` ignore pattern; the accepted 50-file package manifest never included it. This is a packaging omission, not proof of a front DMA guard failure. A future distinct candidate must **separately hash and privately stage the R4 sidecar and validate the launcher dry-run without hardware** before arming. The E004ja run is consumed, must not be rearmed and has no front-QC10C hardware verdict. Non-sensitive summary: `RESULT.json`.

2026-09-20. Distinct new one-shot candidate after retired E004iz. Parent
`4f4d2e9`. The goal is to advance **both** rear OV13858 and front
IMX681 into selectable ordinary Linux RGB cameras. This is a bounded
hardware regression, not an application release.

E004iz's real candidate loaded the exact accepted three-sensor package
and source-locked QC10C mapped-DMA guard, but discovered that the
newly-bound media graph was already `rear-only`: exactly both mutable
rear links enabled, both front links disabled. E004iz had asserted
`neutral` and failed closed **before streaming**, then cleaned the
graph to neutral and returned to Golden. Its unique GRUB entry,
service and root staging were retired and must NOT be rearmed.

E004ja uses a NEW boot entry, root staging and one-attempt identity.
Its root service waits for both Ubuntu GRUB writer services to
finish, explicitly verifies that both `ExecMainStatus=0`, that
their monotonic start/end times are nonzero and ordered, and checks
the E004iy removable GRUB ordering drop-in byte-for-byte. It checks
the exact persistent Golden saved entry and consumed `next_entry`,
the boot command-line marker, exact source-locked package and driver
hashes, and no preexisting camera nodes/modules/processes. It boots
the protected Golden kernel/initrd with the previously accepted
three-sensor candidate-only DTB; the four camera modules are blacklisted
until preflight passes. It uses the owner-scoped read-only Git
invocation to avoid E004iv's root-ownership failure.

The only intentional behavioural difference from E004iz is at
**idle media graph normalization**. E004ja accepts *only* an
initially neutral graph, or the exactly classified idle
`rear-only` state observed in E004iz (both rear links and neither
front link enabled). For `rear-only`, it calls the existing
`media-ctl` controls to disable precisely those two **mutable**
rear links, then reads the graph again and requires `neutral`
and three suspended sensors. It rejects partial, front-only,
mixed and unexpected graphs before initiating capture.

Then it follows the previously accepted bounded rear route and
4076x2806 `pgAA` GRBG10 format: one byte-exact hardware colourbar
frame, restore normal sensor mode, eight private optical Bayer
frames with ordered sequences, exact buffer sizes and approximately
30fps timing; disable the rear route, prove neutral, and use the
accepted front QC10C shadow-mode launcher to capture 27 ordered
7,778,304-byte frames with the E004ip DMA guard. It proves suspended
sensors, neutral final graph and absence of kernel Oops/IR emitter
markers. All optical data remain in the private root-owned
`/var/lib/sp11-camera-e004ja/output` staging area for bounded
**local-only** offline rear NV12 conversion after Golden return.
There is NO IR illumination/stream, PMIC write, protected signing,
true front NV12 promise, or default camera installation.

The test is strictly **one attempt**. An unconditional systemd
`ExecStopPost` reboots to the untouched persistent Golden on success,
failure or the 360-second timeout. After verified Golden return,
collect only non-sensitive status, hashes and frame counts; retire
the consumed service, GRUB entry and private staging. If the
candidate stops at any gate, do not retry it in the same boot
or rearm the identity.

All binaries were independently rebuilt from original accepted
Golden-v4 camera source after E004iz's files were erased, with
hardware manifest `ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c`,
package manifest `11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646`,
and new mapped-DMA candidate module SHA-256
`4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d`.
Eleven offline positive/negative tests cover root-safe preflight,
exact manifests and ABI, both media-route transitions, provenance,
one-use boot guard, no front IR activation and exact shell/GRUB
syntax. Offline validation does **not** establish successful live
camera capture, real front QC10C DMA mapping, or usable
front RGB/NV12.
