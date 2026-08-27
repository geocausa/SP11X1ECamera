# E002c-r1 result — ACCEPTED

## Result

**PASS automatically from initrd with no manual module insertion.**

The packaging-only r1 correction fixed r0 exactly as predicted. During init-top:

1. the accepted SP11 camera RPMh provider loaded and bound;
2. `mc`, `videodev`, `v4l2_async` and `v4l2_fwnode` loaded in dependency order;
3. the patched native `ov13858` module loaded;
4. the native driver powered the sensor using the accepted Windows-derived D0 sequence;
5. the unchanged upstream 24-bit identity read succeeded;
6. dmesg logged `SP11 E002c PASS: native OV13858 identity verified`;
7. the driver disabled all four rails and MCLK in the accepted reverse sequence;
8. the I2C client remained bound to `/sys/bus/i2c/drivers/ov13858` in runtime-suspended state.

## Loaded native driver identity

`/sys/module/ov13858/srcversion`:

`02C96088AA5798CD5A70BFE`

This is the E002c patched build. The installed stock module reports `37BA92DF5373E083134987D`, so the runtime module identity is mechanically distinguishable and proven.

## Electrical idle after native bind

- runtime PM: `suspended`;
- runtime usage: `0`;
- MCLK1 source/branch enable count: `0`;
- MCLK1 retained rate: 19.2 MHz;
- GPIO110 physical low / reset asserted;
- GPIO97 remains accepted pinctrl `0x00000244` (`cam_mclk`, 4 mA, no pull, output) while the native client is bound;
- all provider rail logs show disable after the successful identity cycle.

## No transport contamination

The rear sensor DT node contains no `port`, `ports` or `endpoint`. E002c therefore introduced no CSIPHY graph and invoked no stream operation. CAMSS's existing infrastructure nodes remained present independently.

## System health

- Wi-Fi up;
- `MultiMedia1 Playback` present;
- `MultiMedia3 Capture` present;
- Golden remains `saved_entry=sp11-audio-fullio-v19c`;
- one-shot `next_entry` consumed;
- payload hashes exactly match r1 preflight.

## Conclusion

**E002c native OV13858 driver ownership/bind/identity gate: ACCEPTED.**

We have now independently proven:

1. physical SP11 rear power/CCI/MCLK/reset path;
2. native Linux OV13858 driver ownership of that path;
3. native sensor identity and runtime-PM teardown.

Next gate is E002d: add only the rear sensor <-> CAMSS **CSIPHY1 four-lane D-PHY media graph** and prove async graph binding/enumeration without starting a stream. Windows-derived first-mode/link-rate programming remains a later stream gate.
