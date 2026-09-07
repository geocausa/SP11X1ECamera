# BE static proof

## 1. Exact tuning pointer

- literal `aecxmetering`: VA `0x181375e68`;
- lookup call: `0x1803ca9ac` -> `0x1806f39f8`;
- module data pointer: `lookup_result + 0x120`;
- stored at AEC core `+0xff0`: `0x1803ca9c0`.

Core vtable slot `+0x68` points to `0x1803aebb0`, which returns `core+0xef8`. `CAECXMetering::CalculateAntibandingPriority` and `CalculateAntibandingADRCPriority` then load tuning at returned `+0xf8`, i.e. core `+0xff0`.

## 2. Compact root

Pinned IMX681 contains ten Parameter Bin `aecxmetering` entries, each size `0xf8`: `159,330,354,380,422,450,481,524,548,574`. BE verifies the critical gate/threshold layout in all ten, eliminating mode-selector dependence.

ADRC serialized block begins at `0x84`:

- enable `0`;
- factor bits `0x3f266666` = `0.65`;
- nested adjustment flags `0/0`;
- three `(9,8)` trigger descriptors;
- one interpolation child.

Luma serialized block begins at `0xb8`:

- enable `0`;
- clamp bits `0x3f70a3d7` = `0.94`;
- exit bits `0x3f59999a` = `0.85`;
- nested adjustment flags `0/0`;
- three `(9,8)` trigger descriptors;
- one interpolation child.

Both child chains terminate in the float triple `190,230,180`.

## 3. ABI widening

The nested adjustment payload is compact `0x2c` bytes. In native ARM64 layout it is `0x38` bytes because the interpolation `(count, 32-bit symbol ref)` becomes an aligned native count/pointer container.

Therefore:

- ADRC: compact `0x34` -> native `0x40`; `0x84` -> native `+0xc0`, next block lands exactly at `+0x100`.
- Luma: compact `0x38` -> native `0x48`; `0xb8` -> native `+0x100`, next tail lands exactly at `+0x148`.

Windows itself accesses the next tail at `+0x148`, closing the block boundary independently.

## 4. Disabled luma mutation

`CalculateAntibandingPriority` reads:

- enable `+0x100`;
- clamp/exit `+0x104/+0x108`.

At `0x1803e56e4..0x1803e56f4`, enable must equal 1 or execution branches to `0x1803e59a4`, bypassing the target writes in the enabled region. The pinned enable is 0.

Its nested dynamic-adjustment gate at `+0x110` is also zero in the pinned root.

## 5. Disabled ADRC mutation

`CalculateAntibandingADRCPriority` reads:

- enable `+0xc0`;
- `exitThresholdAsFactorOfMinExposure` at `+0xc4`.

At `0x1803e5c30..0x1803e5c40`, enable must equal 1 or execution branches to the return path `0x1803e5ea8`, before the enabled target store at `0x1803e5de8`. The pinned enable is 0.

## Closure

For every `aecxmetering` mode variant in the pinned IMX681 tuning, the metering antibanding stage is an identity mapping on its target exposure tuple. Enabled-branch interpolation semantics are intentionally outside BE.
