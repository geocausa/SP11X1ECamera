# BE — Windows AEC metering antibanding is a no-op for pinned IMX681 tuning

This checkpoint closes the **pinned IMX681 path through the metering antibanding postprocess**. It does **not** claim that Qualcomm's enabled antibanding algorithms are globally no-ops.

## Result

The exact Windows `aecxmetering` module used by `CAECXMetering` is loaded into core `+0xff0`. The pinned Surface IMX681 blob contains **ten** `aecxmetering` mode variants; BE checks every one. Across all ten:

- ADRC-priority antibanding top-level enable = **0**;
- luma-priority antibanding top-level enable = **0**;
- the luma auxiliary dynamic-adjustment enable is also **0**;
- the corresponding static thresholds are present (`0.65`, `0.94`, `0.85`) but are not authorized to mutate the target tuple while their gates are zero.

Therefore the `(Short, Long, Safe)` target exposures entering this metering antibanding stage leave it unchanged for the pinned IMX681 tuning **independently of which of its ten metering mode variants the selector chooses**.

## Exact native join

`CAECXContextManager` performs the tuning lookup for the literal `aecxmetering`, adds `0x120` to the returned module object and stores that pointer at core `+0xff0`. Core vtable slot `+0x68` returns `core+0xef8`; the metering functions then load `[returned+0xf8]`, which is the same core `+0xff0` pointer.

Each compact Parameter Bin `aecxmetering` root is `0xf8` bytes. The ten entry IDs are `159, 330, 354, 380, 422, 450, 481, 524, 548, 574`. Their adjacent antibanding structures widen under the ARM64 ABI exactly onto the native offsets used by Windows:

- compact ADRC block `0x84..0xb7` (`0x34` bytes) -> native `+0xc0..+0xff` (`0x40` bytes);
- compact luma block `0xb8..0xef` (`0x38` bytes) -> native `+0x100..+0x147` (`0x48` bytes);
- the next compact tail field at `0xf0` lands at native `+0x148`, matching the Windows tail read.

The widening comes from the nested interpolation vector becoming a native count/pointer container plus normal 8-byte alignment. This is the same Parameter Parser compact-reference/native-pointer distinction already established in BD.

## Pinned values

- ADRC: compact `+0x84 = 0`; compact `+0x88 = 0.65` -> native gate `+0xc0`, threshold `+0xc4`.
- Luma: compact `+0xb8 = 0`; compact `+0xbc = 0.94`; compact `+0xc0 = 0.85` -> native gate `+0x100`, clamp `+0x104`, exit `+0x108`.
- Both nested interpolation trees resolve to the same `190 / 230 / 180` three-float core payload.

Read-only sibling Surface tuning inspection provided an independent schema cross-check: MSHW-specific rear/front variants flip compact ADRC fields `+0x84/+0x8c/+0x90` from `0` to `1` and change the adjacent factor from `0.65` to `0.45`, consistent with the native enable/adjust-enable branch shape. Those sibling binaries are not copied into this checkpoint.

## Scope

BE proves only the disabled path selected by the exact pinned IMX681 tuning. The enabled luma/ADRC interpolation equations remain available for a later clean-room stage if another sensor/tuning requires them.

No camera modules were loaded and no live camera operation was performed.
