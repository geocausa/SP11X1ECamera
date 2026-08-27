# E002g result — ACCEPTED

Strict one-shot E002g boot passed.

## Native V4L2 mode semantics

Read-only sensor-subdev ioctls report exactly:

- one frame size: `4076x2806` RAW10;
- `LINK_FREQ = 592800000` Hz;
- `PIXEL_RATE = 432732960` Hz;
- `HBLANK = 412`;
- `VBLANK = 408`.

These values form exactly 30 fps at the sensor pixel array:

`432732960 / ((4076 + 412) * (2806 + 408)) = 30`.

CSI transport remains independently represented by 592.8 MHz link frequency / 474.24 Mpixel/s RAW10 four-lane throughput.

## Hardware invariants

The automatic boot sequence also reproduced all accepted predecessor gates:

- E002e four-lane D-PHY/592.8 MHz endpoint validation PASS;
- E002c native OV13858 identity PASS;
- E002f Surface mode0 standby programming/readback PASS;
- GPIO97/MCLK1 routing unchanged;
- sensor runtime PM `suspended`, usage 0 after probe;
- MCLK1, CSIPHY1 and CSI1 timer clocks at enable count 0;
- Wi-Fi, playback and capture healthy;
- Golden remains saved GRUB default and the one-shot entry was consumed.

No stream or format-setting ioctl was issued.

## Windows 207-register oracle decision

Offline comparison proved the clean E002f/E002g reconstruction covers all 207 Windows mode-0 register addresses with identical Windows-covered final values after final VTS. The only extra Linux write is `0x4503=0`, explicit test-pattern disabled. Therefore the proprietary table remains a local oracle rather than shipped driver data.

**E002g native Surface rear mode semantics gate: ACCEPTED.**

Next: E002h first controlled transport activation. Before allowing `MODE_SELECT=1`, validate CAMSS CSIPHY1/CSID/VFE routing, receiver link-frequency use and an explicit rollback/timeout capture path. Start with the smallest one-frame/short-buffer experiment possible.
