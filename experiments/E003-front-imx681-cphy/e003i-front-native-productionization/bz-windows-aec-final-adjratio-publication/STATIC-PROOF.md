# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

Pinned tuning SHA256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Runtime arithmetic identity

- AEC context constructor stores vtable `0x1813383b8` at `0x1803a9424..0x1803a9430`.
- Vtable slot `+0x58` is `0x1803c8e10`, `RunOneArithMeticOperator`.
- `CAnalyzer` helper `0x1803f0cd8` reads arithmetic count/pointer from parsed tuning `+0xb0/+0xb8`, advances by `0x108`, checks record `+0` enabled and `+4` phase, and calls context virtual slot `+0x58` with the record pointer.
- The executor reads enum byte `+0x8`; its four operands begin `+0x10/+0x48/+0x80/+0xb8` and its output descriptor is `+0xf0/+0xf4/+0xf8/+0x100`.
- `UtilGetOperand@0x1803c9f18` switches the operand's first u32: 0 returns fixed float `+4`, 1 reads DB descriptor `+8`, 2 uses the trigger path.

## Operation enum

The context stores the DLL operation-name table `0x18169dac0` at context `+0x118`. Entries 0..15 are:

`ADD, SUB, MUL, DIV, MAX, MIN, Smallest, SecondSmallest, Largest, SecondLargest, FlashHighLuma, LinearInterpolation, CondLarger, CondSmaller, CondEqual, Sqrt`.

The switch bodies independently show enum 0 `fmul/fmul/fadd`, enum 1 `fmul/fmul/fsub`, enum 2 `fmul/fmul/fmul`, and enum 3 `fmul/fmul/fdiv` with the Windows epsilon guard.

## Serialized structure correction

A compact arithmetic operator is 52 u32 = `0xd0` bytes. The correct boundary is:

- words 0..2: header;
- four 11-word operands;
- words 47..51: five-word output descriptor `(bank, dataID, mode, descriptionLength, descriptionRef)`.

The earlier BV description treated the last word of operand D as an output-enable field. That boundary label was off by one, although BV's bank/data indices and resulting topology remain correct.

## Exact final formulas

FrameSA anchors the operand interpretation: enum DIV, fixed 1, DB `3:5`, fixed 1, DB `3:4`, output `3:7` (`AdjRatio`). Therefore `3:7=(3:5)/(3:4)`.

The final aggregate records are then direct:

- SafeAggSA phase-2 enum MUL: DB `3:8`, then three fixed `1.0` operands; output `3:9`. Therefore `3:9=3:8` exactly.
- ShortAggSA phase-2 enum DIV: DB `3:9`, fixed `1.0`, DB `3:67` (`ADRCGain`, fallback 1), fixed `1.0`; output `3:11`. Therefore `3:11=3:9/3:67`.
- LongAggSA phase-2 enum MUL: DB `3:9`, fixed `1.0`, DB `3:69` (`DarkBoostGain`, fallback 1), fixed `1.0`; output `3:13`. Therefore `3:13=3:9*3:69`.

BY already proves arithmetic SceneAnalyzer scalar publication duplicates the float to both slot lanes, so selector 1 does not create a low/high ambiguity on this path.

## AdjRatio versus qword exposure SI

`CAnalyzer` scans its `0x108` arithmetic records for an enabled phase-2 operator, reads that operator's published bank/data float, and if it is positive uses it directly as `AdjRatio`. The fallback path computes target/luma. It then multiplies the chosen ratio by source exposure and executes `FCVTZU` to form the qword exposure result.

Thus bank data `3:7/9/11/13` are adjustment ratios. The final exposure SI/qword is downstream of them.
