# E003h 0063 — CSID Epoch lifecycle bridge candidate

Fresh Golden-safe bounded one-shot candidate based on the successful 0062r1 assets. DT, IMX681 mode2, C-PHY/CSID programming, VFE programming, BUS clients/UBWC/CGC, RT-CDM payload/order, helper, firmware capsule, and geometry are unchanged from 0062r1.

Only `qcom-camss.ko` changes: the first-frame runner waits up to 500 ms for the CSID1 IPP ISR's existing latched Epoch0 bit21 instead of polling raw VFE BUS status1 bit21. No new MMIO read/write/register value or IRQ programming is introduced.

Candidate is installed and inspected unarmed first. Runtime is exactly one boot and one helper invocation, with no same-boot retry and immediate Golden reboot after archival.
