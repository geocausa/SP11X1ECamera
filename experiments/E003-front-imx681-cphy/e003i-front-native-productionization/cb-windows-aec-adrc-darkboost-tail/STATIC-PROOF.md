# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

Pinned tuning SHA256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

> Note: the DLL hash above is checked mechanically by the verifier; the canonical full value is emitted in `VERIFY-RESULT.txt`.

## Trigger IDs and bank read

`0x1803ae3b0` contains the Windows trigger-control name switch. Its signed-byte jump table at `0x1803ae5f8` is indexed by `controlID-1`. Enum ID 8 dispatches to `TriggerCtrlLux`; enum ID 14 dispatches to `TriggerCtrlGyro`. BG independently ties trigger-bank `(9,8)` to the controller LuxIndex path. CB does not need to assume a writer-level identity for bank `(9,14)`: the selected method-2 program has a single outer region, so its result is invariant to that outer coordinate.

`CAECXBankManager::GetDataTriggers@0x1803ae610` bounds the data ID, indexes `dataID*16`, and returns slot `+8`. Trigger-bank reads therefore consume the published scalar directly.

## Method-2 operand semantics

`UtilGetOperand` method 2 at `0x1803ca020` reads the two runtime descriptors at operand `+0x10/+0x18` through the generic bank getter and passes the resulting scalars as `s0/s1` to `0x1803acf40`. That helper stores current `s0/s1` at interpolation state `+0x58/+0x5c`; recursion level 0 consumes the first coordinate, and level 1 reloads the second from `+(level+0x16)*4`. Thus the first descriptor is mechanically the outer trigger and the second the inner trigger.

The recursive interval helper at `0x1803ad048` clamps within configured regions and interpolates only across gaps. At `0x1803ad39c..0x1803ad3b0` it computes the gap fraction and `1-fraction`. The concrete TwoFloats interpolator at `0x1803adac0` proves blend order `low*(1-t) + high*t` using separate float32 multiply/add instructions.

This instruction order matters. CB contains two explicit 1-ULP traps and therefore forbids algebraic simplification of apparently identity/equal-endpoint ramps.

## Default ADRC cap

CA already proves ADRCCapSA selects operand C because FaceSA confidence remains exact zero in uninterrupted DefaultSequence. C is method 2 with primary descriptor `9:14` and secondary trigger `9:8` (proven Lux). Its outer table has one `0..1000` region; therefore the output is independent of the primary coordinate and its exact bank-slot semantic is unnecessary for this scope. Its inner table is the Lux `1.6/1.5/1.4` program recorded in README.

## Short tail

ShortAggSA:

1. `AdjRatioShort`, enum DIV: `3:66 = 3:9 / 3:10`.
2. `ADRCGain`, enum MIN: A is method-2 `(Lux,3:66)` with outer Lux `0..1000` and inner `0..1 -> 1`, `1000 -> 1000`; C is DB `9:54 ADRCLuxFaceCap`. Therefore `3:67 = MIN(A,C)` with Windows method-2 arithmetic preserved.
3. BZ: final `3:11 = 3:9 / 3:67`.

Trap: `A(123.5f)=0x42f70001`, while direct `123.5f=0x42f70000`.

## Long tail and dominated branch

LongAggSA:

1. `DRCGainRemainder`, enum DIV: `3:157 = 8.0 / 3:67`.
2. `AdjRatioLong`, enum DIV: `3:68 = 3:12 / 3:9`.
3. `DarkBoostGain`, enum MIN:
   - A = method-2 `(Lux,3:68)`, with Lux outer regions `0..260`, `300..320`, `360..1000`; the first two child tables map ratio `0..1 -> 1`, `2..1000 -> 2`, while the final child is constant `1`.
   - C = method-2 `(Lux,3:157)`, outer Lux `0..1000`; child maps `0..1 ->1`, `64 ->64`.

Enum 5 executor body `0x1803c9448..0x1803c9460` proves `MIN(A*B,C*D)`.

The default ADRC cap is at most `1.6`, so `3:67 <=1.6` and the minimum possible positive remainder is float32 `8/1.6 = 5.0`. A is bounded by `2.0`; C is therefore always above A and cannot win the MIN. Thus the default Long dark-boost result is exactly method-2 A, with its Windows interpolation order retained.

Equal-endpoint trap: for Lux `260.9975f` and ratio `1.1f`, the outer interpolation produces `0x3f8ccccc`, while the child value is `0x3f8ccccd`.
