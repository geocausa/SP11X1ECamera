# E004iw — GRUB one-shot environment diagnostic, owner-scoped Git preflight

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
