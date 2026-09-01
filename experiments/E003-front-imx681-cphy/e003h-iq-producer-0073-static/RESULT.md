# E003h 0073 static — IMX681 Chromatix / IQ producer boundary

Status: **accepted static/offline checkpoint**. No camera runtime, request6 submission, MMIO, sensor transmission, or new kernel module was performed.

## What is now decoded

The exact Surface IMX681 tuning blob is QTI Chromatix Parameter Parser V3.4.0. Its container is decoded as three contiguous sections. Section 0 is a fixed 56-byte `ParameterFileSymbolTableEntry` table; section 1 is serialized object data; section 2 is a 20-byte selector/mode index with 55 groups × 17 tuned-module slots.

A module symbol entry contains its SymbolTableID, 32-byte type name, version, ModeId/mode-symbol selection, section-1-relative data offset, and serialized byte length. The serialized module objects then contain SymbolTableIDs for child entries, matching the `ReadPointerEntry()` architecture used by Qualcomm's generated Parameter Parser.

## Front Sensor2 result

The already-proven IMX681 hardware mode maps to tuning selector **Sensor2**. Sensor2 exposes Preview, Snapshot and Video branches, but for the nine IFE modules needed by the proven Linux request materializer there are **no Sensor2/usecase overrides**. All three usecases inherit the same default objects:

- BPC/ABF41
- Demux/BLS14
- DSX10 video full/DC4
- Gamma15
- GIC31
- GTM13
- LSC41
- PDPC31
- WB20

Therefore the still-unresolved global Windows usecase does **not** block decoding these nine IFE modules.

## Pointer-tree proof

The decoder follows real SymbolTableID references from the default root objects into their control and trigger trees. Exact root chains are asserted for BPC/ABF41 (`0x44d/0x44e/0x44f`), GTM13 (`0x497/0x498/0x499`) and LSC41 (`0x4b0/0x4b1/0x4b2`). Region payloads are summarized and hashed rather than recursively interpreted as pointers, avoiding false references from numeric LUT data.

## Safety / next gate

Request6 is neither generated nor authorized. The next gate is offline only: label the effective trigger dimensions using public CamX interpolation structure, recover the per-frame trigger inputs from the same-machine Windows producer, and generate a candidate request6 IQ packet offline. Runtime remains forbidden until that offline result matches Windows request6 register/DMI oracle data.
