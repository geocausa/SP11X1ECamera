# Camera project continuation handoff

Use this file when resuming E003h in a fresh ChatGPT conversation.

## Goal

The project goal is the **entire Surface Pro 11 camera stack with Windows behavior/parity as close to 1:1 as practical**, not merely making the front camera show an image. Preserve rear OV13858 behavior while completing front IMX681, ISP/IQ, request generation, userspace integration, switching, suspend/resume and reliability.

## Current branch / safe machine state

- repo: `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`
- branch: `experiment/e003-front-imx681-cphy`
- persistent Golden kernel: `7.1.5-sp11-render-parity-v4+`
- persistent Golden GRUB: `sp11-audio-fullio-v19c`
- SP11 Linux/Windows can be rebooted and instrumented as needed.
- Use the normal **GRUB one-shot Windows entry**; do not repeat the temporary offline BCD experiments from 2026-09-02.
- SP7 has a faulty cooling fan. Use it only for lightweight/passive analysis or KDNET hosting; do not give it heavy compute jobs.
- Same-machine Windows/QcDeviceMFT is the authoritative oracle.

## Safety gate

**Do not run Linux request6 yet.** Runtime LSC interpolation is now byte-exactly reproduced, but the gate remains fail-closed until the complete request5/request6 producer chain is replayed against one atomic Windows capsule and a separate runtime authorization review passes.

## Latest accepted closures

- GTM/TMC exact replay: closed, 256/256 qwords.
- Windows GIC wire anomaly/alias: closed.
- LSC calibration application: bounded/closed.
- LSC geometry/resampling: closed.
- LSC post-calculation `0x18a0` staging -> Titan680 LSC0/LSC1/LSC2: closed; LSC2 is zero on the validated live requests.
- sequential embedded Tintless request5 -> request6 at DeviceMFT RVA `0xc95fd0`: byte-exact, including persistent state; see `LSC-TINTLESS-SEQUENTIAL-REPLAY.md`.
- exact 42-float live LSC trigger vector and `x22/x23` ABI: closed; see `LSC-RUNTIME-INTERPOLATION-BOUNDARY.md`.
- **runtime LSC41 tuning source and generic interpolation: closed byte-exact**; see `LSC-RUNTIME-TUNING-SOURCE-CLOSURE.md` and `prove-lsc-runtime-tuning-source.py`.
- LSC tuning-manager provenance is statically bounded through front SCFG -> front KMD `SensorTuningData` -> per-CaptureDevice DataManager/TuningDataManager; see `LSC-TUNING-PROVENANCE-BOUNDARY.md`. The rear-only A leaf crossover itself is still open.

## Latest LSC source closure

The old hypothesis that runtime Chromatix transforms the five serialized IMX681 LSC leaves is superseded.

The exact first runtime leaf consumed by generic interpolation is SHA256:

`d5b6ba5acb7c6e29935a455896d433debec9203800b77899cdf64bc17f02791d`

It is absent from `com.surface.tuned.ffc_imx681.bin` and exists byte-for-byte in Surface rear tuning `com.surface.tuned.rfc_ov13858.bin` as region symbol `0x2a0`, absolute offset `1008426`.

The second runtime leaf is SHA256:

`f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8`

and is rear region `0x2a4`, absolute offset `1012018`, the all-ones mesh.

Rear Default `lsc41_ife_v2` symbol `0x29` uses the exact live control vector `[8,2,5,100,0,6]`. At selector 0, its two bands are `[1,340]` and `[430,900]`. With live trigger-vector index0:

- request5 `400.93280029296875` -> float32 ratio `0.6770310997962952` -> exact x22 SHA `e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de`;
- request6 `400.27227783203125` -> float32 ratio `0.6696919798851013` -> exact x22 SHA `3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8`.

The replay matches both accepted Windows `x22` buffers byte-for-byte using the exact DeviceMFT RVA `0x93c940` arithmetic. The raw exploratory `E003H_20260902_LSCCALLBACK` capture independently records those exact A/B runtime leaf bytes.

Do **not** interpret this as proof that Windows configures the rear physical sensor for the front stream. It proves the byte provenance of the LSC41 object resolved by the front stream.

## Latest tuning provenance boundary

`LSC-TUNING-PROVENANCE-BOUNDARY.md` now rules out the simple file-selection explanations. Exact front `SCFG_FRONT_MSHW0490.bin` names only `com.surface.sensormodule.ffc_imx681.bin` and `com.surface.tuned.ffc_imx681.bin`. Whole-file scanning proves the discriminating runtime A mesh is absent from the exact front IMX681 tuning and both tested `com.qti.tuned.default.bin` fallbacks; it occurs exactly once in rear `com.surface.tuned.rfc_ov13858.bin` at offset `1008426`.

The static ownership chain is also pinned. Front `surfacecamfrontsensor8380.sys` loads its selected sensor tuning into device `+0x80/+0x88` and publishes those exact bytes as `InitParams/SensorTuningData`. DeviceMFT `DataManager::LoadDataFromDriver` copies that payload to DataManager `+0x38/+0x30`, and `DataManager::Construct` builds the tuned-mode tree from that exact buffer. `CaptureDevice::ConstructReal` allocates a fresh DataManager per CaptureDevice at `CaptureDevice+0x60`; the DataManager and the earlier selected-Sensor-ID query use the same provider object at `CaptureDevice+0x10`.

Therefore the remaining provenance question is narrower: trace the selected-sensor provider and the exact TuningDataManager/module pointer that reaches IFELSC411. Do not assume a global CamX manager swap or a bad front SCFG without new evidence.

## Latest live oracle

Raw/untracked Windows capture directory:

`C:\Users\Geoca\Documents\SP11CameraOracle\E003H_20260902_LSCTRIGSRC`

On Linux after mounting the Windows volume read-only:

`/mnt/windows/Users/Geoca/Documents/SP11CameraOracle/E003H_20260902_LSCTRIGSRC`

At LSC411Interpolation post RVA `0x93c8e8`:

- `x22` = generic pre-calibration LSC41 interpolation result.
- `x23` = calibrated destination.
- request5 x22 SHA `e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de`
- request6 x22 SHA `3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8`
- request5 x23 SHA `94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71`
- request6 x23 SHA `62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15`

Exact 42-float trigger vector is captured for both requests. LSC control vector `[8,2,5,100,0,6]` consumes indices `[8,2,5,19,20,21,0,6]`. Request5 mapped values are `[370,1,1,1,0,0,400.9328003,4999]`; request6 differs only in index0=`400.2722778`.

## Current open problem / immediate action

The previous upstream LSC interpolation bottleneck is **closed**. Do not spend more time fitting the five IMX681 LSC leaves or looking for a hidden numerical materialization transform.

Immediate work is now:

1. build one integrated offline request5 -> request6 LSC replay beginning with the newly closed rear/default LSC41 source;
2. chain it through the already-closed golden/EEPROM calibration -> geometry -> exact sequential Tintless -> staging -> Titan680 LSC0/LSC1/LSC2 -> GIC path and demand byte parity against one atomic Windows capsule;
3. independently trace the tuning-loader/overlay provenance that makes the front stream resolve the rear/default LSC41 branch, and check whether the same overlay rule affects other IQ modules;
4. keep GTM/TMC as the already byte-exact parallel path;
5. only after the integrated producer/output capsule passes, conduct a separate review before Linux request6.
