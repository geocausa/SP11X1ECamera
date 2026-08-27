# Windows rear-camera KD oracle — 2026-08-27

Clean-room derived notes only. No Microsoft/Qualcomm binary or memory dump is committed.

## Live PnP identity

On this SP11 Windows installation:

- rear instance: `ACPI\\VEN_OVTI&DEV_D858&SUBSYS_MSHW0491&REV_0000\\15`
- rear service: `CameraRearSensor`
- rear device stack: `ACPI -> CameraRearSensor -> ksthunk`
- camera platform service: `qcCameraPlatform` (`QCOM0C32`)
- MIPI CSI service: `qcCameraMipiCsi`
- ISP service: `qcISP`

The rear KMDF mini-driver image remained resident even though normal `lm` enumeration did not name it. Its live PE image was found at `fffff800d89c0000`, size `0x42000`, timestamp 2025-04-25 20:40:23, with embedded CodeView path ending in `surfacecamrearsensor8380.pdb`.

The live image contains the diagnostic text `CameraSensorDriver_ProbeImageSensor() Sensor probing succeed:0xd855`, independently corroborating the sensor-module configuration's expected ID.

A partial live memory image was used locally on SP7 for analysis and remains outside Git.

## Exact static probe tuple

`tools/qti_sensor_summary.py` on the exact installed `com.surface.sensormodule.rfc_ov13858.bin` decodes:

- QTI 8-bit slave address: `0x20`
- Linux 7-bit slave address: `0x10`
- register-address type: 16-bit
- register-data type: 16-bit
- ID register: `0x300b`
- expected ID: `0xd855`
- I2C/CCI mode: `FAST` = 400 kHz

The independently reversed platform routing descriptor maps the rear slot to packed I2C master 1. `qccamplatform8380.sys` splits that index as controller `index / 2`, master `index % 2`, giving **CCI0/master1**. The same descriptor maps rear receive to **CSIPHY1**.

## Consequence for E002b

r3e already used the correct CCI0/master1, 400 kHz, Linux address `0x10`, Windows-derived rails, GPIO110 reset sequence and 19.2 MHz MCLK1. Its remaining known mismatch was the generic/upstream-style identity transaction: three bytes from `0x300a` expecting `0x00d855`.

r3f changes only that transaction to the Windows-exact 16-bit read at `0x300b` expecting `0xd855`.
