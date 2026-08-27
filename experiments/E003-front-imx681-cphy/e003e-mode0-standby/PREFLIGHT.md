# E003e preflight — IMX681 Windows mode0 standby

Purpose: cross the sensor-register boundary without crossing the transport boundary.

Hard runtime boundary:

- exact same-machine Windows/QTI sensor package SHA-256 is verified by the extractor;
- write the 364-register Windows init table followed by the 68-register Windows mode0 table;
- require software standby before and after programming;
- `MODE_SELECT` (`0x0100`) is structurally absent from both generated write arrays;
- group-hold and orientation writes are absent;
- mode0 only: 3840x2640, RAW10, C-PHY, one trio;
- fixed link metadata is returned as 1.2 GHz through `.get_mbus_config()`;
- `.s_stream(1)` remains hard-blocked with `-EOPNOTSUPP`;
- no CSIPHY stream/power request is permitted;
- MCLK4/front rails/reset must return to idle after probe/runtime-PM;
- rear camera, Wi-Fi, FullIO audio and G6 touch must remain healthy;
- one-shot boot only; saved Golden must remain untouched.
