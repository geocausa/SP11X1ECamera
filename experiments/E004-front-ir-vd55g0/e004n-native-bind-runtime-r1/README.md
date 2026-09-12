# E004n — corrected native VD55G0 bind-only one-shot

E004n is a fresh one-shot after the safely aborted E004m attempt. E004m is not retried.

The only package-level defect exposed by E004m was an unprivileged read of the E004k CAMSS module parameter, whose sysfs mode is 0400. E004n reads that parameter through `sudo -n cat`.

E004n also hardens acceptance by moving the V4L2 contract checks into the tiny kernel harness. Before calling the sensor's deliberately blocked `.s_stream(1)`, the harness requires:

- link frequency = 420,000,000 Hz;
- pixel rate = 84,000,000 Hz;
- HBLANK = 556;
- VBLANK = 1351;
- media-bus type = `V4L2_MBUS_CSI2_DPHY`;
- one active data lane;
- media-bus link frequency = 420,000,000 Hz.

The user-space graph inspection remains read-only. No video-node stream command exists in this package.

Acceptance still requires the native sensor to return to runtime suspend, the direct sensor stream callback to return `-EOPNOTSUPP`, and the E004j CSIPHY receiver-programming marker to remain absent. Thus E004n is a native bind/graph/control test only: no receiver stream configuration, sensor stream-register write, capture, or illumination.
