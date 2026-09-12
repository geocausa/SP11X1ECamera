# E004s — adapter-independent IR native bind gate

E004s is the fresh successor to E004r.

E004r never started a camera attempt: its preflight assumed the physical VD55G0 client would always be named `2-0060`, but on that disposable boot Linux enumerated the same DT device as `3-0060`. No sensor/CAMSS module was loaded and no sensor write occurred.

E004s removes I2C adapter numbering from the device identity everywhere.

Shell discovery requires exactly one I2C device that simultaneously has:

- address suffix `-0060`;
- OF compatible `microsoft,sp11-vd55g0`.

The discovered sysfs path and generated client name are recorded in `RUNTIME-PREFLIGHT.txt` and carried unchanged through binding, runtime-PM checks, media-entity matching and acceptance parsing.

The kernel harness independently performs the same identity resolution:

1. `of_find_compatible_node(..., "microsoft,sp11-vd55g0")`;
2. `bus_find_device_by_of_node(&i2c_bus_type, np)`;
3. require `client->addr == 0x60`.

It then performs the already-correct typed V4L2 control checks and direct stream refusal test.

No literal `2-0060` or `3-0060` is permitted anywhere in the E004s package.

All camera behavior remains unchanged from the already-proven chain:

- E004o IR-only graph;
- E004l exact 596-write Windows-state native sensor;
- E004k scoped CAMSS module;
- bounded notifier wait;
- one immutable enabled link to CSIPHY0;
- 420 MHz link / 84 MHz pixel / HBLANK 556 / VBLANK 1351;
- D-PHY one lane;
- direct `s_stream(1) == -EOPNOTSUPP`;
- zero CAMSS receiver programming, capture and illumination.

One attempt only. No same-boot retry.

## Runtime outcome

The single E004s attempt passed completely.

The shell preflight dynamically identified the physical sensor by compatible + address and recorded client `2-0060` for this boot. The kernel harness independently resolved the same OF node on the I2C bus and matched the same generated client name. The adapter number itself is not part of the authority and remains intentionally unpinned.

The native sensor reached the exact already-proven Windows state with 596 sensor-data writes and returned to runtime suspend. CAMSS notifier completion produced one enabled+immutable link from the sensor to `msm_csiphy0`, with a registered subdevice and Y10 644x604 format.

The typed in-kernel V4L2 checks passed: 420 MHz link frequency, 84 MHz pixel rate, HBLANK 556, VBLANK 1351, D-PHY one lane and 420 MHz mbus link. Direct `.s_stream(1)` returned `-EOPNOTSUPP` as designed.

There were no kernel warnings or faults, no E004j receiver-programming marker, no capture request and no illumination. SP11 returned immediately to Golden and the disposable candidate was retired.

This closes the native VD55G0 bind/graph/control stage. The next gate can move to bounded CSIPHY0 receiver programming while keeping sensor streaming and illumination disabled.
