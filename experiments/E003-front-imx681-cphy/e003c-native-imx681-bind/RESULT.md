# E003c result — ACCEPTED

The native bind-only Sony IMX681 driver passed on SP11 X1E80100.

- Windows/platform identity: `0x0004 = 0x0aff`.
- Sony silicon identity: `0x0016 = 0x0681`.
- Driver bound natively at CCI1/master1 Linux client `3-0010`.
- Runtime PM returned to `suspended`, usage `0`.
- MCLK4, CSIPHY2 and CSIPHY2 timer enable/prepare counts returned to zero.
- LDO3_M 1.8 V and LDO7_B 2.8 V have zero enabled consumers after probe.
- GPIO237 returned physical low/reset asserted.
- No IMX681 entity/link is present in the CAMSS media graph because E003c intentionally has no front endpoint.
- A test-only kernel harness invoked the bound V4L2 subdev `s_stream(1)` callback directly; it returned `-EOPNOTSUPP` (`-95`) exactly as required.
- The production E003c driver contains no sensor write path, no mode table, and no executable MODE_SELECT/`0x0100` operation.
- Rear OV13858, Wi-Fi, FullIO playback/capture and G6 touch remained healthy; no serious kernel fault was observed.

The absence of a `/dev/v4l-subdevN` node for IMX681 is expected at this gate: `v4l2_async_register_subdev_sensor()` registers the sensor asynchronously, but without a remote endpoint no CAMSS notifier can complete the async match. E003d will add the C-PHY graph and is the first phase where the front sensor should enter `/dev/media0`.

Next: E003d C-PHY graph/receiver configuration, initially idle/no streaming.
