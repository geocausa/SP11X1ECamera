# E004q — IR-only native bind graph gate with bounded notifier wait

E004q is the fresh successor to E004p. It uses exactly the same IR-only DT, native VD55G0 sensor module and scoped CAMSS parity module.

E004p's late read-only diagnostics proved that the graph and controls were correct; its wrapper simply evaluated them before CAMSS async-notifier completion had finished. E004q changes only lifecycle timing:

- after the native sensor binds and runtime-suspends, wait up to 10 seconds;
- poll read-only for both the sensor V4L subdevice node and the immutable enabled sensor -> msm_csiphy0 media link;
- only after both exist, capture MEDIA.txt and run the same direct sensor V4L2 contract/stream-block harness.

Acceptance still requires:

- exact native Windows-state sensor initialization, 596 writes, final SW_STBY;
- runtime PM suspended, usage 0;
- one immutable enabled sensor -> msm_csiphy0 link;
- Y10_1X10 644x604 and registered subdevice node;
- 420 MHz link, 84 MHz pixel, HBLANK 556, VBLANK 1351, D-PHY one lane;
- direct sensor s_stream(1) returns -EOPNOTSUPP;
- no E004j receiver-programming marker;
- no capture, no sensor stream-register write and no illumination;
- immediate Golden return and candidate retirement.

One attempt only. No same-boot retry.
