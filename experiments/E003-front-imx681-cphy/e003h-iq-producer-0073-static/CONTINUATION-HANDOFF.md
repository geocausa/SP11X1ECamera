# Camera project continuation handoff

Use this file when resuming E003h in a fresh ChatGPT conversation.

## Goal

The project goal is the **entire Surface Pro 11 camera stack with Windows behavior/parity as close to 1:1 as practical**, not merely making the front camera show an image. Preserve rear OV13858 behavior while completing front IMX681, ISP/IQ, request generation, userspace integration, switching, suspend/resume and reliability.

## Current branch / safe machine state

- repo: `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`
- branch: `experiment/e003-front-imx681-cphy`
- persistent Golden kernel: `7.1.5-sp11-render-parity-v4+`
- persistent Golden GRUB: `sp11-audio-fullio-v19c`
- SP11 is currently in Golden Linux. Windows was restored sufficiently to produce fresh read-only oracle captures on 2026-09-03/04, including current DataManager source identity and an atomic front Tintless request4/5/6 capsule. Keep Linux as the working target; one-shot boot Windows again only when the remaining same-stream upstream LSC oracle is genuinely required.
- If Windows is eventually rebuilt, use the normal **GRUB one-shot Windows entry** only; do not repeat the temporary offline BCD experiments from 2026-09-02.
- SP7 has a faulty cooling fan. Use it only for lightweight/passive analysis or KDNET hosting; do not give it heavy compute jobs.
- Same-machine Windows/QcDeviceMFT is the authoritative oracle.

## Safety gate

**Atomic upstream producer gate CLOSED on 2026-09-04.** SP11 Linux now reproduces the fresh verified-front atomic request4 pre-Tintless input byte-for-byte from the repaired Windows authority: IMX681 LSC leaves `0x4bd -> 0x4bf` at float32 ratio `0.342`, nominal IMX681 golden, physical front-camera OTP slot and native DeviceMFT RVA `0x9b6048` geometry resampling produce full input SHA `71fdf640...` with 0 byte differences. The same proof first validates request5 end-to-end and reproduces `6499164c...` exactly. The prerequisite for the separate Linux request6 runtime-authorization review is therefore satisfied; request6 hardware execution still requires that review and a bounded candidate.

### Runtime supersession — 0076 request6 closed

That separate Linux runtime gate is now complete. 0075a proved the accepted 0072 five-frame runtime under the required Golden `clk_ignore_unused pd_ignore_unused` boot flags; 0075b proved fresh atomic R4/R5 on the exact accepted 0072 runtime; and 0076 used the exact 0074 kernel/module/DT plus atomic R4/R5/R6 to deliver six QC10C frames `[0,1,2,3,0,1]` / sequences `[0,1,2,3,4,5]`, each 7,778,304 bytes, with clean RT-CDM stop at userdata 6 and no boot faults. The only 0076 functional helper delta from A3 was the DQBUF watchdog from 1 s to 5 s plus monotonic telemetry. A3 is therefore reclassified as a fragile harness timeout, not a kernel/IQ failure. SP11 returned to persistent Golden cleanly after 0076.

The next gate is productionization/source integration of the now-proven producer + executor semantics; captured capsules remain bounded oracle evidence rather than the final dynamic IQ generator.

## Latest accepted closures

