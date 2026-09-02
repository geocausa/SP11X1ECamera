# E003h 0073 — LSC tuning-manager ownership closure

Status: **closed static ownership chain**. This checkpoint supersedes the open request-time-manager part of `LSC-TUNING-PROVENANCE-BOUNDARY.md`. It does **not** yet explain why the live front manager/tree resolves the rear-only OV13858 LSC41 leaf. No Linux camera runtime or Linux request6 is performed or authorized.

## Result

The `TuningDataManager*` consumed by `IFELSC411` is not taken from an unconditional global manager and is not selected independently at the IQ-module boundary. The exact Surface DeviceMFT wiring carries the same CaptureDevice's private DataManager into its CapturePipe, asks that DataManager for its private TuningDataManager, stores the result in the common CamX node context, and injects that pointer into `ISPInputData` for IQ modules.

The chain is:

`CaptureDevice+0x60 private DataManager`

`-> CapturePipe config +0x10`

`-> CapturePipe+0x163488`

`-> DataManager vtable +0x30`

`-> DataManager+0x28 private TuningDataManager*`

`-> common node/pipeline context +0x2460`

`-> ISPInputData+0x1fe8`

`-> IFELSC411 one-tree lookup("lsc41_ife_v2")`.

This rules out the current theory that a rear/global TuningDataManager pointer is simply swapped into the front request after an otherwise-correct front DataManager was constructed.

## CaptureDevice -> CapturePipe ownership bridge

`CaptureDevice::ConstructReal` (RVA `0x291c00`) allocates a fresh `0x220`-byte DataManager, constructs it with the CaptureDevice's provider, and stores it at `CaptureDevice+0x60`. That per-CaptureDevice allocation was already accepted by `LSC-TUNING-PROVENANCE-BOUNDARY.md`.

The CapturePipe configuration builder at RVA `0x293ad8` makes the ownership transfer explicit. ARM64 at `0x293b14` is:

```text
ldr x8, [x19, #0x60]
str x8, [x20, #0x10]
```

where `x19` is the CaptureDevice and `x20` is the `0x1c8`-byte CapturePipe configuration object. Therefore:

`CapturePipeConfig+0x10 = CaptureDevice+0x60 = that CaptureDevice's private DataManager*`.

`CapturePipe::Construct` at RVA `0x2acb60` copies the complete `0x1c8`-byte configuration into `CapturePipe+0x163478`. Consequently config `+0x10` lands at:

`CapturePipe+0x163478+0x10 = CapturePipe+0x163488`.

There is no lookup or camera-ID remapping in this transfer.

## CapturePipe -> private TuningDataManager

`CapturePipe::ConfigureMetadata` at RVA `0x2c2250` loads `CapturePipe+0x163488`, loads its vtable slot `+0x30`, and calls it. The returned pointer is saved at `CapturePipe+0x1e00`, then copied to the common node/pipeline context at `+0x2460`.

The DataManager vtable used by the exact binary begins at VA `0x18133b780`. Its `+0x30` entry at VA `0x18133b7b0` points to VA `0x1800517c0`. That function is exactly:

```text
ldr x0, [x0, #0x28]
ret
```

So the virtual call is a direct accessor for `DataManager+0x28`.

`DataManager+0x28` is the CamX `TuningDataManager*` created by `DataManager::Construct` from the same DataManager's `SensorTuningData` buffer (`+0x38` pointer / `+0x30` size), as already bounded by the preceding provenance checkpoint.

Therefore:

`CapturePipe common context +0x2460 = CaptureDevice private DataManager +0x28`.

## Common context -> request-time ISPInputData

The same `+0x2460` field is consumed by multiple CamX nodes and by `ChiNodeWrapper::FNGetData`, independently confirming its tuning-manager role.

For IFE, `IFENode::UpdateInitSettings` at RVA `0x73c298` contains:

```text
ldr x8, [x19, #0x400]
ldr x8, [x8, #0x2460]
str x8, [x9, #0xa38]
```

which copies the common-node tuning manager into IFE input state.

For BPS, `BPSNode::ExecuteProcessRequest` at RVA `0x780070` contains the direct request build:

```text
ldr x11, [x19, #0x400]
ldr x8,  [x11, #0x2460]
str x8,  [x26, #0x21a0]
```

The same stack-local ISP input has `tuningModeChanged` at stack `+0x2220`. The delta is `0x80`, exactly matching the known `ISPInputData` layout delta `0x2068 - 0x1fe8 = 0x80`. Thus stack `+0x21a0` is `ISPInputData+0x1fe8` and receives the common context `+0x2460` pointer directly.

## IFELSC411 consumes only that manager/tree

`IFELSC411::CheckAndUpdateChromatixData` at RVA `0xa02420` begins by loading:

```text
ldr x23, [x20, #0x1fe8]
```

It validates that manager/tree and calls the already-inspected generic tuned-mode lookup for `lsc41_ife_v2`. That lookup searches one supplied tree and does not fall back to another tuning package.

Therefore the request-time ownership path is closed end-to-end.

## What this excludes

This checkpoint excludes the following explanation for the rear-only live LSC A leaf:

1. a single unconditional global TuningDataManager is injected into all CaptureDevices;
2. CapturePipe independently chooses a tuning manager unrelated to its CaptureDevice;
3. IFE/BPS independently substitute a rear manager while building `ISPInputData`;
4. IFELSC411 falls back to a second/rear tuning tree during module lookup.

The normal static path is camera-instance-local from CaptureDevice DataManager through IFELSC411.

## Remaining provenance question

The contradiction is now upstream and measurable:

**What exact bytes back the live front CaptureDevice's private DataManager/TuningDataManager?**

The next Windows oracle should be deliberately narrow and same-session. On a verified front IMX681 stream, capture only:

- selected sensor ID;
- CaptureDevice private DataManager pointer;
- `DataManager+0x38` source tuning-buffer pointer and `DataManager+0x30` byte count;
- SHA256 / bounded copy of that exact source tuning buffer;
- `DataManager+0x28` TuningDataManager pointer;
- CapturePipe/common-context `+0x2460` pointer;
- request `ISPInputData+0x1fe8` pointer;
- resolved `lsc41_ife_v2` module/leaf pointer if needed.

If the source-buffer hash is the exact front IMX681 tuning hash, the remaining bug/behavior lies inside parsing/tree contents or a later mutation of that same manager. If the source-buffer hash is rear tuning, then the inconsistency is already present in the live `InitParams/SensorTuningData` payload despite the statically clean FFC route.

Do not repeat broad LSC trigger fitting. Request5/request6 `x22` and all downstream LSC stages are already closed.

## Safety

Linux request6 remains fail-closed. This checkpoint performs static binary validation only and does not authorize Linux camera runtime.

Proof: `prove-lsc-tuning-manager-ownership.py`

Oracle: `lsc-tuning-manager-ownership-oracle.json`
