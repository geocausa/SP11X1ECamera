# E003h 0073 — front raw OTP provenance closure

Status: **accepted static/cross-binary proof**. No Linux camera runtime is performed and Linux request6 remains forbidden.

## Result

The normal raw calibration source feeding the verified-front camera2 `EEPROMData` path is now closed to the **front camera module's physical EEPROM**.

There are two normal branches, selected by the option byte carried through AVS command `0x801`:

1. option byte `0`: front sensor KMD publishes its already-read physical EEPROM cache as `SensorCalibrationData`; DeviceMFT copies it into `DataManager+0xc8/+0xd0` and supplies those bytes to `EEPROMData`;
2. option byte nonzero: front sensor KMD deliberately frees that cache so UMD can reread without reboot; DeviceMFT therefore takes its own camera-local `CreateAndReadEEPROMData` / `ReadEEPROMDevice` physical-read path.

Both routes converge on the same camera-local raw-data object **before** `CamX::EEPROMData::FormatLSCData`.

Therefore the already-proven rear/default-equivalent front LSC calibration payload cannot be explained by an ordinary rear-camera0 raw-OTP pointer/buffer being injected into camera2. The remaining crossover has moved later, to **EEPROM formatting / library / golden-reference selection**.

Reproducer:

- `prove-lsc-front-raw-otp-provenance.py`
- `lsc-front-raw-otp-provenance-oracle.json`

Pinned binaries:

