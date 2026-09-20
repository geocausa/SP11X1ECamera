# E004ir — read-only GRUB preflight after consumed E004iq abort

Date: 2026-09-20. Parent: `406fc4d`. This experiment is **offline-only**;
no candidate kernel was booted, no camera module was loaded, and no service
was installed or enabled.

## Facts from the consumed E004iq boot

The E004iq one-shot entered its candidate kernel and reached its dedicated
service at 16:16:55 BST. Its first read of `/boot/grub/grubenv` using
`grub-editenv ... list` failed with `invalid environment block`. No
camera-attempt marker, camera module load or 27-frame launcher followed.
The service-exit reboot returned SP11 to Golden, whose GRUB environment
then reported `saved_entry=sp11-audio-fullio-v19c` and `next_entry=`.
The E004iq identity and all candidate boot/package/service assets were
retired. The original candidate GRUB environment bytes were not preserved,
so a later valid Golden block **cannot establish why the earlier block
was unreadable**.

Inspection of the retained candidate journal also showed the
`grub2-common.service` and `grub-initrd-fallback.service` starting
in the same second as the camera service. Both GRUB services invoke
`grub-editenv ... unset` to update that environment block. Their
relative order within the second and exact file operations were not
recorded. Startup overlap is a **plausible concurrency hazard**, not a
proven root cause. Ext4 had already been remounted read-write before
the failed read; the visible journal does not show a block I/O or ext4
failure at that moment.

## Offline-only artefacts

`boot_env_preflight.py` reads a designated GRUB environment with exactly
one `grub-editenv PATH list` command. It requires a parseable block,
the exact persistent Golden entry and an explicitly present empty
`next_entry`; when invoked in candidate mode it also verifies a unique
candidate-specific kernel command-line marker and boot ID. Any missing
or invalid item rejects access; a damaged block is **never** silently
interpreted as an empty `next_entry`. It does not repair any GRUB
block or authorize camera hardware.

`sp11-camera-e004ir-grubenv-diagnostic.service` is a **proposal only**
for a distinct future *diagnostic* boot. It is conditioned on its own
command-line marker and explicitly orders itself after the two known
GRUB environment writers, with dependencies on both. It contains no
installation section, reboot callback, camera driver command or boot
entry. It is not the replacement live QC10C runner, and has never run
during a candidate boot.

`test_boot_env.py` uses newly created GRUB environment **fixtures
under a disposable temporary directory**, never the machine's live
`/boot/grub/grubenv`. It checks valid, corrupted, truncated, wrong
default, nonempty/missing next-entry, missing/mismatched/duplicate
candidate-marker cases. A separate test reads the live Golden
environment before and after a read-only audit and verifies identical
bytes. All **11 tests pass** on SP11; `systemd-analyze verify` accepts
the uninstalled diagnostic unit.

Run on Golden without any test-boot installation:

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ir-boot-env-preflight-offline \
  -p 'test_boot_env.py' -v
systemd-analyze verify \
  experiments/E004-front-ir-vd55g0/e004ir-boot-env-preflight-offline/sp11-camera-e004ir-grubenv-diagnostic.service
```

## Boundary for the next physical experiment

E004ir does **not** prove that the concurrent GRUB writers caused
E004iq's invalid block, that their completion guarantees a valid block,
or that it would be safe to omit the original GRUB check. Before
another uniquely identified physical test, review the boot contract
and preserve a fail-closed early environment check, one-shot identity,
protected persistent Golden default and unconditional bounded
return path. Never rearm E004iq. The E004ip QC10C mapped-DMA safety
guard remains untested on actual mapped buffers; linear NV12 ISP
and safe UBWC reset remain independently unproven.
