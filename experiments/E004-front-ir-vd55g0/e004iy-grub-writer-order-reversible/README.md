# E004iy — reversible serialization of stock GRUB environment writers

Date: 2026-09-20. Parent: `3eabdd4`. Camera project encompasses
**rear OV13858 AND front IMX681 RGB**; both physical capture paths
have previously produced real frames, but ordinary Linux selectable
video endpoints remain incomplete.

## Observed reason for the change

On E004iw's camera-free candidate and its subsequent ordinary Golden
boot, `grub2-common.service` failed with `cannot read
/boot/grub/grubenv: Invalid argument` while the independent
`grub-initrd-fallback.service` also updated the same environment.
After the two units reached terminal state, a separate read-only
candidate audit successfully read the saved Golden and consumed
one-shot entries. E004ix reproduced two GRUB writer and two
overlapping reader failures on 120 disposable /tmp trials,
versus zero in 120 serialized control trials. The original E004iq
transient invalid bytes were not saved: **a concurrency root
cause is supported but is not conclusively established**.

The E004iy proposal is deliberately limited to a single
**reversible, existing service drop-in** for
`grub2-common.service`:

```ini
[Unit]
Wants=grub-initrd-fallback.service
After=grub-initrd-fallback.service
```

This preserves Ubuntu's shipped service `ExecStartPre`,
`ExecStart`, `ExecStartPost`, existing boot-complete requirement
and GRUB commands, but prevents the two stock service writers from
starting their environment writes concurrently in the ordinary
boot transaction. It does not serialize arbitrary external GRUB
commands, prove rollback after a kernel-level failure, or alter
the persistent Golden boot entry. An uninstalled disposable
systemd service-graph verification and eight fail-closed installer/
rollback static tests passed on SP11.

## Scoped installation and removal contract

`install-unarmed.sh` is source-locked to a clean, pushed camera Git
commit, Golden v4, exact saved Golden and **empty** next-entry,
with no camera node/module/process or preexisting drop-in.
It preserves a root-private snapshot of the original GRUB
environment and the original Ubuntu service checksum under
`/var/lib/sp11-camera-e004iy`, adds only the new dependency
drop-in, reloads systemd, verifies its actual loaded `After`/
`Wants` edge and checks that the GRUB environment bytes were
not changed by installation. It **does not arm a boot, enable
camera hardware or reboot**.

`rollback.sh` requires protected Golden, a valid saved default
and empty one-shot entry, confirms the installed drop-in byte-for-byte
against the exact E004iy source and removes only that drop-in
and its dedicated private archive. It reloads the original
service and checks the dependency disappeared. It does not
overwrite system GRUB environment bytes or repair malformed
blocks. For manual rescue when the repo is not readable, use a
root shell to remove ONLY
`/etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf`,
rmdir its empty parent directory, run `systemctl daemon-reload`,
then inspect `grub-editenv /boot/grub/grubenv list` and the
saved Golden entry before any further reboot.

The new ordering needs validation on a real boot **without
loading either camera**. A live service check or single ordinary
Golden reboot may be carried out only once the actual drop-in
has been verified and the persistent default/rollback plan
are intact. Do not use E004iy as authorization for front QC10C
DMA tests, rear live optical calibration or native IR; those
require separate bounded camera experiments and direct
evidence of healthy boot services.

## Offline tests

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004iy-grub-writer-order-reversible \
  -p test_reversible_order.py -v
```

Any observed deployment/boot result must be recorded separately,
including writer unit exit statuses, ordering and Golden saved
entry; passing these offline checks alone does not demonstrate
a production-safe camera candidate boot.