- `surfacecamavs8380.sys` SHA256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`
- `surfacecamfrontsensor8380.sys` SHA256 `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`
- `QcDeviceMFT8380.dll` SHA256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## AVS -> front KMD function-table identity

### GETFNTABLE handshake

AVS `CameraDeviceOpen` sends IOCTL **`0x2326ab`** when opening the registered sensor device.

The front sensor KMD internal IOCTL handler accepts `CAMERA_DEVICE_IRPCMD_GETFNTABLE` when:

`ioctl & 0x3ffc == 0x26a8`.

For the AVS request:

`0x2326ab & 0x3ffc = 0x26a8`.

The handler returns the live front sensor object pointer at response `+0` and writes zero at response `+8`.

### Returned object is the front sensor dispatcher

`CameraKMDSensorEvtDevicePrepareHardware` allocates the live front sensor object and stores at its first qword:

`FUN_140005270`.

That function is the sensor command dispatcher. Its command `0x801` branch calls:

`CameraSensorDriver_GetInitParams` RVA `0xa350`.

AVS stores the GETFNTABLE response in its device entry beginning at entry `+0x30` and returns handle `entry+8`, therefore:

- `handle+0x28` = live front sensor object / function-table pointer;
- `handle+0x30` = zero direct-dispatch byte.

The generic AVS sensor-handle wrapper consequently takes its direct path and calls the front object's first function without rewriting `w1/x2..x7`.

## Exact `0x801` option-byte transport

`CCaptureFilter::GetInitParams` loads `CCaptureFilter+0x23f` as its option byte and passes it as argument `w4` to `CCameraEngine::GetInitParams`.

`CCameraEngine::GetInitParams` stores that byte at stack `+4`. For its sensor call it emits:

- `w1 = 0x801`;
- `x2 = stack+4` — pointer to the option byte;
- `w3 = 1`;
- output buffer/length in the remaining command arguments.

The direct sensor-handle wrapper preserves those arguments. Front KMD dispatcher `FUN_140005270` then maps original `x2` to `CameraSensorDriver_GetInitParams` argument `x1` and original `w3` to argument `w2`.

At `CameraSensorDriver_GetInitParams` entry:

- `x1` must be non-null;
- `w2` must equal 1;
- the byte at `[x1]` is loaded as the branch selector.

So the AVS option byte is mechanically the exact KMD calibration-cache policy byte.

Important correction retained from the static analysis:

- `CCaptureFilter+0x23e` is associated with `AllowOtpReload`;
- `CCaptureFilter+0x23f` is associated with `EnableContinuousRawDump`.

Do not conflate the two.

## Front KMD physical EEPROM cache

The front sensor KMD stores its raw EEPROM cache at:

- pointer: device `+0x320`;
- size: device `+0x328`.

The native read path:

1. obtains the EEPROM read length;
2. allocates the raw buffer;
3. stores that allocation at device `+0x320`;
4. places the same pointer into the hardware read descriptor;
5. performs the sensor/EEPROM read;
6. records successful physical-read semantics with `Reading OTP data succeed.`;
7. retains the resulting raw length at device `+0x328`.

For the special banked format, checksum selection only canonicalizes the selected bank **in place inside the same physical-read buffer**. It does not substitute packaged calibration data.

## Front KMD `SensorCalibrationData` branch

Once `GetInitParams` reaches the calibration cache:

- if device `+0x320` is null, there is no cached payload to publish;
- if device `+0x320` exists and the incoming option byte is **zero**, the KMD creates the `SensorCalibrationData` entry and writes exactly:
  - payload pointer = device `+0x320`;
  - payload size = device `+0x328`;
- if the incoming byte is **nonzero**, the KMD frees device `+0x320`, zeros `+0x320/+0x328`, and logs that the EEPROM data is not cached so UMD may read it without reboot.

This means the nonzero branch is not an alternate packaged-calibration source. It is an explicit handoff to a later UMD physical reread.

## DeviceMFT transport and fallback

`DataManager::LoadDataFromDriver` parses `SensorCalibrationData`. When present it:

- stores the payload size at `DataManager+0xd0`;
- allocates an owned copy;
- copies the payload;
- stores the resulting pointer at `DataManager+0xc8`.

`DataManager::Construct` then tests those two fields.

### Supplied-data route

When both pointer and size are present, they become the raw input to the camera-local `EEPROMData` object. DeviceMFT's own log labels this path:

`Retrieve OTP from InitPramas.`

Those bytes originated in the front KMD physical EEPROM cache above.

### UMD reread route

When either supplied pointer or size is absent, the same camera-local `ImageSensorModuleData` path executes:

`CamX::ImageSensorModuleData::CreateAndReadEEPROMData`
-> `CamX::EEPROMData::ReadEEPROMDevice`.

The code builds the EEPROM packet/memory-map commands, reads the physical device, allocates the canonical raw-data buffer, then continues into the normal EEPROM formatting calls.

Thus the two normal branches are:

`front physical EEPROM -> front KMD cache -> SensorCalibrationData -> DeviceMFT rawData`

or

`front physical EEPROM -> DeviceMFT camera-local reread -> DeviceMFT rawData`.

They converge before `FormatLSCData`.

## Supplemental restored-Windows registry observation

The currently restored Windows SYSTEM hive was inspected read-only:

- size `17825792`;
- SHA256 `21f2fa03b6fd0766b0578fac2062cf75a8d477439b9e2ca010949c72c82e63c7`;
- a full `hivexml` scan contains no `EnableContinuousRawDump` or `AllowOtpReload` override.

This is **supplemental only**. System Restore changed Windows state, so it is not used to assert the option byte in the earlier accepted September 2 captures. The proof does not need that capture-time value because both normal option branches source raw OTP from the front physical EEPROM.

## Classification

**CLOSED NORMAL RAW-OTP SOURCE CLASS.**

Excluded on the pinned normal path:

- rear camera0 raw-OTP cache pointer being reused as the front camera2 raw buffer;
- a rear/default packaged calibration blob replacing front physical EEPROM before `EEPROMData` formatting;
- AVS command `0x801` accidentally targeting some unrelated sensor function table instead of the live front sensor KMD object.

Not closed here:

- which EEPROM formatting library/callback is selected for camera2;
- how `FormatLSCData` chooses the golden/reference object used to materialize its formatted slot;
- why the verified-front formatted calibration payload is byte-equivalent to the preserved rear/default OV13858 authority;
- the separate live private-DataManager tuning-tree source-buffer identity;
- genuine verified-front sequential Tintless state/stats/output.

## Next provenance target

Trace the **post-raw-OTP formatting boundary**:

1. identify the exact EEPROM driver/library selected for front camera2;
2. trace its callback ownership into the `Format*` sequence;
3. determine where the LSC golden/reference mesh comes from;
4. explain mechanically why `FormatLSCData` produces the rear/default-equivalent calibration authority even though its raw input and physical stream are front IMX681.

The existing byte-exact result already tells us what this stage must explain: rear/default OV13858 `lscgolden41_ife_v2` region `0x2ae` plus the recovered rear-equivalent formatted slot reproduces the verified-front x23 exactly. Raw physical EEPROM ownership is no longer the candidate crossover point.
