# E004iq — one-shot QC10C DMA-coverage regression, front RGB only

Date: 2026-09-20. Parent: `0cbd06f`. SP11 Golden v4. E004ip isolated
QC10C DMA-mapped coverage check is the **only** source delta from the
original CAMSS driver; the earlier E004io alternate NV12 format overlay
is **not installed or compiled into this candidate**.

## Actual consumed one-shot result — PRE-CAMERA ABORT

The E004iq identity was armed once on 2026-09-20. SP11 booted the intended
candidate kernel/DTB and its conditional systemd service started, but at
16:16:55 BST the candidate service's initial `grub-editenv` read failed:
`invalid environment block`. The service exited with RC=1 **before its
camera-attempt marker was written**, before loading any camera module,
opening a video device or executing the 27-frame launcher. Thus **zero
QC10C frames were captured and the new mapped-DMA guard was NOT tested
on real vb2 buffers**. No same-boot retry occurred.

The boot-specific service's exit hook rebooted the machine into the
persistent Golden entry. The Golden-return boot ID was distinct, the
protected kernel and saved GRUB default were verified, `next_entry` was
empty, no camera modules remained, and Golden's `grubenv` was readable.
The *underlying cause* of the candidate-only invalid environment block
has not been established; do not assume that bypassing this check would
be a safe fix. The unique E004iq service, private package, GRUB entry,
candidate boot files and temporary raw-image directory were retired under
independent pre-camera-abort checks. The E004iq identity is **consumed:
do not rearm it**. The next work is a separately proven candidate-boot
GRUB environment/rollback contract, not another unguarded camera run.
See `evidence/PRE-CAMERA-ABORT.json` and the updated `RESULT.json`.

## Why this separate candidate is needed

The existing front QC10C camera already completed its accepted R27/27-frame
production run, but `camss_x1e_pix_v4l2_buffer` did not prove that all
7,778,304 bytes of the single compressed surface were covered by
contiguous, device-mapped DMA addresses. E004ip's source-locked guard
walks the mapped SG entries, accepting adjacent DMA ranges and rejecting
gaps/short spans before frame ownership and bus-address programming.
Offline kernel compilation and synthetic positive/negative testing passed.
Actual mapped SP11 vb2 buffers require **one strictly bounded physical
regression** before accepting this extra check.

## Exact components and non-default scope

The reproducible front kernel build uses the **provenance-pinned** kernel
frontend `/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src`,
not the newer E004in offline C-test frontend. With the pinned Golden v4
build/header tree it reproduced all seven accepted hardware binaries and
the unified DTB exactly; rebuilt full package SHA-256 of its 50-file
manifest is `11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646`,
equal to the previously accepted E004id current-package positive
lifecycle evidence. The old E004en live capture used a **different,
historical** front package manifest `3f3bf8d3...`, so copying its
installer/runtime preflight unmodified would be invalid.

The new candidate is built from *unmodified original CAMSS source*
except the one E004ip validator insertion in `camss.c`. All other
original files match exactly. Candidate `qcom-camss.ko` SHA-256:

`950ca403fc224873762001a013ec278bf93b041eb12e1ad7a0bd3687c86b4f56`.

The accepted original module remains separately preserved with SHA-256
`862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7`.
Both have the running Golden-v4 kernel ABI.

The package is kept under a unique root-owned
`/var/lib/sp11-camera-e004iq/stack`, **not installed as the system's
default**. A unique GRUB one-shot candidate boots the original Golden
kernel and previously accepted three-camera DTB, with all camera modules
blacklisted until the bounded script loads them explicitly. The root
service runs **only** if the candidate-specific kernel command line is
present. Its `ExecStopPost` calls reboot after success, failure or a
360-second start timeout. The persistent GRUB `saved_entry` remains
`sp11-audio-fullio-v19c`; the unique `next_entry` is consumed by
GRUB at the one-shot boot. There is no scheduled recurring task.

`run-once.sh` checks package, module and repository identities,
proves idle/binding state, invokes only the accepted front RGB
Color/VideoRecord-like QC10C V4L2 route in `shadow` mode (G1..G3
startup control writes; **no later native sensor writes**), verifies
27 ordered 7,778,304-byte frames, no kernel Oops, three suspended
sensors and a neutral final media route, then exits. It does **not**
start native IR, illuminate an emitter, write PMIC, use protected
SecurePD/Hello, promote the camera as default, or authorize NV12.

The one-shot writes private optical frame data and logs only to the
root-owned `/var/lib/sp11-camera-e004iq/output`. Do not commit,
publicly share or export those frames. After inspecting and recording
bounded outcome details, `retire-after-golden.sh` removes the private
frames, unique boot entry, service and staging root.

## Lifecycle and proof boundaries

1. `install-unarmed.sh` requires clean tracked Git, protected Golden,
   no loaded camera module, exact package/module SHA-256 values,
   source-locked scripts, an unused GRUB identifier and an empty
   `next_entry`. It installs the unique root-owned assets, enables a
   **candidate-kernel-conditional** systemd unit, and regenerates GRUB
   **without arming any boot**.
2. `arm-once.sh` independently checks package and candidate identities,
   preserved Golden, the enabled conditional service and empty one-shot
   state, arms the unique `grub-reboot` entry once, and invokes reboot.
   After the candidate kernel starts, the conditional unit performs the
   run and reboots into protected Golden even on a bounded test failure.
3. Only after a verified Golden return and inspected test outcome should
   `retire-after-golden.sh` remove **only** E004iq-owned roots.
   If the candidate fails before systemd starts, the persistent Golden
   boot is still preserved for a later reboot, but software cannot
   guarantee recovery from a pre-kernel boot failure.
4. Do not run E004en again; that historic identity is consumed. Do not
   infer that a passing QC10C DMA-coverage regression solves the
   independent ordinary desktop NV12 output / UBWC reset blockers.

No live-frame result is claimed in this README until one-shot evidence
exists. No login, IR illumination or default-camera activation is part
of the test.
