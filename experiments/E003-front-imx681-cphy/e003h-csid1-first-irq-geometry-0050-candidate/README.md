# E003h 0050 — ordered first-IPP geometry read-only candidate

Distinct Golden-safe package for 0050. Relative to consumed 0049, only `qcom-camss.ko` changes. The 0050 module keeps an eight-entry software-only ordered history of the first nonzero front-mode0 IPP IRQ statuses and one read-only `FORMAT_MEASURE0 +0x38c` sample per retained IRQ before the existing clear. It adds zero MMIO writes and changes no camera programming.

The helper, IMX681 module, front-only DTB, oracle capsule, media setup, and persistent RT-CDM observer are byte-identical to 0049. Installation cannot arm the boot. Runtime requires a separately committed authorization and permits one helper invocation only.
