# E004iv — one-shot, camera-free GRUB-environment diagnostic

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
