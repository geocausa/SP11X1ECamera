# E002j — sensor test-pattern integrity

Status: PREPARED / NOT YET RUN

## Question

Does the native rear pipeline preserve a sensor-generated OV13858 RAW10 test pattern coherently from silicon through CSIPHY1 -> CSID0 -> VFE0 RDI0 -> `/dev/video0`?

## Fixed implementation

E002j changes **no code or DT**. It reuses the exact accepted E002h-r1 payload:

- kernel SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- initrd SHA-256: `5dae9dcdb1efc4c8c3addf3655b2261e9400c1ada90cb02d8ee5620965ee36a8`
- DTB SHA-256: `f5d6e3dfd41354d155bd620f7fb13e45e63444484218a2720edc1384eb5b8a9b`
- OV13858 module SHA-256: `95e312c78cbd3d48f199a6e06c0816b76054e41946f7d491d55765b248dab153`

Native mode/transport remain 4076x2806 SGRBG10, 592.8 MHz link, 432732960 Hz VT pixel rate, CSIPHY1 -> CSID0 -> VFE0 RDI0.

## Single variable

Use the standard V4L2 control only:

- exposure = 1600
- analogue gain = 128
- digital gain = 1024
- VBLANK = 408
- test pattern = `1` (`Vertical Color Bar Type 1`)

Capture exactly one local-only RAW10 frame. Then restore test pattern to Disabled (`0`).

## Acceptance

1. one complete 14,321,824-byte frame dequeues normally;
2. packed RAW10 decodes to 11,437,256 pixels;
3. image statistics show deterministic vertical-band structure: strong column-domain transitions, high row-to-row agreement, and substantially lower within-band variance than between-band variance;
4. test pattern is restored to 0;
5. sensor runtime PM returns suspended/usage 0;
6. MCLK1, CSIPHY1 and CSI1 timer clocks return to enable count 0;
7. no new kernel fault and normal Wi-Fi/audio health remain intact.

The RAW frame stays local only. Commit only its hash and derived statistics.
