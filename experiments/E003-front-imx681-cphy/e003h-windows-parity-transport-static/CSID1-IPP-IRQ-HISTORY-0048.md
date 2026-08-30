# E003h 0048 — CSID1 IPP IRQ history telemetry

## Why this diagnostic is required

Linux VFE680 and CSID680 do not have equivalent observer behavior. VFE680's normal ISR is a no-op, so the private bounded poll for VFE1 `BUS status1 bit21` cannot lose Epoch0 to the normal ISR. The consumed 0047 result that VFE1 Epoch0 was absent therefore remains valid.

CSID680 is different. While powered, its IRQ is enabled. The ISR reads `CSID_IPP_IRQ_STATUS` (`+0xac`) and, whenever non-zero, writes that complete value to `CSID_IPP_IRQ_CLEAR` (`+0xb4`) before returning. Therefore a later timeout snapshot of `IPP_IRQ_STATUS=0x00011e00` is only the live status at that instant. It is not an OR-history and cannot prove CAMIF SOF/EOF, CAMIF Epoch0/1, or RUP_DONE never asserted earlier.

This supersedes only that historical inference in 0042–0047 analysis. It does not alter the raw status values, packet counts, ECC/CRC results, exact masks/configuration, or the 0047 VFE1 Epoch0 absence.

## 0048 delta

Patch `0048-x1e-csid1-ipp-irq-history-readonly.patch` is software-only telemetry:

- add per-CSID `seen_or`, `last`, and `count` fields;
- zero them after the front software-reset completion and before front full configuration/startup/RUP traffic;
- in the existing CSID680 ISR, after the existing IPP status read and before the existing clear, OR-latch that already-read value, save `last`, and increment `count`;
- print those software fields in the existing timeout dump.

There are **zero new MMIO reads/writes**, no changed masks or clears, no RT-CDM/VFE/BUS/CSID configuration/start ordering change, and no CSIPHY/sensor change.

## Static gates

- patch SHA-256: `91d292888e563c2d4e0ffc65664cfa4b0a3225cb1f56af9053652998ff0be1d7`;
- checkpatch: 0 errors, 0 warnings;
- exact patch round-trip: PASS;
- observer-integrity extractor SHA-256: `67ec1a42a05c96648426cbee5625f3607158090de08d582e6c776c3d8a069a32`;
- observer-integrity oracle SHA-256: `23bc970a9bacff901e1336208282904cb9c0add0dfd5bea311194caeacb5451d`;
- 0048 inspector SHA-256: `b1ea1ed6122281c0b67bd3283ad401dc80065a2633f6394fdc4d01c6106b1857`;
- 0048 inspection SHA-256: `6e98360aa0a83c8c61db1e67bd5c12f4fb6c7856698f48aea404a23100de8eb2`;
- built `qcom-camss.ko` SHA-256: `94cc14d9702492bffa2b4e72989db45356cf59ffcce7f4c382be13e7130030b7`;
- exact Golden vermagic.

This static checkpoint does not itself authorize camera hardware. The next bounded run, once separately packaged and authorized, asks one question: **which CSID1 IPP IRQ bits were ever observed by the normal ISR from front reset through the VFE Epoch0 timeout?**
