# E001 static oracle — sensor probe and lifecycle map

Evidence: exact local `com.surface.sensormodule.*.bin` files, QTI Parameter Parser v3.4.0. Parsed read-only by `tools/qti_parameter_bin.py` / `tools/qti_sensor_summary.py`.

| Camera | Sensor | Windows 8-bit address | Linux 7-bit | ID register | Expected ID | I2C mode |
|---|---|---:|---:|---:|---:|---|
| Front RGB | IMX681 | `0x20` | `0x10` | `0x0004` | `0x0aff` | FAST |
| Rear RGB | OV13858 | `0x20` | `0x10` | `0x300b` | `0xd855` | FAST |
| Front IR | VD55G0 | `0xc0` | `0x60` | `0x0000` | `0x3047` | FAST |

Qualcomm's camera schema uses the Windows/QTI sensor slave field as the 8-bit wire-format address; Linux uses the 7-bit address. `FAST` corresponds to the normal 400 kHz QTI camera I2C/CCI mode.

## Stream lifecycle

### IMX681
- stream on: `0x0100 <- 0x01`
- stream off: `0x0100 <- 0x00`
- group hold: `0x0104 <- 0x01`; release `0x0104 <- 0x00`

### OV13858
- stream on: `0x0100 <- 0x01`
- stream off: `0x0100 <- 0x00`
- group hold on: `0x3208 <- 0x00`
- group hold release: `0x3208 <- 0x10`, then `0xa0`
- module advertises actuator `dw9800` and EEPROM `st_m24c64`

### VD55G0
- stream-on package contains a four-step write/poll/wait lifecycle involving `0x0201`, `0x0020`, and `0x002c`; operation type 4 must not be flattened into blind writes before its semantics are dynamically validated.
- stream off: `0x0202 <- 0x01`
- group hold: `0x0448 <- 0x01`; release `0x0448 <- 0x00`

## Camera slot evidence
The QTI `CameraModuleConfig` schema defines `CameraId` as the slot number and places it first. The local module-configuration records begin with slot values that map consistently as:
- rear OV13858: camera ID 0
- IR VD55G0: camera ID 1
- front IMX681: camera ID 2

Treat this slot mapping as high-confidence static evidence; host CCI/CSIPHY assignment still requires platform/dynamic confirmation.
