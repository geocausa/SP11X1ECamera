# Camera project continuation handoff

Use this file when resuming E003h in a fresh ChatGPT conversation.

## Goal

The project goal is the **entire Surface Pro 11 camera stack with Windows behavior/parity as close to 1:1 as practical**, not merely making the front camera show an image. Preserve rear OV13858 behavior while completing front IMX681, ISP/IQ, request generation, userspace integration, switching, suspend/resume and reliability.

## Current branch / safe machine state

- repo: `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`
- branch: `experiment/e003-front-imx681-cphy`
- persistent Golden kernel: `7.1.5-sp11-render-parity-v4+`
- persistent Golden GRUB: `sp11-audio-fullio-v19c`
- SP11 is currently in Golden Linux. The existing Windows installation fails very early in boot and is being treated as a **frozen evidence source**, not an active oracle. Mine Linux/VSS/NTFS/static evidence first; repair/reinstall Windows only when a genuinely new dynamic oracle becomes necessary.
- If Windows is eventually rebuilt, use the normal **GRUB one-shot Windows entry** only; do not repeat the temporary offline BCD experiments from 2026-09-02.
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
- sequential embedded Tintless request5 -> request6 at DeviceMFT RVA `0xc95fd0`: byte-exact, including persistent state, **but the TINTCTX capture is now mechanically identified as OV13858 rear mode 1**. It is a rear/shared-algorithm oracle and must not satisfy the front gate; see `LSC-TINTCTX-CAMERA-IDENTITY-CORRECTION.md` and `LSC-TINTLESS-SEQUENTIAL-REPLAY.md`.
- exact 42-float live LSC trigger vector and `x22/x23` ABI: closed; see `LSC-RUNTIME-INTERPOLATION-BOUNDARY.md`.
- **runtime LSC41 tuning source and generic interpolation: closed byte-exact**; see `LSC-RUNTIME-TUNING-SOURCE-CLOSURE.md` and `prove-lsc-runtime-tuning-source.py`.
- **live LSC golden authority: closed byte-exact** from carved verified-front x22/x23. Rear/default OV13858 `lscgolden41_ife_v2` region `0x2ae` (SHA `f771e54d…`) uniquely satisfies 442/442 red+blue request5/6 calibration equations; nominal IMX681 golden satisfies only 9/442. See `LSC-LIVE-GOLDEN-AUTHORITY.md`.
- **verified-front calibration payload authority: closed byte-exact**. The older rear OV13858 VSS runtime slot (SHA `fb14d234…`) plus rear/default golden reproduces the complete front req5/req6 calibrated x23 payloads byte-for-byte, including all 884 floats and tail; the slot also resolves the three green inverse ambiguities. This closes payload bytes, not the upstream live pointer/loader provenance. See `LSC-FRONT-REAR-CALIBRATION-AUTHORITY.md`.
- **verified-front request4 pre-Tintless bridge: closed offline/native**. Exact request4 lux `355.14508` and CCT `4712` generate x22 `99bf4e1d…`; rear/default golden+rear slot generate x23 `a24bba7c…`; native Surface resampler RVA `0x9b6048` produces pre-Tintless mesh `839cae7d…`. See `LSC-FRONT-REQUEST4-PRETINTLESS-BRIDGE.md`.
- LSC request-time tuning-manager ownership is statically closed through CaptureDevice private DataManager -> CapturePipe -> common context -> `ISPInputData+0x1fe8`; see `LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md`. The rear-only A leaf crossover itself is still open upstream at the live private DataManager source-buffer/tree identity.

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

## Latest tuning provenance boundary

`LSC-TUNING-PROVENANCE-BOUNDARY.md` now rules out the simple file-selection explanations. Exact front `SCFG_FRONT_MSHW0490.bin` names only `com.surface.sensormodule.ffc_imx681.bin` and `com.surface.tuned.ffc_imx681.bin`. Whole-file scanning proves the discriminating runtime A mesh is absent from the exact front IMX681 tuning and both tested `com.qti.tuned.default.bin` fallbacks; it occurs exactly once in rear `com.surface.tuned.rfc_ov13858.bin` at offset `1008426`.

The static ownership chain is also pinned. Front `surfacecamfrontsensor8380.sys` loads its selected sensor tuning into device `+0x80/+0x88` and publishes those exact bytes as `InitParams/SensorTuningData`. DeviceMFT `DataManager::LoadDataFromDriver` copies that payload to DataManager `+0x38/+0x30`, and `DataManager::Construct` builds the tuned-mode tree from that exact buffer. `CaptureDevice::ConstructReal` allocates a fresh DataManager per CaptureDevice at `CaptureDevice+0x60`; the DataManager and the earlier selected-Sensor-ID query use the same provider object at `CaptureDevice+0x10`.

The later `LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md` closes the request-time manager path. `CaptureDevice+0x60` is copied into CapturePipe config `+0x10`, lands at `CapturePipe+0x163488`, DataManager vtable `+0x30` returns its private `DataManager+0x28` TuningDataManager, CapturePipe stores it at common context `+0x2460`, BPS/IFE inject that manager into request `ISPInputData+0x1fe8`, and IFELSC411 consumes that one tree. A random/global rear-manager swap is excluded on the normal path.

Therefore the remaining provenance question is narrower still: **what exact bytes back the live verified-front DataManager at `+0x38/+0x30`?** The next Windows oracle should correlate selected Sensor ID, DataManager `+0x38/+0x30`, DataManager `+0x28`, context `+0x2460`, and request `+0x1fe8` in one front stream. If the source hash is front IMX681, investigate parsing/tree mutation; if it is rear OV13858, investigate the live InitParams payload. Do not assume a global CamX manager swap or a bad front SCFG without new evidence.

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

The previous upstream front LSC interpolation bottleneck is **closed**, and the calibrated x23 req5/6 buffers have been raw-carved back from NTFS. Do not reopen the five-IMX681-leaf fitting or invent a hidden x23 materialization transform: `IQInterface::LSC411CalculateSetting` passes the calibrated interpolation destination directly into `LSC411Setting::CalculateHWSetting`.

A correction changes the integrated gate: `E003H_20260902_TINTCTX` is **OV13858 rear mode 1 (4064x2286)**, not the verified IMX681 front stream. Its exact sequential replay cannot be spliced into front LSCTRIGSRC/adaptive-live evidence.

Immediate work is now:

1. use the now-closed verified-front request4 pre-Tintless target (`839cae7d…`) and mine/recover a genuine same-front-stream sequential Tintless wrapper capsule that bridges it into captured front `0x18a0` staging; do not treat the request4 entry-time correction snapshots as same-frame post-request ratios;
2. preserve and use the carved front LSCTRIGSRC x22/x23 as front calibration/tuning evidence, but do not assume its request state equals the independent adaptive-live stream;
3. keep the TINTCTX request5->request6 replay as a rear OV13858/shared-Tintless oracle and fold it into rear parity work;
4. continue static/private-DataManager provenance mining; the one live front DataManager source-buffer hash remains the eventual dynamic oracle if static evidence cannot close it;
5. keep GTM/TMC as the already byte-exact front parallel path;
6. only after a **front-specific** integrated producer/output capsule passes, conduct a separate review before Linux request6.

Windows is not required for the current mining phase. If the remaining front gap eventually becomes irreducibly dynamic, rebuild/repair the Windows oracle then rather than delaying this offline work now.
