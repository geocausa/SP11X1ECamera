# E004iw — GRUB one-shot environment diagnostic, owner-scoped Git preflight

## Actual candidate result — read-only check passed; stock writer failed

E004iw booted once as candidate boot `112069bc-a12f-45a2-9aef-046a28f79f8a`. Its owner-scoped Git checks succeeded, `grub-initrd-fallback.service` finished, and the diagnostic read a private 1024-byte candidate GRUB environment snapshot (SHA-256 `151df76c93e71843bb39c645a8a9d37d524b3e3e347f3d6eb3a4418cb85493ba`) and successfully verified `saved_entry=sp11-audio-fullio-v19c` and `next_entry=`. The service returned SP11 to Golden boot `9523efbe-8d0b-48c9-ba8c-ec1ffe27f2fb`. However `grub2-common.service` **failed earlier in the candidate boot** with `cannot read /boot/grub/grubenv: Invalid argument`. The same error occurred in `grub2-common.service` on the subsequent ordinary Golden boot; in both cases the fallback service finished and a later environment read was valid. Thus E004iw validates **post-writer read-only preflight**, not successful execution of both stock GRUB writers or resolution of the original E004iq failure. A disposable-file race reproducer is E004ix. All E004iw private files, service and GRUB entry have been retired; this unique identity is consumed. No camera hardware was accessed or further camera boot authorized by this outcome. Redacted results: `evidence/OBSERVED.json` and `RESULT.json`.

2026-09-20. Parent: `f0e0a00`. Unique, **camera-free** one-shot
test of the exact failure preventing further front and rear live capture.

The consumed E004iq camera candidate stopped at `grub-editenv:
invalid environment block` before opening a camera. E004iv then
proved on a real diagnostic boot that both `grub2-common.service` and
`grub-initrd-fallback.service` **finish before** a diagnostic service
which orders itself `After=` them; however its root-owned runner
aborted even earlier because Git refused to inspect a user-owned
checkout. Its service returned SP11 safely to Golden, and all its
assets/identity were retired. No candidate boot so far has proven a
valid GRUB environment after both writer services finish.

E004iw reproduces the read-only E004iv diagnostic with a NEW unique
boot ID and replaces **both** root `git -C` calls with
`runuser -u geoca -- git -C`, which reads the exact original user-owned
checkout without modifying global Git trust or repository state.
The owner-scoped invocation was independently tested on Golden to
match the ordinary user invocation. Ten E004iw tests plus the eleven
earlier E004ir fixture/Golden environment tests pass offline.

This boots the original **Golden kernel, Golden DTB and Golden initrd**
with the exact additional unique diagnostic marker and a blacklist
for all camera modules. It installs no camera module and does not
open /dev/video, /dev/media, an optical frame, IR, SecurePD, or PMIC.
The candidate-only conditional systemd service waits until both
GRUB writer units finish, enforces a bounded timeout, and triggers
a reboot to the unchanged persistent Golden default on either success
or failure. The runner refuses unexpected camera nodes/modules and
a reused attempt marker, snapshots the live candidate GRUB environment
into a PRIVATE root-owned file for possible failure analysis, and
then performs a read-only `grub-editenv list`. It strictly verifies
the persistent Golden default and consumed empty next-entry.
No script repairs an invalid environment block.

Workflow is explicit and NOT a scheduled task: commit/push these
source-locked files, run `install-unarmed.sh`, verify private root
assets and the inactive service, then arm `arm-once.sh` once.
After the observed return to Golden, inspect the private result,
store only a non-sensitive outcome under `evidence/OBSERVED.json`,
and retire all unique assets using `retire-after-golden.sh`.
Original candidate grubenv bytes and journal stay private and
must not be committed. This identity must never be rearmed.

A passing E004iw result would validate the **post-writer GRUB
read-only preflight in one camera-free candidate boot**. It would
not prove that E004iq's earlier fault was a concurrent-writer race;
it also would not validate E004ip's front QC10C mapped-DMA guard,
rear Bayer colour calibration, true front linear NV12/QC10C
decompression, either live Linux application endpoint, camera
switching, native IR illumination or Windows Hello. Future camera
experiments still require a distinct source-locked physical one-shot
and independent fail-closed safety checks.
