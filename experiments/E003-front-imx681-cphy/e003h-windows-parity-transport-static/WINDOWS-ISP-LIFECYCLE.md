# Same-machine Windows ISP lifecycle — static + dynamic oracle

Date: 2026-08-28

This combines static evidence from the exact Windows camera binaries installed for this SP11 with a two-pass same-machine KD runtime oracle. No external implementation is treated as behavioral evidence.

## Exact binaries

- `qccamisp8380.sys` SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- `qccammipicsi8380.sys` SHA-256 `033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407`
- `surfacecamfrontsensor8380.sys` SHA-256 `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`
- `com.surface.sensormodule.ffc_imx681.bin` SHA-256 `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`

Proprietary bytes remain local and are not committed.

## ISP device start

The exact `qccamisp8380.sys` ARM64 DEVICE_START branch is selected by command `0x804` at VA `0x140015ee0`.

Mechanical call ordering in the disassembly is:

1. start the allocated IFE core(s) with command `0x804`;
2. submit the initial configuration packets with command `0x803` to the IFE/CSID resources;
3. start the CSID core(s) with command `0x804`.

The nearby exact diagnostic strings identify the failing operations as `ife%d Start_cmd`, initial packet failures to `ife%d` / `csid%d`, and `CSID%d Start_cmd` respectively.

Therefore the Windows ISP-internal start order is:

**IFE start -> initial IFE/CSID configuration packets -> CSID start**.

## ISP device stop

The DEVICE_STOP branch is selected by command `0x805` at VA `0x140016300`.

Mechanical call ordering is:

1. invoke command `0x805` on the CSID core resource;
2. invoke command `0x805` on the IFE core resource;
3. invoke command `0x805` on the CDM/remaining core resource.

The exact diagnostic strings identify the corresponding failures as CSID stop, IFE stop and CDM stop.

Therefore the Windows ISP-internal teardown order is:

**CSID stop -> IFE stop -> CDM/remaining core stop**.

## Sensor relationship

The exact front-sensor KMD shows MIPI CSI power/open during `CameraSensorDriver_PowerOn()` before sensor init/config/crop packets are submitted. Sensor `CSLPacketOpcodesSensorStreamOn` is archived and later applied by `SensorAsyncProcessUpdate()`. The SHA-pinned sensor data itself defines stream-on as the single write `0x0100=0x01` and stream-off as `0x0100=0x00`, both with zero delay.

This proves that Windows does not require a guessed multi-register stream toggle and establishes the exact sensor control operations used below.

## Dynamic cross-driver lifecycle oracle

A corrected WinRT holder hard-selects the `Surface Camera Front` source group and refuses to start unless the chosen source itself reports `DeviceInformation.Name == Surface Camera Front`. Two independent runs both completed `MediaFrameReader.StartAsync=Success` and normal `StopAsync()`. The exact holder is archived as `windows-dynamic/E003H-WinRT-Holder.ps1` (3,809 bytes, SHA-256 `7eb5971788d89024ef85614774866ddf205ba39c2b9ded618890ee0eef7ddd75`).

The current DriverStore binaries were re-hashed immediately before capture and matched the static oracle. Same-machine Windows kernel enumeration supplied the live image bases used for relocation-proof absolute breakpoints:

- `qccamisp8380.sys` base `0xfffff802eed70000`;
- `qccammipicsi8380.sys` base `0xfffff802eb340000`;
- `surfacecamfrontsensor8380.sys` base `0xfffff802ef200000`.

The raw KD log is `windows-dynamic/E003H_LIFECYCLE_ABS_20260828.log`, 51,296 bytes, SHA-256 `2908392a619b14f229161dec616e43052103b53b161a3fc77edda56b782d1b36`. The deterministic parser `windows-dynamic/extract_lifecycle_order.py` rejects any sequence other than two identical cycles. It finds:

- cycle 1: line 22 `ISP_START_DONE`, line 25 `SENSOR_STREAM_ON_APPLY`, line 422 `ISP_STOP_DONE`, line 423 `SENSOR_STREAM_OFF_APPLY`;
- cycle 2: line 435 `ISP_START_DONE`, line 438 `SENSOR_STREAM_ON_APPLY`, line 831 `ISP_STOP_DONE`, line 832 `SENSOR_STREAM_OFF_APPLY`.

The ISP start/stop *entry* offsets are internal command-path sites and fire hundreds of times; they are intentionally excluded from top-level lifecycle acceptance. The unique completion/sensor markers are reproducible.

Therefore the cross-driver ordering is mechanically proven twice:

**ISP start complete -> sensor stream-on apply**

**ISP stop complete -> sensor stream-off apply**

Combining dynamic ordering with the static ISP-internal disassembly gives the current Windows lifecycle oracle:

**start: IFE start -> initial IFE/CSID configuration -> CSID start -> sensor `0x0100=0x01`**

**stop: CSID stop -> IFE stop -> CDM/remaining core stop -> sensor `0x0100=0x00`**

The Windows MIPI/CSIPHY driver's exact placement relative to those ISP operations is still a separate question; do not infer it from the sensor/ISP ordering alone.

## Linux mismatch to resolve

Current CAMSS `video_start_streaming()` walks upstream from video as VFE -> CSID -> CSIPHY -> sensor. VFE-before-CSID and sensor-last are consistent with the proven Windows ordering at those boundaries, but CSIPHY placement still requires same-machine evidence.

Current CAMSS `video_stop_streaming()` also walks VFE -> CSID -> CSIPHY -> sensor. Sensor-last is now proven compatible with Windows, but **VFE-before-CSID is the opposite of Windows' CSID-before-IFE/VFE stop order**. A parity candidate must fix that host ordering without inventing a sensor-off-first teardown.
