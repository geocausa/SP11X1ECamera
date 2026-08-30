# E003h 0049 — CSID1 line-error frame read-only candidate

Distinct Golden-safe package for 0049. Relative to consumed 0048, only `qcom-camss.ko` changes. The 0049 module adds three conditional read-only CSID1 format-measure reads (`+0x38c/+0x390/+0x394`) when the existing ISR observes IPP bit14 `ERROR_LINE_COUNT`; no MMIO writes or camera-programming behavior change.

The helper, sensor module, front-only DTB, capsule, media setup, and persistent RT-CDM observer are byte-identical to 0048. Package installation cannot arm the boot. Runtime requires a separately committed authorization and permits one helper invocation only.