- GTM/TMC exact replay: closed, 256/256 qwords.
- Windows GIC wire anomaly/alias: closed.
- LSC calibration application: bounded/closed.
- LSC geometry/resampling: closed.
- LSC post-calculation `0x18a0` staging -> Titan680 LSC0/LSC1/LSC2: closed; LSC2 is zero on the validated live requests.
- **verified-front atomic Tintless request4 -> request5 -> request6: closed byte-exact** on the fresh 2026-09-04 IMX681 `3840x2160` capsule. Request4 lazy-allocates the exact `0x126e8` persistent core; zero-filled and hostile `0xA5` fresh-core replays both reproduce Windows wrapper/core/output state exactly. See `LSC-FRONT-ATOMIC-TINTLESS-REPLAY.md`.
- **fresh atomic Tintless output -> captured staging -> wire: closed**. Exact Q10 output channels agree with the captured `0x18a0` staging and exact Titan680 packer for req4/5/6. The separately captured LSC0/LSC1 raw files are zero placeholders and are explicitly rejected; staging-derived nonzero wire hashes are authoritative.
- **fresh current DataManager source identity: closed for the 2026-09-03 instance**. `DataManager+0x38/+0x30` is exact `com.surface.tuned.ffc_imx681.bin` (6,465,007 bytes, SHA `2c1c7fd9...`), excluding rear-blob source substitution before normal tree construction for this current instance. This does not retroactively identify the exact 2026-09-02 instance. See `LSC-LIVE-CURRENT-DATAMANAGER-SOURCE.md`.
- **current repaired-Windows front LSC authority + fresh atomic upstream generator: CLOSED byte-exact on 2026-09-04**. Hardware KD breakpoints mechanically establish `INTERP1 -> INTERP2 -> INTERP3 -> INTERP4 -> Tintless request4 -> INTERP5 -> Tintless request5`. Current request4 x22 is exact IMX681 leaf interpolation `0x4bd -> 0x4bf` at float32 `0.212`; request5 is exact leaf `0x4bd`. Current physical front OTP + nominal IMX681 golden reproduce current request5 x23 with all 884 floats exact. On SP11 Linux, float32 ratio `0.342` through those same front leaves, front golden/OTP calibration and native DeviceMFT geometry resampler RVA `0x9b6048` reproduces atomic req4 full input SHA `71fdf640...` with **0 byte differences**; req5 independently reproduces `6499164c...` exactly. See `prove-lsc-current-repaired-atomic-request4.py` and `lsc-current-repaired-atomic-request4-oracle.json`. Historical rear/default x22/golden evidence remains valid only for its older independent stream and is not authority for this repaired/current oracle.
- sequential embedded Tintless request5 -> request6 at DeviceMFT RVA `0xc95fd0`: byte-exact, including persistent state, **but the TINTCTX capture is now mechanically identified as OV13858 rear mode 1**. It is a rear/shared-algorithm oracle and must not satisfy the front gate; see `LSC-TINTCTX-CAMERA-IDENTITY-CORRECTION.md` and `LSC-TINTLESS-SEQUENTIAL-REPLAY.md`.
- exact 42-float live LSC trigger vector and `x22/x23` ABI: closed; see `LSC-RUNTIME-INTERPOLATION-BOUNDARY.md`.
- **runtime LSC41 tuning source and generic interpolation: closed byte-exact**; see `LSC-RUNTIME-TUNING-SOURCE-CLOSURE.md` and `prove-lsc-runtime-tuning-source.py`.
- **live LSC golden authority: closed byte-exact** from carved verified-front x22/x23. Rear/default OV13858 `lscgolden41_ife_v2` region `0x2ae` (SHA `f771e54d…`) uniquely satisfies 442/442 red+blue request5/6 calibration equations; nominal IMX681 golden satisfies only 9/442. See `LSC-LIVE-GOLDEN-AUTHORITY.md`.
- **verified-front calibration payload authority: closed byte-exact**. The older rear OV13858 VSS runtime slot (SHA `fb14d234…`) plus rear/default golden reproduces the complete front req5/req6 calibrated x23 payloads byte-for-byte, including all 884 floats and tail. It selects one valid pair at each of the three averaged-green inverse ambiguities, but the physical front raw bytes remain 8 candidates until front-specific evidence resolves them. See `LSC-FRONT-REAR-CALIBRATION-AUTHORITY.md`.
- **verified-front request4 pre-Tintless bridge: closed offline/native**. Exact request4 lux `355.14508` and CCT `4712` generate x22 `99bf4e1d…`; rear/default golden+rear slot generate x23 `a24bba7c…`; native Surface resampler RVA `0x9b6048` produces pre-Tintless mesh `839cae7d…`. See `LSC-FRONT-REQUEST4-PRETINTLESS-BRIDGE.md`.
- LSC request-time tuning-manager ownership is statically closed through CaptureDevice private DataManager -> CapturePipe -> common context -> `ISPInputData+0x1fe8`; see `LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md`. The rear-only A leaf crossover itself is still open upstream at the live private DataManager source-buffer/tree identity.
- **front calibration object ownership is statically closed camera-local**. `DataManager::Construct` uses `cameraId*0xebe8`; `FormatLSCData` lands slot0 at camera-local `pOTPData+0x168`; `GetSensorStaticCapability` copies that camera-local OTP object to capability `+0x3e60`; IFENode binds it at `+0x3638`; `ExecuteProcessRequest` stores it at `ISPInputData+0x2070`; IFELSC411 consumes `+0x168`. Verified front is camera2, rear VSS is camera0, so normal-path rear-object pointer alias is excluded. See `LSC-FRONT-CALIBRATION-OBJECT-OWNERSHIP.md`.
- **front raw OTP provenance is closed to the physical front EEPROM on both normal branches**. AVS `0x801` resolves through GETFNTABLE to the live front KMD dispatcher. Option zero publishes the KMD physical EEPROM cache (`+0x320/+0x328`) as `SensorCalibrationData`; nonzero deliberately drops that cache and DeviceMFT performs its own camera-local physical reread. Both converge before `FormatLSCData`. See `LSC-FRONT-RAW-OTP-PROVENANCE.md`.
- **front calibration/tuning provenance now converges on one request-private tuning-tree gate**. Front EEPROM `gt24p128f_imx681` and rear `st_m24c64` both miss DeviceMFT's exact 11-entry plugin table and use generic `FormatLSCData`; their decisive LSC descriptors are byte-identical. `FormatLSCData` performs no tuning/golden lookup. IFELSC411 later resolves both `lsc41_ife_v2` and `lscgolden41_ife_v2` through the same `ISPInputData+0x1fe8` manager/root and lookup RVA `0x6f39f8`. The Aug-4 raw cache was also proven conclusively rear (rear KMD RVA `0x1f7e8`, exact rear READ size `0x174a`, rear tuning filename), so it cannot resolve the three physical-front green ambiguities. See `LSC-FRONT-CALIBRATION-TUNING-CONVERGENCE.md`.

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

