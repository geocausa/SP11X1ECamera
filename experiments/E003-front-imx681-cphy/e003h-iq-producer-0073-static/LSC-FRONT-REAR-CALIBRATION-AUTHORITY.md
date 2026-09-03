# E003h 0073 — verified-front rear/default LSC calibration authority

Status: **accepted offline byte-exact proof**. No Linux camera runtime or Linux request6 is performed or authorized.

## Result

The recovered verified-front LSCTRIGSRC request5/request6 pre-calibration `x22` and calibrated `x23` payloads are reproduced **byte-for-byte** by combining:

- the already-proven rear/default OV13858 `lscgolden41_ife_v2` region `0x2ae`, SHA `f771e54d183281251bf0ef6d94e94a0d439c641f8b8ed9a3ad60ead4094487d6`; and
- the exact 0xdf0-byte runtime LSC calibration slot recovered from the older OV13858 VSS capture, SHA `fb14d234d55317c9665de39fe93ddeb76ee06b9cffc64bee8d250152ae9dfa18`.

The VSS slot is independently identified as rear-camera state by its captured geometry `4076x2806 -> 4064x2286`, crop `(6,260)`. Its slot header is `(available=1, lightType=3, meshSize=221)`, followed by four 221-float planes at offsets `0x0c`, `0x380`, `0x6f4`, and `0xa68`; every sample is an integer-valued float32, exactly matching the proven u16 EEPROM formatter contract.

Applying the exact Surface calibration arithmetic to the verified-front data gives:

- request5 generated `x23`: `94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71` — exactly the Windows capture;
- request6 generated `x23`: `62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15` — exactly the Windows capture.

The equality covers the complete `0xdf0` payload: all 884 float32 mesh values plus the final 0x20-byte region tail.

## EEPROM inverse cross-check

The earlier live-golden proof inverted the red and blue equations independently. Re-running that inverse with both request5 and request6 proves **442/442 direct points have one unique integer EEPROM value**, and every value equals the corresponding sample in the rear VSS runtime slot.

The two calibrated green planes are averaged by Windows, so three mesh positions have two mathematically valid `(G1,G2)` integer pairs. The exact rear runtime slot resolves them as:

- point 19: `(336,334)` from candidates `(335,335)` / `(336,334)`;
- point 57: `(751,753)` from candidates `(751,753)` / `(752,752)`;
- point 94: `(970,965)` from candidates `(967,968)` / `(970,965)`.

For every other green point the pair is unique. Therefore the rear VSS slot matches the complete 4x221 calibration payload consistent with both verified-front requests.

## Generic trigger mapping pinned

`CamX::IQInterface::SetupGenericTrigger` at RVA `0x897b78` is also machine-code pinned:

- canonical generic vector index 0 is loaded from `ISPInputData+0x20b8`, the raw `ISPIQTriggerData+0x38` AEC lux index;
- canonical vector index 6 is loaded from `ISPInputData+0x20c8`, the raw `ISPIQTriggerData+0x48` AWB color temperature.

This removes the prior need to infer the generic LSC selector values by field name.

## Camera-local object ownership refinement

`LSC-FRONT-CALIBRATION-OBJECT-OWNERSHIP.md` closes the downstream pointer/object path. The formatted EEPROM object consumed by a request is camera-local: `cameraId * 0xebe8` storage -> `FormatLSCData` -> pOTPData -> SensorStaticCapability -> IFENode -> `ISPInputData+0x2070`. Verified front uses camera ID 2 while the preserved rear VSS uses camera ID 0. Therefore this payload-authority crossover is **not explained by ordinary rear-camera0 formatted-object pointer reuse**.

`LSC-FRONT-RAW-OTP-PROVENANCE.md` closes the upstream raw input too. AVS command `0x801` resolves to the live front sensor KMD; option zero publishes that KMD's physical front-EEPROM cache as `SensorCalibrationData`, while nonzero intentionally drops the cache and DeviceMFT performs its own camera-local physical EEPROM reread. Both routes converge before `FormatLSCData`.

`LSC-FRONT-CALIBRATION-TUNING-CONVERGENCE.md` then closes the post-raw formatting question: both Surface modules use the same generic formatter, their LSC descriptors are byte-identical, and generic `FormatLSCData` contains no tuning/golden lookup. The rear/default `lsc41_ife_v2` and `lscgolden41_ife_v2` authorities are instead resolved from the same request-private tuning tree. The older rear slot still closes parity bytes, but its three selected green pairs must not be reinterpreted as physical-front EEPROM identity; current front evidence leaves 8 parity-equivalent raw candidates.

## Provenance scope

This is a **calibration-payload byte-authority** result. It proves that the exact rear runtime slot is the payload needed to reproduce the verified physical-front IMX681 calibration transform. It does not by itself prove which live front pointer/loader object supplied those bytes. The separate private-DataManager/tuning-tree provenance question remains upstream.

The physical stream identity is unchanged: independent sensor programming and geometry identify the verified stream as front IMX681.

Proof artifacts:

- `prove-lsc-front-rear-calibration-authority.py`
- `lsc-front-rear-calibration-authority-oracle.json`
