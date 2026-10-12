# C-PHY rate contract audit, 2026-10-12

The published CAMSS C-PHY RESEND v9 patch8 uses multiplier16*bpp and
divisor2*trios*7 for the V4L2 pixel-rate fallback. Executing the unchanged
pinned kernel `v4l2_get_link_freq_ctrl()` shows that this differs from the
inverse of the documented bus equation:

```
bus_pixel_rate = link_frequency * 2 * trios * 16 / (7 * bpp)
link_frequency = bus_pixel_rate * bpp * 7 / (32 * trios)
symbol_rate = 2 * link_frequency
```

The proposal's fallback is approximately256/49 times the inverse documented
value, before integer rounding. This is a source calculation discrepancy,
not an observed SP11 transport failure. An explicit link-frequency control
bypasses the fallback. The existing IMX681 driver reports1.2GHz through
get_mbus_config for its2.4Gsymbol/s link, so this audit does not establish an
error in its currently reported frequency or change installed behavior.

The pixel-array rate from V4L2_CID_PIXEL_RATE is also not necessarily the bus
pixel rate. The forthcoming C-PHY path should obtain an explicit sensor link
frequency through get_mbus_config or V4L2_CID_LINK_FREQ and reject an absent
explicit value (`v4l2_get_link_freq(sensor_pad, 0, 0)`). Do not silently
estimate C-PHY timing from the sensor pixel-array rate. Keep link frequency
and symbol rate distinct, check overflow before doubling, and validate the
typed C-PHY options against the board routing before MMIO.

```sh
python3 -B tools/test-upstream-cphy-rate.py --kernel-source /path/to/pinned-source
```

GCC and Clang with ASAN/UBSAN each reproduce75 C-PHY proposal discrepancies,
pass100 D-PHY arithmetic controls,3 explicit-frequency controls and4 error
controls. The actual kernel function is extracted unchanged from a hash-pinned
GPL source file; only control lookup/menu and warning primitives are modeled.
This does not test a live media graph, concurrent control changes or hardware.

References:
- [Kernel transmitter/receiver bus-rate equation](https://docs.kernel.org/driver-api/media/tx-rx.html#pixel-rate)
- [V4L2 link-frequency units](https://docs.kernel.org/userspace-api/media/v4l/ext-ctrls-image-process.html)
- [Original RESEND v9 patch8 and discussion](https://patchew.org/linux/20260729-qcom-cphy-v9-0-1f8d9fdab037@ixit.cz/20260729-qcom-cphy-v9-8-1f8d9fdab037@ixit.cz/)

The original patch remains byte-pinned for attribution and reproduction; it
has not been applied to candidate16. The GPL Qualcomm CSIPHY2.1.2 header is
also reverified at an immutable public revision in
`cphy-rate-reference-20261012/public-cphy-source.json`. This is a source
reference, not a runtime table selection or generic C-PHY API implementation.
Do not copy private Windows tuning/deltas into the new standalone driver.
