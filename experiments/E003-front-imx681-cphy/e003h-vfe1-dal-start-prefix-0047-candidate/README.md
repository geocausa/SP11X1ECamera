# E003h 0047 — VFE1 DAL start-prefix one-shot candidate

Distinct Golden-safe package for the static 0047 Windows-parity delta. Relative to the consumed 0046 telemetry package, only `qcom-camss.ko` changes. The new CAMSS module preserves the 0046 timeout telemetry and adds the exact same-machine Windows VFE680 first-start prefix between startup packet 1 and the existing BUS prepare: TOP masks `0x0007f051/0`, BUS masks `0xd0000000/0`, then VFE TOP `+0x24=0`.

The package does not copy any 0046 authorization or runtime evidence. `preflight.sh` is package-only and cannot activate camera hardware. `install-candidate.sh` creates a distinct GRUB entry but never calls `grub-reboot`. Runtime scripts require a separately published `AUTHORIZATION.json`, exact candidate identity, clean HEAD/origin, persistent RT-CDM observer READY/idle, and exactly one helper invocation followed by immediate reboot. Normal QBUF/STREAMON remains outside this harness.

Package installation/inspection is not runtime authorization.
