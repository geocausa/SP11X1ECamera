# E004ix — GRUB environment writer overlap, disposable reproduction

Date: 2026-09-20. Parent: `ac3d1f0`. Both rear OV13858 and front IMX681
ordinary Linux camera integration remain the goal. This stage addresses
a separate **boot safety** issue before another camera candidate boot.

## On-machine evidence, carefully bounded

The previous E004iq front QC10C candidate failed while reading
`/boot/grub/grubenv` at almost the same time that two stock systemd
services were writing the same block. E004iv showed that waiting for
the two stock writer services to reach terminal state avoids overlap
with a later reader, but its script aborted early on Git ownership.
E004iw fixed the owner-scoped Git read and on the real candidate boot
successfully read a private 1024-byte GRUB snapshot with
`saved_entry=sp11-audio-fullio-v19c` and explicitly empty
`next_entry=`. However, **grub2-common.service itself failed**
earlier in that candidate boot with `cannot read /boot/grub/grubenv:
Invalid argument`; `grub-initrd-fallback.service` finished
successfully. The same grub2-common failure also occurred on the
next **ordinary Golden boot**, while the final environment was
readable afterward. E004iw then returned to Golden and all candidate
boot assets were removed. The original E004iq transient block was
not preserved, so these observations do NOT prove its exact cause.

## Actual safe experiment

`grubenv_race_fixture.py` creates and resets a separate, uniquely
named, user-owned **/tmp fixture**, with synthetic values for the
known Golden saved entry, empty next entry and three stock markers
(`recordfail`, `initrdfail`, `prev_entry`). The concurrent
trial runs the stock `grub-editenv unset recordfail` and
`unset initrdfail` concurrently, with a simultaneous `list`,
then does `unset prev_entry`; the serial control runs the
same three commands strictly in sequence before reading. Both
use the exact **private fixture path** for every write/read.
All fixtures and test output are removed automatically.

On SP11, 120 bounded paired trials gave **2 concurrent writer
failures and 2 overlapping reader failures**, versus **zero
writer failures, zero reader failures and zero state errors**
in 120 serialized controls. The concurrent fixture's final
environment remained readable and retained the synthetic
saved/next values; this is consistent with the later recovery
of the real candidate environment. An initial five-trial
exploratory check independently saw one overlapping reader
failure.

The live Golden grubenv SHA-256 was independently compared
immediately before and after the 120-trial run and was
**unchanged**. Its actual saved-entry/next-entry read and
the Golden overlap guard passed. No root privileges, system
service edits, boot, camera, module, PMIC or IR were used
during this fixture test. Eight positive/negative fixture
and temporary systemd-proposal tests pass.

The file
`PROPOSED-NOT-INSTALLED-grub2-common-after-initrd-fallback.conf`
contains only a **staged** GRUB service dependency proposal:
make `grub2-common.service` want and run *after*
`grub-initrd-fallback.service`. `systemd-analyze verify`
passed on copies of the two Ubuntu service units and the
proposed drop-in under **/tmp**. The real installed
`grub2-common.service` was separately checked and still
does **not** have that dependency; this experiment never
installed the proposal.

## What this does and does not establish

This proves that SP11's installed GRUB tool can produce
transient reader/writer errors on a single **disposable
environment file** when its independent writer processes
overlap, and that the tested serial controls do not show
those errors. Together with the candidate/Golden journals,
this supports a shared-file concurrency hypothesis, not
a complete proof that it was the *only* cause of E004iq's
particular failure.

A systemd verification of an uninstalled drop-in does not
establish real-boot correctness, eliminate other GRUB
writers, ensure firmware one-shot semantics, or justify
modifying the protected Golden boot service as part of
this offline experiment. Before any deployment, inspect
ordering cycles, boot recording/fallback semantics,
backup/rollback and a separately authorized test
that can return to the protected Golden boot. The current
camera candidates remain **unarmed**. The front QC10C
mapped-DMA guard is still untested on real V4L2 buffers,
and neither a calibrated rear live desktop endpoint nor
a real front NV12/QC10C decoder is available.

## Reproduce without changing the system GRUB block

```sh
python3 experiments/E004-front-ir-vd55g0/e004ix-grub-writer-race-offline/grubenv_race_fixture.py --trials 120
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ix-grub-writer-race-offline \
  -p test_grubenv_fixture.py -v
```

The concurrent error count is scheduling-dependent. A run with
zero concurrent errors does not disprove a race; the serialized
control must always preserve its saved and next entries.