The recovered calibrated x23 buffers close the live golden side independently. Across all 10 installed tuning blobs containing `lscgolden41_ife_v2`, only rear/default OV13858 region `0x2ae` can reproduce both front req5/req6 direct red/blue calibration transforms for all 442 points using one u16 EEPROM value per point. It passes 442/442 uniquely; nominal IMX681 golden passes 9/442. The exact older rear VSS runtime slot then reproduces the complete verified-front req5/req6 x23 payloads byte-for-byte and resolves the three averaged-green inverse ambiguities. This is a byte-authority crossover, not a physical-sensor identity change; the live pointer/loader mechanism remains a separate provenance question.

Static ownership excludes a simple stale rear formatted-OTP object as the mechanism. Camera-local storage is strided by `0xebe8`; the verified-front ISP inputs carry camera ID 2 and the preserved rear VSS carries camera ID 0. `FormatLSCData` writes camera-local `pOTPData+0x168`, and that same camera-local object is carried through SensorStaticCapability -> IFENode -> `ISPInputData+0x2070` -> IFELSC411.

The upstream raw source is closed too. AVS GETFNTABLE resolves command `0x801` to the live front sensor KMD object. With option zero, `CameraSensorDriver_GetInitParams` publishes its physical front-EEPROM cache at `+0x320/+0x328` as `SensorCalibrationData`; with option nonzero, DeviceMFT performs its own camera-local physical reread. Both routes feed the same `EEPROMData` raw input before `FormatLSCData`.

The later convergence proof eliminates formatting as an independent crossover. Exact front EEPROM `gt24p128f_imx681` and rear `st_m24c64` both miss the built-in custom-plugin table, use the same generic `FormatLSCData`, and share a byte-identical LSC descriptor over `0x103d..0x1724`. Generic formatting contains no tuning lookup. IFELSC411 then resolves both the already-proven rear/default `lsc41_ife_v2` authority and the rear/default `lscgolden41_ife_v2` authority from the **same request-private tuning manager/root**. Thus these are one tuning-tree provenance problem. A full ARM64 active-dump revalidation also proves the Aug-4 raw cache is rear-only and cannot be promoted to front physical EEPROM evidence.

## Latest tuning provenance boundary

`LSC-TUNING-PROVENANCE-BOUNDARY.md` now rules out the simple file-selection explanations. Exact front `SCFG_FRONT_MSHW0490.bin` names only `com.surface.sensormodule.ffc_imx681.bin` and `com.surface.tuned.ffc_imx681.bin`. Whole-file scanning proves the discriminating runtime A mesh is absent from the exact front IMX681 tuning and both tested `com.qti.tuned.default.bin` fallbacks; it occurs exactly once in rear `com.surface.tuned.rfc_ov13858.bin` at offset `1008426`.

The static ownership chain is also pinned. Front `surfacecamfrontsensor8380.sys` loads its selected sensor tuning into device `+0x80/+0x88` and publishes those exact bytes as `InitParams/SensorTuningData`. DeviceMFT `DataManager::LoadDataFromDriver` copies that payload to DataManager `+0x38/+0x30`, and `DataManager::Construct` builds the tuned-mode tree from that exact buffer. `CaptureDevice::ConstructReal` allocates a fresh DataManager per CaptureDevice at `CaptureDevice+0x60`; the DataManager and the earlier selected-Sensor-ID query use the same provider object at `CaptureDevice+0x10`.

The later `LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md` closes the request-time manager path. `CaptureDevice+0x60` is copied into CapturePipe config `+0x10`, lands at `CapturePipe+0x163488`, DataManager vtable `+0x30` returns its private `DataManager+0x28` TuningDataManager, CapturePipe stores it at common context `+0x2460`, BPS/IFE inject that manager into request `ISPInputData+0x1fe8`, and IFELSC411 consumes that one tree. A random/global rear-manager swap is excluded on the normal path.

