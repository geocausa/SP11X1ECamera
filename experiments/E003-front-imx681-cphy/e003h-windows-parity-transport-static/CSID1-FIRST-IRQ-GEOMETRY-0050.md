# E003h 0050 — bounded ordered first-IPP IRQ geometry telemetry

## Question

At which exact Linux CSID1 IPP interrupt does measured geometry diverge from the Windows first-IRQ sequence? In particular: does Linux observe RUP_DONE while `FORMAT_MEASURE0` is still 3840x2640, and is the first Epoch-bearing IRQ already at the wrong 2640-line geometry?

## Delta

0050 is a software-only diagnostic on top of exact 0049. For the first eight nonzero front-mode0 IPP IRQs it stores, in order:

- the already-read IPP IRQ status word;
- one read-only `FORMAT_MEASURE0` (`+0x38c`) value taken before the existing IPP clear.

The trace count is reset at the existing front reset/history boundary. Runtime dump prints `ipp-seq[N]=STATUS/ACTUAL` for the retained entries. The existing 0048 OR/last/count and 0049 bit14 frame/HBI/VBI telemetry remain unchanged.

## Safety boundary

- New MMIO reads: exactly **1** callsite (`+0x38c`), bounded to at most eight reads per reset epoch.
- New MMIO writes: **0**.
- No IRQ mask/clear changes.
- No CFG0/CFG1/crop/RUP/AUP changes.
- No CSIPHY, VFE, RT-CDM, sensor, regulator, clock or DT changes.
- No candidate boot or camera hardware execution is authorized by this static checkpoint.

The Windows first-IPP raw KD file is still locally missing and its repository oracle intentionally fails closed; 0050 does not convert the handed-off trace into fabricated raw evidence. Its purpose is only to expose the corresponding Linux sequence with read-only telemetry.
