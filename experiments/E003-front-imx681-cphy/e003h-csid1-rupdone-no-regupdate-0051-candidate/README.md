# E003h 0051 — front IPP RUP_DONE ownership candidate

Distinct Golden-safe package for 0051. Relative to consumed 0050, only `qcom-camss.ko` changes. The exact SP11 front-mode0 IPP RUP_DONE ISR clears Linux software update bookkeeping without issuing the Windows-unmatched follow-up `REG_UPDATE_CMD +0x18` write. No register value is added; RDI/non-front behavior is unchanged.

The helper, IMX681 module, front-only DTB, capsule, media setup and persistent RT-CDM observer are byte-identical to 0050. Installation cannot arm the boot. Runtime requires a separately committed authorization and permits one helper invocation only.