Therefore the remaining provenance question is narrower still: **what exact bytes back the live verified-front DataManager at `+0x38/+0x30`?** The next Windows oracle should correlate selected Sensor ID, DataManager `+0x38/+0x30`, DataManager `+0x28`, context `+0x2460`, and request `+0x1fe8` in one front stream. If the source hash is front IMX681, investigate parsing/tree mutation; if it is rear OV13858, investigate the live InitParams payload. Do not assume a global CamX manager swap or a bad front SCFG without new evidence.

### Private parser / mutation closure

`LSC-PRIVATE-TUNING-TREE-PROVENANCE.md` now closes the ordinary downstream mutation theories. The Aug-4 active dump revalidates complete front/rear KMD module+tuning buffers byte-for-byte against their installed authorities and contains a serialized front `SensorTuningData` record with exact front length/identity. Normal DeviceMFT construction creates a fresh manager and fresh `0x1640` parser with instance-local tree storage/root at `+0x430/+0x428`. A decoded BL scan finds only two calls to the tree-graft helper `0x6f3780`: its own recursion and `DataManager::LoadTuningBin`. Live reload is behind CamX EnableLiveTuning bit29 and the nonzero request-mod-10 gate; AVS sources that bit from `DeviceConfigInfo+0xc0` / `CCaptureFilter+0x6d8` and defaults it to zero when `HKLM\SYSTEM\CurrentControlSet\Control\Qualcomm\Camera\enableLiveTuning` is absent.

This does **not** retroactively prove the September capture-time override value. It means that if the September private DataManager source was front IMX681 and live tuning was disabled, normal parser/cache/graft mechanisms are exhausted. The decisive remaining source oracle is still the exact September `DataManager+0x38/+0x30` identity.

**Restore-side evidence note:** after Windows System Restore, the original `E003H_20260902_LSCTRIGSRC` trigger-vector files are no longer present at their Windows path. The durable x22/x23 carves and accepted runtime-source oracle remain, but `prove-lsc-runtime-tuning-source.py` is not currently rerunnable from its default capture directory. Do not synthesize replacement trigger-vector files; recover them from NTFS/VSS if possible or recapture only when Windows is intentionally used as an oracle again.

## Latest live/front oracle and recovered raw evidence

System Restore removed the later `SP11CameraOracle` directories from the live Windows profile. Do **not** depend on `/mnt/windows/.../E003H_20260902_LSCTRIGSRC` or `TINTCTX` existing. Read-only NTFS carving recovered the authoritative LSCTRIGSRC req5/6 x22+x23 buffers and a subset of TINTCTX under:

`experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/oracle-carved-20260902/`

The front LSCTRIGSRC capture at LSC411Interpolation post RVA `0x93c8e8` remains valid:

- `x22` = generic pre-calibration LSC41 interpolation result.
- `x23` = calibrated destination.
- request5 x22 SHA `e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de`
- request6 x22 SHA `3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8`
- request5 x23 SHA `94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71`
- request6 x23 SHA `62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15`

Exact 42-float trigger vector is captured for both requests. LSC control vector `[8,2,5,100,0,6]` consumes indices `[8,2,5,19,20,21,0,6]`. Request5 mapped values are `[370,1,1,1,0,0,400.9328003,4999]`; request6 differs only in index0=`400.2722778`.

## Current open problem / immediate action

The atomic producer proof and bounded Linux request4/5/6 executor are both closed. Immediate work is now **productionization/source integration**:

1. keep SP11 on protected Golden except for explicit bounded candidates; all camera candidate boot entries must inherit `clk_ignore_unused pd_ignore_unused`;
2. inspect the canonical front-camera source/integration path and identify which 0074 executor pieces are still experiment-only one-shot plumbing versus reusable driver behavior;
3. promote the proven request ordering, V4L2 ownership/requeue semantics and producer contract into the canonical source without hardcoding captured request4/5/6 replay as the production IQ engine;
4. connect the already-closed repaired-Windows producer semantics to dynamic Linux request generation, preserving exact Windows-derived tuning/calibration/Tintless/GTM materialization and request-local state;
5. run bounded regression first (request4/5/6, clean teardown, Golden return), then extend toward sustained streaming, controls/modes, camera switching, suspend/resume and reliability;
6. use Windows/SP7 only when a genuinely missing oracle is encountered; otherwise continue from Linux and the existing byte-exact proofs.

Do not reopen the old request6-authorization gate unless a productionization change alters the proven hardware contract.
