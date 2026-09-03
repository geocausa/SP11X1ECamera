# E003h 0073 — front LSC calibration object ownership closure

Status: **accepted offline/static + preserved-capture evidence**. No Linux camera runtime is performed and Linux request6 remains forbidden.

## Result

The normal Surface DeviceMFT path from formatted EEPROM LSC data to the front IFELSC411 request is **camera-local**. A rear-camera0 formatted OTP object/pointer cannot ordinarily alias the verified-front camera2 object.

This closes **object/pointer ownership only**. It does **not** explain why the verified-front calibration payload is byte-equivalent to the previously recovered rear/default authority. That byte-source question moves one stage earlier: what raw OTP / `InitParams` content populates camera2's own `EEPROMData` object before `FormatLSCData`?

Authority binary:

- `QcDeviceMFT8380.dll` SHA256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

Reproducer:

- `prove-lsc-front-calibration-object-ownership.py`
- `lsc-front-calibration-object-ownership-oracle.json`

## Closed native ownership chain

### 1. Camera-indexed storage

`DataManager::Construct` RVA `0x712f50` computes its camera-local HWEnvironment slot using stride **`0xebe8`**.

At VA `0x180713734` the exact ARM64 sequence materializes `0xebe8`, and at `0x18071373c`:

`umaddl x21, w25, w8, x0`

forms:

`cameraSlot = HWEnvironment + cameraId * 0xebe8`.

It then forms `cameraSlot+0xfa18` and retains that pointer for module/EEPROM construction.

### 2. EEPROMData binds its formatted-data base to that camera slot

During `EEPROMData` construction, VA `0x1807139e8` loads the saved pair and VA `0x1807139f8` stores them into `EEPROMData+0x10/+0x18`.

The second stored pointer, `EEPROMData+0x18`, is the exact `cameraSlot+0xfa18` value.

### 3. FormatLSCData writes slot0 into camera-local pOTPData

`CamX::EEPROMData::FormatLSCData` RVA `0x723e40` begins with:

- load `EEPROMData+0x18`;
- add **`0x3fd8`**.

Therefore its formatted LSC destination is:

`cameraSlot + 0xfa18 + 0x3fd8 = cameraSlot + 0x139f0`.

Independently, `CamX::ImageSensorData::GetSensorStaticCapability` RVA `0x71b270` uses the same `cameraId * 0xebe8` stride and copies `0xac90` bytes from:

`cameraSlot + 0xfa28 + 0x3e60 = cameraSlot + 0x13888`

into `SensorStaticCapability+0x3e60`.

The exact difference is:

`0x139f0 - 0x13888 = 0x168`.

So `FormatLSCData` writes LSC slot0 **directly at that camera's pOTPData+0x168**. This is the same first formatted slot already pinned by `LSC-CALIBRATION-APPLICATION-BOUNDARY.md`.

### 4. SensorStaticCapability carries the same camera-local OTP object

At VA `0x18071b304..0x18071b32c`, `GetSensorStaticCapability` performs the camera-indexed source calculation above and copies the full **`0xac90`** pOTPData object to capability offset **`+0x3e60`**.

There is no camera-ID substitution in that copy.

### 5. IFENode binds directly to capability+0x3e60

`CamX::IFENode::FetchSensorInfo` RVA `0x75dcf8`, at VA `0x18075e920..0x18075e93c`, checks `IFENode+0x3638`. If not already populated it loads the SensorStaticCapability pointer at `IFENode+0xa028`, adds **`0x3e60`**, and stores the result at:

`IFENode+0x3638`.

Its own error string names the semantic boundary: `Sensor static capabilities not available`.

Thus `IFENode+0x3638` is the camera-local pOTPData object copied into the selected sensor's static capability.

### 6. ExecuteProcessRequest writes that pointer to ISPInputData+0x2070

The relevant request builder is `CamX::IFENode::ExecuteProcessRequest`, function RVA **`0x7453d0`**.

At VA `0x180745aac` it constructs the request-local ISP input object at:

`x26 + 0x1ef8`

and zeroes exactly **`0x17e60`** bytes.

At VA `0x180745cd0` it loads `IFENode+0x3638`, and at `0x180745cd4` stores that pointer at:

`x26 + 0x3f68`.

The layout equality is exact:

`0x3f68 - 0x1ef8 = 0x2070`.

Therefore this is precisely:

`ISPInputData+0x2070 = IFENode+0x3638`.

The same request-local base is subsequently passed through the IFE IQ setup/calculation chain.

### 7. IFELSC411 consumes that exact slot

`IFELSC411` at VA `0x180a02b18` loads:

`ISPInputData+0x2070`

then adds:

`+0x168`.

This is the formatted LSC slot0 just proven to have been generated inside the same camera-local pOTPData object.

So the normal path is:

`cameraId`
→ `HWEnvironment + cameraId*0xebe8`
→ `EEPROMData::FormatLSCData`
→ camera-local `pOTPData+0x168`
→ `SensorStaticCapability+0x3e60`
→ `IFENode+0x3638`
→ `ISPInputData+0x2070`
→ `IFELSC411 +0x168`.

## Front versus rear capture identity

The preserved verified-front `windows-adaptive-live-20260902` ISPInputData captures are stable:

- request4 SHA `775adcc5…`: `camera=2`, `sensorAR=1`;
- request5 SHA `7328b190…`: `camera=2`, `sensorAR=1`;
- request6 SHA `c51a7b54…`: `camera=2`, `sensorAR=1`.

The preserved rear VSS captures are:

- request1 SHA `14637c3e…`: `camera=0`, `sensorAR=1`;
- request6 SHA `1cf44712…`: `camera=0`, `sensorAR=1`.

Relative to the same HWEnvironment base:

- camera0 pOTPData = `0x13888`;
- camera2 pOTPData = `0x31058`;
- separation = **`0x1d7d0` = `2 * 0xebe8`**.

The separately discovered previous-Tintless cache key `sensorAR + camera*2` is also disjoint for these preserved streams: rear key **1**, verified-front key **5**. That cache therefore does not provide a rear→front alias mechanism either.

## Classification

**CLOSED NORMAL-PATH CAMERA-LOCAL CALIBRATION OBJECT OWNERSHIP.**

Excluded on the SHA-pinned normal path:

- rear camera0 formatted pOTPData object pointer being reused directly as front camera2 pOTPData;
- a same-key previous-Tintless global-cache collision between the preserved rear and verified-front streams.

Not closed by this proof:

- the raw OTP bytes selected for camera2 before `FormatLSCData`;
- whether those bytes arrive from physical EEPROM read, `InitParams`, a default/fallback, or another pre-format source;
- why camera2's formatted LSC payload is byte-equivalent to the preserved rear/default calibration authority;
- the separate live front private-DataManager tuning-buffer identity;
- genuine verified-front sequential Tintless state/stats/output.

## Next provenance target

Trace `EEPROMData` **upstream of `FormatLSCData`**. The native constructor contains both a hardware EEPROM-read path and an explicit `Retrieve OTP from InitPramas.` path. The next static proof must identify the branch conditions and exact raw-data owner for camera2, then determine whether the verified front uses physical EEPROM bytes or `InitParams`-provided/default content.

Do not reinterpret the rear-equivalent calibration bytes as rear physical-sensor routing. Front IMX681 sensor/mode/geometry remain independently verified.
