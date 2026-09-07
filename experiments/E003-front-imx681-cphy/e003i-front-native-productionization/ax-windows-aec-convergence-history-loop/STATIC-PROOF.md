# AX static proof anchors

## Previous request -> convergence

- `0x1803b4700`: convergence requests history offset `1`.
- `0x1803b4708`: call `GetInternalFrameHistory`.
- Previous-history qwords: `+0x28,+0x50,+0x78,+0xa0,+0xc8,+0xf0,+0x118`.
- Current target qwords: convergence input `+0x10,+0x18,+0x20,+0x28,+0x30,+0x38,+0x40`.
- Diagnostic labels the two seven-value sides `TargetInExp(Log)` and `CurrentExp(Log)`.

## Pre-convergence normalization

- `0x180374ef0`: destination/control block pointer `controller+0x16660` is provided to bridge helper.
- `0x180374efc`: call `0x180389dd0`.
- `0x180389de0`: bridge selects `w4=1`.
- `0x180389dec`: bridge calls `RunControlArbitration`.
- `0x180389df0..0x180389ebc`: seven rich output payloads are copied into `child+0x688..+0x868`, 0x50 stride.

## Convergence output

- `CAECXConvergence::PopulateOutput` at `0x1803cdf50` converts internal exposure slots `+0xa0..+0xd0` to seven compact qwords `+0x00..+0x30`.
- `0x180375150`: controller supplies convergence input `controller+0x14ca0`.
- `0x180375154`: controller supplies output `controller+0x14cf8`.
- `0x180375158`: callback slot `+0xb0` is `RunConvProcesss` adapter (AR mapping).

## Post-convergence arbitration

Normal frame sequence:

- `0x1803722d4`: call `CAECXControl::runConvergence`.
- `0x1803723c4`: post-convergence `w4=0`.
- `0x1803723c8`: `x1 = controller+0x14cf8`.
- `0x1803723d0`: call `RunControlArbitration`.
- `0x1803723d8`: copy size `0x3c0`.
- `0x1803723e0`: destination `controller+0x14da8`.

Inside `RunControlArbitration`:

- `0x180388970`: compact convergence pointer retained at child `+0x668`.
- `0x18038a174..180`: selected `x1[lane]` qword -> selected 0x28 record `+0x18`.
- `0x18038a1b4`: reload selected record `+0x18`.
- `0x18038a1bc`: divide exposure by base exposure.
- `0x18038a1d4`: logarithm implementation.
- `0x18038a1e0`: multiply reciprocal-log(1.03) scale.
- `0x18038a1f4`: store result at selected record `+0x10`.

Array geometry:

- selected-record array = child `+0xe0`;
- stride = `0x28`;
- selected exposure qword address = child `+0xf8 + 0x28*lane` = record `+0x18`;
- selected coordinate address = child `+0xf0 + 0x28*lane` = record `+0x10`;
- array end/next field `+0x1f8`; `(0x1f8-0xe0)/0x28 = 7`.

## Core type-5/T681 path

- Core `RunArbitration` entry: `0x1803b89f0`.
- `0x1803b8af4`: save input/output pointers.
- `0x1803b8c60..80`: selected input 0x28 record is copied into rich output; initial rich `+0x20` is selected input record `+0x18`.
- `input+0x4 == 5` dispatches directly to `0x1803ba5a4`.
- `0x1803ba5c0`: call `ApplyCoreTable`.
- `0x1803c3c20`: normal table path reloads selected record `+0x10` coordinate.
- `0x1803c3c24`: reloads selected record `+0x18` exposure.
- `0x1803c41c0`: final gain -> result `+0x00`.
- `0x1803c41c4`: final time -> result `+0x08`.
- `0x1803c41d4`: selected correction factor.
- `0x1803c41e0`: multiply correction by gain*time product.
- `0x1803c41e4`: `FRINTA` helper.
- `0x1803c41f0`: retained exposure -> result `+0x18`.
- `0x1803ba5d0..5d8`: the 32-byte table-result block `+0x00..+0x1f` is copied to rich output `+0x08..+0x27`; therefore result `+0x18` maps exactly to rich output `+0x20`.

## End-of-frame -> next history

- `0x180377308`: runEnd argument `x5 = controller+0x14da8`.
- `0x18037730c`: `x4 = controller+0x14cf8`.
- `0x18037731c`: external callback `+0x48`.
- adapter `0x1803a7ea0`, instruction `0x1803a7ec0`: wrapper vtable `+0xc0` -> core `runEndOfFrame`.
- `runEndOfFrame` rich source block starts: `+0x08,+0x90,+0x118,+0x1a0,+0x228,+0x2b0,+0x338` = `0x08 + 0x88*i`.
- each copies 0x28 bytes; source block third qword is rich record `+0x20`.
- next request reads history payload `0x28 + 0x28*i`, which is history-record `+0x18`.

Closed normal recurrence:

`historyExposure(F-1,i) -> convergence(F,i) -> compactExposure(F,i) -> post-conv arbitration -> T681 -> retainedExposure(F,i) -> history(F,i)`.
