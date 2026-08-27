# E002f result — ACCEPTED

## Result

**PASS.** The real rear OV13858 accepted the clean-room Surface mode-0 sensor configuration while remaining in standby for the entire validation.

Automatic probe sequence produced all earlier gates plus:

`SP11 E002f PASS: Surface mode0 standby 4076x2806, VTS 3214, PLL 592.8 MHz profile`

The validator mechanically read back before power-down:

- MODE_SELECT = 0 (standby);
- PLL `0x0300=0x05`, `0x0301=0x00`, `0x0302=0xf7`;
- output width 4076 (`0x3808/09=0x0fec`);
- output height 2806 (`0x380a/0b=0x0af6`);
- line-length register 1122 (`0x380c/0d=0x0462`);
- static mode VTS 3208 (`0x380e/0f=0x0c88`);
- MIPI timing `0x4837=0x0d`;
- after the QTI frame-length control-stage write, VTS = 3214 (`0x0c8e`);
- final MODE_SELECT = 0.

No MODE_SELECT=1 write exists in the E002f validator.

## Composition / clean-room isolation

E002f did not copy the 207-entry vendor table. It composed:

1. 12 Windows-derived Surface PLL register/value facts;
2. the byte-identical upstream full-resolution common register table;
3. 24 Windows-derived Surface mode-0 override register/value facts.

All pre-existing upstream PLL and mode arrays remain byte-identical to E002e.

## Receiver remained idle

After the sensor standby validation and normal reverse teardown:

- runtime PM `suspended`, usage 0;
- GPIO97 `0x244` retained, MCLK enable count 0;
- GPIO110 reset asserted low;
- CSIPHY1 enable count 0;
- CSI1 PHY timer enable count 0;
- E002e LINK_FREQ remains 592800000;
- E002e PIXEL_RATE remains 474240000;
- E002d immutable enabled OV13858 -> CSIPHY1 media link remains present.

Wi-Fi, playback and capture remained healthy.

Payload hashes:

- kernel `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`;
- initrd `b23b757b390da6c906b72812552f5e2c249a0f7e85580e7a2d7492cb7a142d27`;
- DTB `b669db40f44a108560aeca23e9f0d52b312246452d0771c93daf8765fc8d0692`;
- E002f module `d70cd7708ceeca024de65582950e3d7b4a8beaae3b085fa0dead728a1cdbb6ae`, srcversion `231AFB553F518F668097FEB`.

Two GRUB-generator substitution mistakes (stale E002e marker/path) were detected by pre-boot audits and corrected before the one-shot was armed; neither incorrect generator was booted.

**E002f Surface mode-0 standby-programming gate: ACCEPTED.**

Next: resolve the exact V4L2 timing semantics for the Surface 30-fps mode (QTI line-length unit vs link-derived pixel-rate) before exposing 4076x2806 as a normal supported mode. No streaming yet.
