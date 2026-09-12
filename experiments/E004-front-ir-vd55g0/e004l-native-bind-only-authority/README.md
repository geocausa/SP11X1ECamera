# E004l — native VD55G0 bind-only Windows-state integration

Status: **offline build authority only; no runtime yet.**

E004l converts the already-proven E004i sensor initialization into a native V4L2 subdevice while deliberately keeping sensor streaming impossible.

The driver:

- powers the physical CUT1 sensor with the proven Surface sequence;
- requires model 0x3047 / revision 0x1111 before writes;
- mechanically regenerates the exact 552-byte Surface Windows patch;
- replays the exact patch/setup/boot poll lifecycle;
- requires post-boot GPIO1 selector 0x0468 to already equal Windows value 0x02 and never writes that register;
- writes the remaining exact Windows safe-42 final configuration;
- requires full Windows-state readback: 19.2 MHz ext clock, 840 Mbps sensor MIPI rate, line 1200, frame 1955, ROI 644x604, GPIO 01/02/01/01;
- exposes one fixed V4L2 mode: monochrome RAW10 `MEDIA_BUS_FMT_Y10_1X10`, 644x604;
- exposes fixed link frequency 420 MHz and pixel rate 84 MHz;
- reports a fixed D-PHY bus contract of one data lane at 420 MHz;
- returns `-EOPNOTSUPP` for every stream-on request.

The DT is the proven E004h tree with exactly one property changed: the IR sensor compatible becomes `microsoft,sp11-vd55g0`. Its sensor endpoint remains 420 MHz / one lane, while CAMSS CSIPHY0 remains D-PHY receiver lane position 0.

No illumination API exists in this driver and no stream register write is present.
