# E004n runtime diagnosis — native sensor PASS, CAMSS notifier incomplete

The single E004n attempt was consumed and was not retried.

## What passed

The native clean-room VD55G0 driver ran its full same-machine Windows-state initialization successfully:

- VDDIO 1.8 V, VCORE 1.152 V, VANA 2.8 V;
- model 0x3047 / revision 0x1111 CUT1 before writes;
- exact 552-byte Surface patch;
- exact Windows patch-setup / boot polling;
- post-boot 0x0468 already 0x02, with no write to that register;
- 42 remaining Windows final-state writes;
- exact final readback;
- exactly 596 sensor-data writes;
- final SW_STBY;
- no stream;
- no illumination.

The native driver then powered the sensor off through runtime PM and remained bound at I2C 2-0060 with runtime status suspended and usage count 0.

The exact pinned E004k CAMSS module was loaded with e004j_ir_dphy_windows_parity=Y.

## Why the graph gate failed

MEDIA.txt proves that CAMSS registered sp11-vd55g0 2-0060 as a sensor entity but it had 0 links:

entity 387: sp11-vd55g0 2-0060 (1 pad, 0 link, 0 routes)

The same media device contained msm_csiphy0, but there was no sensor -> CSIPHY0 link and no V4L subdevice nodes.

This matches the exact CAMSS source:

- notifier .bound only assigns the matched sensor's host_priv to its CSIPHY;
- external sensor -> CSIPHY links are created in notifier .complete;
- .complete also calls v4l2_device_register_subdev_nodes().

The E004l DT still contains CAMSS ports for IR, rear RGB and front RGB. E004n deliberately blacklisted rear/front sensor drivers, so CAMSS was still waiting for those async endpoints and .complete could not run.

This is a graph-isolation issue, not a VD55G0 sensor-programming issue.

## Safety

Because graph acceptance failed before the direct harness stage:

- the direct s_stream(1) harness did not run;
- E004j receiver programming did not run;
- no CAMSS stream configuration occurred;
- no sensor stream-register write occurred;
- no capture request occurred;
- no illumination occurred;
- no serious kernel fault occurred.

SP11 immediately returned to protected Golden and the E004n candidate was retired.

## Next gate

Build a fresh IR-only CAMSS graph DT derived from E004l by removing CAMSS port@1 (rear) and port@2 (front RGB), plus the corresponding disposable RGB sensor graph nodes/endpoints so no dangling remote references remain. Keep Golden and accepted rear/front work untouched.

With only the IR external endpoint advertised to CAMSS, the IR native bind should be sufficient to complete the notifier, create the immutable sensor -> msm_csiphy0 link and register subdevice nodes. Then rerun the same bind-only direct-stream-block gate in a new one-shot.
