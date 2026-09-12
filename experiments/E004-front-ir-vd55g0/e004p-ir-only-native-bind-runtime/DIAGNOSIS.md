# E004p runtime diagnosis — IR-only graph PASS, acceptance scan raced notifier completion

The single E004p attempt was consumed and was not retried.

The native VD55G0 Windows-state initialization again passed completely and the sensor returned to runtime suspend. The E004k CAMSS parity parameter was armed and no receiver programming occurred.

The runtime wrapper failed because it scanned for the media graph immediately after the sensor entered runtime suspend. At that instant no matching media artifact had yet been captured, so the bounded attempt was marked failed and the direct stream-block harness was not run.

Read-only diagnostics taken shortly afterward on the same boot showed that CAMSS notifier completion had succeeded:

- /dev/media0 present;
- /dev/v4l-subdev25 registered for sp11-vd55g0 2-0060;
- sensor entity: 1 pad, 1 link, 0 routes;
- exact external link: sp11-vd55g0 -> msm_csiphy0 pad0, ENABLED and IMMUTABLE;
- format: Y10_1X10 / 644x604;
- controls: link frequency 420 MHz, pixel rate 84 MHz, HBLANK 556, VBLANK 1351;
- sensor runtime status suspended, usage 0;
- E004k CAMSS parameter Y;
- no E004J_CSIPHY0_DPHY_WINDOWS_PARITY marker, so receiver stream programming never ran.

Therefore the E004o IR-only graph fix is proven correct. E004p failed only because its graph-discovery timing gate was too eager.

No direct s_stream callback, capture stream or illumination occurred. SP11 returned to Golden and the candidate was retired.

Next gate: fresh E004q one-shot with identical DT/modules but a bounded read-only wait for notifier completion/subdev registration before graph acceptance and the direct -EOPNOTSUPP stream-block harness.
