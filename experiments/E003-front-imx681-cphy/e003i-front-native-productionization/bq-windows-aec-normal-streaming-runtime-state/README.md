# E003i BQ — Windows AEC normal-streaming runtime state

Status: **PASS (static/offline)** — closes the ordinary **normal-streaming, AEC-unlocked** values of the four runtime controls left public by BP, and corrects the old provisional interpretation of convergence `+0x2b4`.

## Normal operation mode excludes context bit 3

The final context-manager interface vtable used by convergence is `0x1813383b8`. Its slot `+0x18` is the pure bit-test helper at `0x1803ae9b0`:

`IsContextActive(n) = ((1ULL << n) & contextMask[+0xb8]) != 0`.

BasicSafe calls that slot with `n=3` at `0x1803ceaf0..0x1803ceb18`.

`CAECXContextManager::UpdateContext` handles operation-mode updates at `0x1803c868c`. Its six-way jump table maps operation modes `0..5` to context bits `1..5` plus the mode-5 flash branch. In particular:

- opMode `1` -> context bit `2` (`0x4`);
- opMode `2` -> context bit `3` (`0x8`).

The pinned DLL's `CAECXControl::SetControlOpMode` switch independently identifies enum value **1** as Streaming: case 1 emits either `Streaming to Streaming` or `entering streaming op mode`.

The archived same-tree CamX source independently shows `CAECEngine::StartStreaming` maps `StatsOperationModeNormal` to `AECAlgoOperationModeStreaming` and sends it with `AECAlgoSetParamOperationMode`.

Therefore ordinary normal streaming has context bit 2, not bit 3, and the BasicSafe context-3 exemption is **false**.

## `+0x2ac/+0x2b0/+0x2b4` are lock bookkeeping, not three independent flags

The convergence constructor at `0x1803cd570` initializes:

- `+0x2ac = 0`;
- the full 64-bit qword at `+0x2b0 = 0` (therefore both `+0x2b0` and `+0x2b4` words are zero).

A whole-AEC-code store census finds all writes to those offsets:

- nonzero `+0x2ac` writes: only inside the routine carrying the source/function identity `CAECXMetering::UpdateMeteringLockExposure`;
- nonzero `+0x2b0` writes: only the same routine, using **64-bit** stores of its current marker;
- independent stores to `+0x2b4`: **none**;
- the only other stores are constructor/reset zeroes at `0x1803bad84..0x1803bad88` and `0x1803cd5f4..0x1803cd5f8`.

The lock routine itself contains `Metering locked, overwrite metering output.` and maintains status `+0x2ac` as 0/1/2 while writing the marker qword at `+0x2b0` (`0x1803b3150..0x1803b31d4`).

This supersedes the earlier provisional AY name **`intolerance_gate`** for `+0x2b4`: there is no standalone runtime flag stored there. It is the upper word of the lock marker qword. BB's `state_flag_long` likewise reads the low word of this lock marker when type 1 is requested; it is not an independent persistent Long-state control.

## Explicit unlocked normal-preview projection

The metering-lock bookkeeping routine uses the same final context interface as BasicSafe, but tests **context index 38 (`0x26`)**. At `0x1803b302c` it loads `w1=0x26`, points `x0` at the core `+8` interface, and later calls vtable slot `+0x18`. The control path explicitly sets context 38 with `(index=38,value=1)` at `0x1803777d8..0x1803777f8` and clears it with `(index=38,value=0)` at `0x180378274..0x180378294`. BQ therefore treats this as a separate temporary metering-lock context and does not collapse locked/snapshot/preflash behavior.

The archived CamX `SetLockToSetParamList` independently maps any HAL state other than `ControlAELockOn` to `AECAlgoLockOFF`.

For the explicitly scoped **AEC-unlocked normal-streaming, metering-lock-context-inactive** path, the bookkeeping branch is excluded. With constructor/reset state and no lock bookkeeping activation:

- `state0/+0x2ac = 0`;
- lock marker qword `+0x2b0 = 0`;
- therefore GetExposureInfo type-1 word `+0x2b0 = 0`;
- BasicSafe word `+0x2b4 = 0`;
- context query(3) = 0 because Streaming is opMode 1 / context bit 2.

Thus all four BP runtime scalar controls evaluate to zero on the ordinary unlocked normal-streaming path. AEC-lock requests remain a separate dynamic mode and are **not** collapsed by BQ.

## Safety / scope

Static and read-only only. No Windows boot, mount, camera stream, module load, sensor write, MMIO, or reboot. This checkpoint does not claim locked/preflash/FastAEC behavior is fixed to zero.
