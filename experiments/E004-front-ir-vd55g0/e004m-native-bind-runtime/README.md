# E004m — one-shot native VD55G0 bind-only runtime

E004m is the first native V4L2 integration run for the SP11 front IR sensor, but it is **not** a camera-stream experiment.

The one-shot candidate uses:

- E004l native VD55G0 DTB and sensor module;
- E004k exact CAMSS module with `e004j_ir_dphy_windows_parity=1` armed;
- Golden kernel/initrd;
- all camera drivers blacklisted at boot so the pinned modules are loaded manually.

Acceptance requires:

1. exact CUT1 Windows-state initialization succeeds and returns to SW_STBY;
2. sensor runtime-PM returns to suspended after native bind;
3. the media graph contains `sp11-vd55g0 2-0060` linked to `msm_csiphy0`;
4. sensor format is Y10/RAW10 644x604;
5. controls expose 420 MHz link frequency and 84 MHz pixel rate, with Windows line/frame blanking;
6. a tiny kernel harness directly calls only the sensor subdevice `.s_stream(1)` and receives `-EOPNOTSUPP`;
7. the E004j CSIPHY programming marker is **absent**, proving CAMSS never entered receiver stream configuration;
8. no video capture request, sensor stream-register write, or illumination occurs;
9. reboot immediately to Golden and retire the candidate.

One attempt only. No same-boot retry.
