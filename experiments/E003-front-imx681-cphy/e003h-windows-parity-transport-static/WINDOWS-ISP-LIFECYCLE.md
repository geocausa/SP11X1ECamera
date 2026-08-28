# Same-machine Windows ISP lifecycle — static oracle

Date: 2026-08-28

This is static evidence from the exact Windows camera binaries installed for this SP11. No external implementation is treated as behavioral evidence.

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

This proves that Windows does not require a guessed multi-register stream toggle and strongly supports a receiver/host-ready-before-transmitter architecture. The exact cross-driver scheduling point of sensor `0x0100=1` relative to ISP DEVICE_START is **not yet mechanically proven**, so E003h must not permit Linux sensor transmission yet.

## Linux mismatch to resolve

Current CAMSS `video_start_streaming()` walks upstream from video and calls `s_stream(1)` as VFE -> CSID -> CSIPHY -> sensor. The broad direction is compatible with host/receiver before sensor, but exact parity is not established.

Current CAMSS `video_stop_streaming()` calls `s_stream(0)` in the same VFE -> CSID -> CSIPHY -> sensor direction. That does **not** match the mechanically proven Windows ISP-internal order CSID -> IFE. A parity candidate must resolve this before runtime acceptance.
