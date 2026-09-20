# E004iv — one-shot, camera-free GRUB-environment diagnostic

## Actual single-use result — E004iv pre-observation abort, retired

The E004iv one-shot booted the unchanged Golden kernel/DTB and its service started only **after both GRUB environment writers finished** (confirmed by the candidate's monotonic systemd journal). However the root-owned diagnostic attempted `git -C` in the user-owned camera checkout; Git rejected the worktree ownership before the script created its attempt marker or copied/read GRUB's environment. The candidate service exited RC=1 and its automatic-return callback rebooted SP11 to persistent Golden. The diagnostic did **not** read or verify candidate GRUB state, load a camera module or capture a frame. The original E004iq environment-corruption cause is still unproven. A read-only `runuser -u geoca -- git -C ... rev-parse HEAD` command was verified independently on Golden without changing global Git trust settings, but has NOT yet run in a candidate boot. All E004iv-owned root staging, service and GRUB assets were subsequently retired; do not rearm this consumed identity. Non-sensitive outcome: `evidence/OBSERVED.json`. A separate unique candidate is required for any later check.

2026-09-20. Parent `1c62d42`. The user requires **both** rear OV13858
and front IMX681 usable as ordinary Linux cameras; a previous front QC10C
DMA-guard physical regression, E004iq, instead aborted before loading
camera hardware because a GRUB environment read returned `invalid
environment block`. The old E004iq identity is retired and must not
be rearmed.

This stage tests **the test-boot mechanism**, not a camera. The original
candidate journal shows the `grub2-common.service` and
`grub-initrd-fallback.service` GRUB-environment writers starting in
parallel with E004iq's failed environment read. That coincidence does
not establish a race as the cause; the original transient invalid GRUB
environment bytes were not retained.

## Strict new one-shot diagnostic scope

A unique `sp11-camera-e004iv-bootenv-diagnostic-one-shot` GRUB entry
uses the **unchanged protected Golden kernel, Golden DTB and Golden
initrd**. Its camera blacklist is carried over, no experimental camera
package is installed, and its root-owned conditional systemd service
waits *after* both GRUB writers. The service requires its unique
kernel command-line marker; it never runs on ordinary Golden boots.
A private diagnostic script accepts only the Golden kernel, refuses
camera nodes/modules, records a one-use attempt marker, copies the
current GRUB environment bytes privately and tries a **read-only**
`grub-editenv list`, asserting `saved_entry=sp11-audio-fullio-v19c`
and explicitly present `next_entry=`. Any failure exits closed; it
does not repair or bypass a damaged environment block. The service
has a bounded timeout and an unconditional exit callback to reboot
into the unchanged persistent Golden default after its one attempt.
A pre-kernel boot failure cannot be recovered by the service itself,
although the saved boot default remains Golden.

The original private GRUB environment binary and full journal
are **not committed**; after returning to Golden, inspect them locally,
save only a non-sensitive status and checksum record to `evidence/`,
then retire the unique service/GRUB entry and securely delete the
private staging root. If the environment is still invalid on the
candidate boot, preserve the private bytes for offline diagnosis
before retiring and do not claim the race was fixed.

## Validation

Run before arming:

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004iv-bootenv-ordered-diagnostic \
  -p test_ordered_boot.py -v
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ir-boot-env-preflight-offline \
  -p test_boot_env.py -v
```

Nine E004iv static tests plus eleven earlier read-only GRUB fixture
tests pass on Golden. The new entry passes `grub-script-check`,
and the actual service is verified with `systemd-analyze verify`
only after the private executable is installed. The unarmed
installer, one-shot arming and Golden-return retirement scripts
have explicit no-retry, unique identity and preserved boot
default checks.

**The outcome must be filled from the actual candidate and Golden
return journal, never inferred from passing offline tests.** Regardless
of outcome, E004iv does not test the QC10C DMA guard, rear Bayer
colour calibration, front QC10C decoding, an NV12 ISP mode, front/rear
desktop switching, protected IR illumination or Windows Hello.
