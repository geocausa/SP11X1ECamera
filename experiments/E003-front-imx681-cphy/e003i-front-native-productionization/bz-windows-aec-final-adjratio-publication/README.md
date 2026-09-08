# E003i BZ — Windows AEC final AdjRatio publication

Status: **PASS (static/offline)**.

BZ closes the arithmetic publication immediately after the final target-component aggregators and corrects one earlier label: SceneAnalyzer bank data `7/9/11/13` are **float adjustment-ratio (`AdjRatio`) publications**, not the final integer exposure SI themselves.

For the ordinary/default path, the exact final arithmetic is:

- FrameSA: `3:7 = (3:5 target) / (3:4 luma)`;
- SafeAggSA: `3:9 = 3:8` exactly;
- ShortAggSA: `3:11 = 3:9 / 3:67`, where `3:67` is `ADRCGain`;
- LongAggSA: `3:13 = 3:9 * 3:69`, where `3:69` is `DarkBoostGain`.

`CAnalyzer` then selects the positive phase-2 arithmetic publication as its adjustment ratio, multiplies it by the analyzer's source exposure, and converts the result to the final qword exposure with `FCVTZU`. If no positive phase-2 publication is available, it falls back to the generic target/luma ratio.

## Why the serialized tuning is mechanically readable

Each arithmetic tuning record is exactly `0xd0` bytes:

`12-byte header + 4 × 44-byte operand + 20-byte output`.

The parsed runtime record is exactly `0x108` bytes:

`16-byte aligned header + 4 × 56-byte operand + 24-byte output`.

The size expansion is accounted for by pointer alignment and expansion of compact 32-bit symbol references to runtime pointers. Across all 241 analyzer arithmetic records (964 operands), the first operand field uses only `0/1/2`, exactly matching the DLL's `UtilGetOperand` switch: fixed, DB, trigger.

The AEC context vtable routes the same `0x108` records to `RunOneArithMeticOperator@0x1803c8e10`. Its operation enum and the DLL's own operation-name table establish enum 2 as multiply and enum 3 as divide.

This checkpoint does not yet reproduce `ADRCGain`, `DarkBoostGain`, or every upstream analyzer publication natively. It closes the final arithmetic join so those producers now have exact downstream semantics.

No camera stream, module load, sensor write, MMIO, Windows boot, or reboot is used.
