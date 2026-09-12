# E004p — IR-only native bind graph one-shot

E004p is a fresh disposable one-shot that combines:

- E004o IR-only CAMSS graph DT;
- E004l native VD55G0 Windows-state sensor driver;
- E004k scoped CAMSS CSIPHY0 D-PHY parity module;
- the in-kernel V4L2 contract/direct-stream-block harness.

The purpose is still **bind/graph validation only**, not a camera stream.

Acceptance requires:

1. native VD55G0 Windows-state initialization passes and returns to SW_STBY;
2. runtime PM suspends the sensor after bind;
3. CAMSS async notifier completes with the IR sensor as its only external endpoint;
4. the media graph reports exactly one sensor link from `sp11-vd55g0 2-0060` to `msm_csiphy0`, enabled and immutable;
5. a V4L subdevice node is registered for the sensor;
6. media format reports Y10/RAW10 644x604;
7. the kernel harness independently verifies 420 MHz link frequency, 84 MHz pixel rate, HBLANK 556, VBLANK 1351, D-PHY, one lane and 420 MHz mbus link frequency;
8. direct sensor `.s_stream(1)` returns `-EOPNOTSUPP`;
9. the E004j CSIPHY receiver-programming marker remains absent, proving CAMSS never entered receiver stream configuration;
10. no capture request, sensor stream-register write or illumination occurs;
11. immediate reboot to Golden and candidate retirement.

One attempt only. No same-boot retry.
