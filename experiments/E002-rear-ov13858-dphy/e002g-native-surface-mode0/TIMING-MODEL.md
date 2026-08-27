# E002g — native Surface rear timing model

## Two clocks, two meanings

The QTI sensor schema distinguishes the sensor timing clock from MIPI output throughput. The installed Surface mode-0 metadata reports:

- output: 4076 x 2806;
- line-length register/QTI value: 1122 (`0x0462`);
- frame length: 3214;
- frame rate: 30 fps;
- MIPI/output pixel throughput: 474,240,000 pixels/s;
- four-lane RAW10 D-PHY;
- link frequency: 592,800,000 Hz.

Linux's existing OV13858 driver already establishes that register `0x0462` corresponds to **4488 pixel clocks per line** (`OV13858_PPL_540MHZ = 4488`), i.e. this sensor's line-length register is in quarter-pixel-clock units for V4L2 timing purposes.

Therefore the Surface pixel-array VT rate is:

```
4488 * 3214 * 30 = 432,732,960 pixels/s
```

and the native V4L2 timing controls are:

- HBLANK = 4488 - 4076 = **412**;
- VBLANK = 3214 - 2806 = **408**;
- PIXEL_RATE = **432,732,960 Hz**;
- LINK_FREQ = **592,800,000 Hz**.

These are intentionally not the same clock. The CSI bus throughput remains 474.24 Mpixel/s because:

```
592.8 MHz * 2 * 4 lanes / 10 bits = 474.24 Mpixel/s
```

Public semantics cross-check:

- Linux V4L2 `V4L2_CID_PIXEL_RATE` is the pixel-array sampling rate; current documentation: https://docs.kernel.org/userspace-api/media/v4l/ext-ctrls-image-process.html
- Linux CSI transmitter documentation distinguishes bus/link rate from pixel-array rate: https://cdn.kernel.org/doc/html/latest/driver-api/media/tx-rx.html
- Qualcomm/Thundercomm sensor bring-up documentation distinguishes `lineLengthPixelClock`, `frameLengthLines` and `outputPixelClock` and warns that output pixel clock is a receiver/transport sizing value.

## E002g scope

E002g exposes this mode/control model only. The existing `microsoft,e002e-no-stream` guard remains before runtime PM, so no stream transition or CSIPHY power is possible in this gate.
