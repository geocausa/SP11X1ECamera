# E003h 0073 — private LSC tuning-tree parser / mutation boundary

## Classification

**CLOSED NORMAL-PATH PARSER/MUTATION BOUNDARY.**

This checkpoint does **not** claim that the exact September 2 verified-front `DataManager+0x38/+0x30` source buffer has been recovered. It closes the ordinary mechanisms by which a correct front IMX681 source could silently become the already-proven rear/default LSC41+golden tree after entering the private DataManager.

The remaining provenance oracle is therefore narrower: recover/capture the exact September verified-front private DataManager source bytes and, only if necessary, the capture-time live-tuning override state.

## Historical Aug-4 transport is front-correct

The exact ARM64 active dump `NetAdapterCx-20260804-1913.dmp` is revalidated at SHA-256 `2ca55e2a...db40`.

A single KMD cache page contains separate rear and front cache tuples:

- rear packed sensor ID: `0xd855`
  - sensor-module VA `0xffff94825fd02000`, size `0x24326`
  - tuning VA `0xffff948260010000`, size `0x279abe`
- front packed sensor ID: `0x0aff`
  - sensor-module VA `0xffff94825fd4c000`, size `0x33d30`
  - tuning VA `0xffff948260290000`, size `0x62a5ef`

The proof walks the active-dump page tables and hashes the **complete mapped buffers**, not just their first pages:

- front module → exact `com.surface.sensormodule.ffc_imx681.bin`, SHA `f7dd81be...a45c`
- front tuning → exact `com.surface.tuned.ffc_imx681.bin`, SHA `2c1c7fd9...75f1d`
- rear module → exact `com.surface.sensormodule.rfc_ov13858.bin`, SHA `f8f60e79...6b14`
- rear tuning → exact `com.surface.tuned.rfc_ov13858.bin`, SHA `4858ccb2...f635`

A separate serialized `SensorTuningData` record in the same dump has:

- record header at dump-file page offset `0x63591fc`
- total record bytes `0x62a61b`
- payload-header bytes `0x2c`
- payload bytes `0x62a5ef`, exactly the front tuning size
- payload begins with the exact front Chromatix bytes and contains `com.surface.tuned.ffc_imx681`

So the historical front KMD cache and the serialized front tuning transport are not rear-swapped.

## Normal DeviceMFT tree construction is private

`DataManager::Construct` creates a fresh tuning manager and copies the private DataManager source into that manager before calling `CreateTunedModeTree`:

`DataManager+0x38/+0x30 -> manager source +0x8/+0x10 -> CreateTunedModeTree`

`CreateTunedModeTree` allocates and zeroes a fresh `0x1640` parser/tree object. The generic parser then allocates/stores instance state at:

- parser `+0x430` — node-array/storage
- parser `+0x428` — root

The exact ARM64 signatures are pinned in `prove-lsc-private-tuning-tree-provenance.py`.

This excludes a normal process-global parser/root reuse explanation.

## Post-construction tree mutation has one external path

The generic tree graft helper is RVA `0x6f3780`.

A decoded scan of every executable PE section finds exactly two BL callsites:

1. `0x6f39c0` — recursion inside the graft helper itself;
2. `0x716134` — `DataManager::LoadTuningBin`.

There is no second external caller that can silently graft another tuning tree into this private manager.

The generic parser itself has four direct callers in this binary:

- `0x6f534c` — normal tuned-mode tree construction;
- `0x716110` — temporary tree used by live-tuning reload;
- `0x721a8c` — SensorModuleDataManager domain;
- `0xe0df3c` — FD tuning domain.

Only the `LoadTuningBin` path reaches the private-tree graft helper.

## Live-tuning gate

`CaptureDevice::IsTuningBinChanged` checks CamX static-settings bit 29. Only when it is enabled does it continue, and then only for nonzero request numbers divisible by ten. It calls:

`DataManager vtable +0x20 -> CheckForTuningBinUpdate`

and on success:

`DataManager vtable +0x28 -> LoadTuningBin`

The reload path is rooted at:

`C:\Data\test\Livetuning\`

The EnableLiveTuning source is also now mechanically connected end-to-end:

`AVS CCaptureFilter+0x6d8`
→ `DeviceConfigInfo+0xc0` inside the `+0x618` payload
→ `DeviceMFT DataManager+0xe8+0xc0`
→ copied CaptureDevice settings block
→ `CaptureDevice+0x464`
→ `SetStaticSettings[0x15]`
→ CamX bit 29.

AVS reads `enableLiveTuning` from:

`HKLM\SYSTEM\CurrentControlSet\Control\Qualcomm\Camera`

and explicitly writes zero to `CCaptureFilter+0x6d8` when that registry value/key is absent.

On the currently recovered Windows filesystem, `C:\Data\test\Livetuning` and the ordinary CamX override file are absent. This is a current-state observation only; it is **not** promoted into proof of the September 2 capture-time registry value.

## What this rules out

The following normal-path explanations are closed:

- a process-global TuningDataManager/parser/root shared between front and rear;
- `CreateTunedModeTree` silently reusing an old rear parser/root while its private source is front;
- an unaccounted second normal tree-graft caller after construction;
- the historical front KMD cache itself containing rear OV13858 module/tuning bytes;
- the historical serialized front `SensorTuningData` record carrying rear tuning by size/identity.

## Remaining provenance gate

The only decisive source identity still missing is the **September verified-front** private:

`DataManager+0x38 pointer / +0x30 size`.

If those bytes are rear OV13858, the investigation moves upstream to the live InitParams/source-buffer handoff.

If those bytes are front IMX681 **and** live tuning was disabled, ordinary parser/cache/graft explanations are exhausted. At that point the remaining hypothesis class is an abnormal memory overwrite/corruption or another write that must be demonstrated directly rather than inferred.

This provenance gate remains separate from the other major remaining camera gate: a genuine verified-front sequential Tintless replay. The historical `TINTCTX` capsule is OV13858 rear mode 1 and must not be reused as front evidence.

## Safety

No Linux camera runtime is performed by this proof. Linux request6 remains fail-closed and unauthorized.
