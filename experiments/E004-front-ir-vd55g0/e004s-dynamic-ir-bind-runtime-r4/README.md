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
