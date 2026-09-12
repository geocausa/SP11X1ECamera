# E004r — clean typed-control IR native bind gate

E004r is the fresh successor to E004q. The camera stack, DT and notifier timing are unchanged.

E004q already proved:

- native VD55G0 Windows-state initialization;
- IR-only notifier completion;
- one immutable enabled sensor -> msm_csiphy0 link;
- Y10_1X10 644x604 sensor format;
- runtime suspend after bind;
- direct sensor s_stream(1) returns -EOPNOTSUPP;
- no CAMSS receiver programming, capture or illumination.

Its only failure was in the tiny verification harness: it incorrectly used v4l2_ctrl_g_ctrl_int64() for controls that are not INTEGER64, generating three kernel WARNs and reading zeros.

E004r changes only that harness accessor logic:

- LINK_FREQ: read integer-menu index with v4l2_ctrl_g_ctrl(), then map through qmenu_int;
- PIXEL_RATE: v4l2_ctrl_g_ctrl_int64();
- HBLANK: v4l2_ctrl_g_ctrl();
- VBLANK: v4l2_ctrl_g_ctrl().

Everything else is inherited unchanged from the proven E004q/E004o/E004l/E004k chain.

Acceptance requires a warning-free bind-only run with:

- link index 0 => 420 MHz;
- pixel rate 84 MHz;
- HBLANK 556;
- VBLANK 1351;
- D-PHY, one lane, mbus link 420 MHz;
- direct s_stream(1) == -EOPNOTSUPP;
- no E004j receiver-programming marker;
- no capture, no sensor stream-register write and no illumination;
- immediate Golden return and candidate retirement.

One attempt only. No same-boot retry.
