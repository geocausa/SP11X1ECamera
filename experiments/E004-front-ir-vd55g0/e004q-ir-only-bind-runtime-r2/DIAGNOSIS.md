# E004q runtime diagnosis — graph PASS, direct stream block PASS, harness accessor WARN

The single E004q attempt was consumed and was not retried.

## Camera-stack results

E004q achieved the intended bind-only integration state:

- native VD55G0 Windows-state initialization passed, 596 writes, final SW_STBY;
- sensor runtime-PM returned to suspended with usage 0;
- IR-only CAMSS notifier completed;
- sensor entity had exactly one link;
- link was sp11-vd55g0 -> msm_csiphy0 pad0, ENABLED and IMMUTABLE;
- sensor subdevice node existed;
- media format was Y10_1X10 / 644x604;
- user-space read-only controls showed:
  - link frequency 420 MHz;
  - pixel rate 84 MHz;
  - HBLANK 556;
  - VBLANK 1351;
- direct sensor s_stream(1) was called and returned -EOPNOTSUPP exactly as designed;
- no E004j CSIPHY receiver-programming marker appeared;
- no capture, no sensor stream-register write and no illumination occurred.

## Why the attempt was still marked failed

The tiny kernel harness used v4l2_ctrl_g_ctrl_int64() for all four controls.

The exact kernel V4L2 API warns unless that accessor is used on V4L2_CTRL_TYPE_INTEGER64. Only PIXEL_RATE is int64 here. LINK_FREQ is an integer-menu and HBLANK/VBLANK are ordinary integer controls.

The result was three WARN traces from v4l2_ctrl_g_ctrl_int64(), with the harness reading:

- link_freq = 0;
- pixel_rate = 84000000;
- hblank = 0;
- vblank = 0.

The media-bus contract itself was correct: D-PHY enum type 5, one lane, 420 MHz.

The user-space control dump on the same boot independently proved the actual control values were all correct. Therefore the failure is entirely a harness accessor bug, not a sensor/control/graph bug.

SP11 immediately returned to Golden and the candidate was retired.

## Next gate

Fresh E004r one-shot with identical DT, sensor and CAMSS binaries. Change only the harness:

- v4l2_ctrl_g_ctrl() for LINK_FREQ index, HBLANK and VBLANK;
- map the LINK_FREQ integer-menu index through qmenu_int;
- v4l2_ctrl_g_ctrl_int64() only for PIXEL_RATE;
- retain the same D-PHY bus checks and direct s_stream(1) == -EOPNOTSUPP requirement.
