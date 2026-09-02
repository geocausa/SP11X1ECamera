# E003h 0073 — LSC tuning-manager provenance boundary

Status: **accepted static provenance checkpoint; request-time manager ownership superseded/closed by `LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md`**. This follows the byte-exact runtime-source closure in `LSC-RUNTIME-TUNING-SOURCE-CLOSURE.md`. It does not yet explain why the live front IMX681 stream resolves one rear OV13858 LSC41 leaf, but it sharply bounds where that crossover can occur. No Linux camera runtime or Linux request6 is performed or authorized.

## Discriminating leaf provenance

The live first generic-interpolation A input remains SHA256:

`d5b6ba5acb7c6e29935a455896d433debec9203800b77899cdf64bc17f02791d`

for exactly `0xdf0` bytes.

A whole-file byte search across the exact relevant tuning authorities proves:

- `com.surface.tuned.ffc_imx681.bin`, SHA256 `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`: **no A occurrence**;
- `com.surface.tuned.rfc_ov13858.bin`, SHA256 `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`: exactly one A occurrence, offset **1,008,426**;
- platform `com.qti.tuned.default.bin`, SHA256 `aa685fb55e528e717eaf115112dd08bffb5d15c7cd00c4570282163667008150`: **no A occurrence**;
- rear-extension `com.qti.tuned.default.bin`, SHA256 `ca620fbcfd9bde3c25157289ac7172244fb39744b36d293ea53ab94422eea634`: **no A occurrence**.

This matters because the second callback input B is an all-ones mesh and occurs in multiple tuning packages; A is the discriminating byte identity. Among these exact front/rear/default authorities, A is rear-OV13858-only.

## Front board configuration does not name rear tuning

Exact `SCFG_FRONT_MSHW0490.bin` is 133 bytes, SHA256:

`e6e3d828a1e4f5bc94c545848a091c20be399a4b22c938ed4a3df072dd033d99`.

It explicitly names:

- `com.surface.sensormodule.ffc_imx681.bin`;
- `com.surface.tuned.ffc_imx681.bin`.

It contains no `rfc_ov13858` name. Therefore the rear A leaf is not explained by the front SCFG simply pointing at the rear package.

## Exact front KMD tuning handoff

Exact `surfacecamfrontsensor8380.sys` SHA256 is:

`80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`.

Static ARM64 decompilation pins these functions:

- `CameraSensorDriver_Init` RVA `0x8a50`;
- `CameraSensorDriver_GetInitParams` RVA `0xa350`;
- binary loader RVA `0x4708`.

After successful sensor probe, `CameraSensorDriver_Init` loads the sensor tuning filename stored in the copied sensor-init configuration at device `+0x21a`. The loaded tuning bytes are retained at:

- device `+0x80` = tuning buffer pointer;
- device `+0x88` = tuning byte count.

Only if that selected sensor tuning file cannot be loaded does this KMD explicitly fall back to `com.qti.tuned.default.bin`.

`CameraSensorDriver_GetInitParams` then creates the `SensorTuningData` entry and copies exactly device `+0x80/+0x88` into that response payload.

So the front KMD side of the contract is:

`selected sensor tuning filename -> KMD +0x80/+0x88 -> InitParams/SensorTuningData`.

## Exact DeviceMFT DataManager handoff

Exact `QcDeviceMFT8380.dll` SHA256 is:

`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

`DataManager::LoadDataFromDriver` at RVA `0x7165a8` parses the driver response as `InitParams`, then enters `SensorInfo`, then recognizes `SensorTuningData`. That payload is copied verbatim into:

- `DataManager+0x38` = tuning-buffer pointer;
- `DataManager+0x30` = tuning byte count.

`DataManager::Construct` at RVA `0x712f50` creates a CamX tuning manager, assigns that exact `+0x38/+0x30` buffer/length to it, and invokes the tuned-mode-tree creation path (`TuningDataManager::CreateTunedModeTree`, RVA `0x6f52c8`).

There is no later arbitrary list-of-files merge in this path before the tree is created.

## DataManager ownership is per CaptureDevice

A stronger ownership result comes from `CaptureDevice::ConstructReal` at RVA `0x291c00`.

It allocates a fresh **0x220-byte DataManager object**, constructs it, and stores the result at `CaptureDevice+0x60` (`param_1[0xc]`). This rules out the simple theory that one unconditional global DataManager/TuningDataManager object is shared by every CaptureDevice.

The DataManager constructor receives `CaptureDevice+0x10`. Importantly, `CaptureDevice::Construct` uses that same provider object to request the selected sensor information and logs:

`Camera Sensor ID:%d`.

The later DataManager uses the same provider to request `InitParams`, from which it extracts `SensorTuningData`.

Therefore, within one CaptureDevice, the selected-sensor query and tuning payload are tied to the same provider object:

`CaptureDevice+0x10 -> selected Sensor ID`

and

`CaptureDevice+0x10 -> InitParams -> SensorTuningData -> private DataManager -> tuned-mode tree`.

The later ownership closure proves the exact request-time path from this private DataManager through CapturePipe/common context into `ISPInputData+0x1fe8`, so random/global manager substitution is now excluded on the normal path. This checkpoint still does **not** prove that the live provider returns mutually consistent sensor ID and tuning bytes.

## What is now excluded

The rear-only A mesh cannot currently be explained by any of these simpler theories:

1. the front SCFG directly names the rear OV13858 tuning file;
2. A is secretly present somewhere else in the exact front IMX681 tuning file;
3. A comes from either tested `com.qti.tuned.default.bin` fallback;
4. every camera unconditionally shares one global DataManager created once by DeviceMFT.

The front stream itself remains mechanically identified as IMX681: the already-closed Windows geometry is full `4048x3152`, crop `(104,496)`, output `3840x2160`, scale 1, with the independently closed IMX681 mode-2 sensor programming. The rear A leaf therefore must not be reinterpreted as proof that the captured stream was physically the rear camera.

## Remaining provenance gate

The next useful question is now narrow:

**What exact source buffer/file backs the verified live front CaptureDevice's private DataManager/TuningDataManager?**

The request-time handoff is now statically closed by `LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md`. The next Windows observation should be deliberately tiny: in one verified front-stream session capture selected Sensor ID, DataManager `+0x38/+0x30` source-buffer identity, DataManager `+0x28`, common-context `+0x2460`, and request `ISPInputData+0x1fe8`. Do not repeat broad state dumps or LSC trigger fitting.

This provenance investigation is separate from the output-parity gate. Request5/request6 front `x22` is byte-exact, and recovered x23 now uniquely pins the live golden to rear/default OV13858 too. Geometry/staging/packer are front-closed, but the historical sequential TINTCTX replay is rear mode1 and therefore does **not** close front Tintless state. The next front parity milestone is a same-front-stream Tintless bridge and then an integrated offline replay.

Linux request6 remains fail-closed.

Proof: `prove-lsc-tuning-provenance-boundary.py`

Oracle: `lsc-tuning-provenance-boundary-oracle.json`
