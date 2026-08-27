# E003e fixed C-PHY transport metadata

The exact SP11 Windows/QTI mode0 table programs PLL2 as:

- external clock: 19.2 MHz;
- pre-divider register `0x030d = 3`;
- multiplier registers `0x030e:0x030f = 0x0177 = 375`;
- resulting C-PHY operating symbol rate: `19.2 MHz * 375 / 3 = 2.400 GHz`.

The local kernel documentation (`Documentation/driver-api/media/tx-rx.rst`) states that fixed-link transmitters should report link frequency through `.get_mbus_config()` and gives the CSI-2 bus pixel-rate relation:

`bus_pixel_rate = link_freq * 2 * nr_of_lanes * 16 / k / bits_per_sample`, with `k=7` for C-PHY.

For one trio and RAW10, `link_freq = 1.200 GHz` gives `548.571428 Mpixel/s`, matching the QTI mode0 output-pixel-clock value `548.570000 MHz` to its published precision. Therefore E003e reports:

- bus type: CSI-2 C-PHY;
- one trio at physical position 0;
- line order ABC;
- fixed V4L2 `link_freq = 1,200,000,000 Hz` through `.get_mbus_config()`;
- sensor remains software-standby and streaming remains blocked.

This explicit fixed link frequency is returned before `v4l2_get_link_freq()` would use any pixel-rate fallback. E003e therefore does not rely on the current Qualcomm v9 C-PHY fallback arithmetic in `camss_get_link_freq()`.
