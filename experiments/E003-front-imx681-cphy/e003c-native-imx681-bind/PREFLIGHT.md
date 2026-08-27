# E003c — native IMX681 V4L2 bind only

Goal: replace the E003b probe shim with a real `sony,imx681` V4L2 sensor subdevice while preserving a hard no-stream boundary.

## Hardware facts

All SP11 X1E electrical facts come from the same-machine Windows oracle and accepted E003b:

- CCI1/master1, 400 kHz, address `0x10`;
- GPIO235/236 AON CCI pair;
- GPIO100 MCLK4/cam_aon at 19.2 MHz;
- GPIO237 active-low reset;
- LDO3_M/dovdd 1.8 V then LDO7_B/avdd 2.8 V;
- Windows identity `0x0004 -> 0x0aff`.

E003c additionally requires the public Sony-style identity `0x0016 -> 0x0681` used by existing open IMX681 Linux drivers.

## Safety boundary

- no front CAMSS port or endpoint;
- no `remote-endpoint`;
- no C-PHY configuration;
- no sensor mode register table in the driver;
- no write to `0x0100` exists in the driver;
- `.s_stream(1)` always returns `-EOPNOTSUPP` before any runtime-PM or I2C write;
- modes 0..4 are metadata only; special mode 5 remains deferred.

The candidate must bind, identify, register the V4L2 subdevice, then runtime-suspend back to reset-low / rails-off / MCLK4-off.
