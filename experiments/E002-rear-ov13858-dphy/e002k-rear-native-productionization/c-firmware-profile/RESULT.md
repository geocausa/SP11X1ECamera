# E002k-C result — ACCEPTED

The rear OV13858 path now operates without any experiment-specific DT property or stream-permission gate.

## Firmware-selected native profile

The live sensor node contains no `microsoft,e002*` properties. The cleaned driver selected the Surface profile solely from standard endpoint metadata: four-lane D-PHY with one link frequency of 592.8 MHz.

Userspace exposes:

- one frame size: 4076x2806;
- LINK_FREQ: 592,800,000 Hz;
- PIXEL_RATE: 432,732,960 Hz;
- HBLANK: 412;
- VBLANK: 408.

Generic upstream mode/PLL tables remain mechanically unchanged for devices without the Surface endpoint signature.

## Deterministic integrity

OV13858 Vertical Color Bar Type 1 captured successfully at 14,321,824 bytes with SHA-256:

`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`

This is byte-for-byte identical to E002j, E002k-A and E002k-B.

## Normal stream stability

With test pattern disabled, 16/16 frames completed with sequences 0 through 15, every frame 14,321,824 bytes. Mean timestamp interval was 33.3806 ms, or 29.9575 fps.

## Power / teardown / health

Only DOVDD/LDO6_M, DVDD/LDO1_M and AVDD/LDO5_M cycled. LDO16_B/VAF had zero enable events. After streaming the sensor returned to runtime suspended with usage 0, MCLK1/CSIPHY1/timer enable counts returned to zero, Wi-Fi/audio remained healthy, and no kernel fault was logged.

## Conclusion

**E002k-C ACCEPTED.** The rear camera has graduated from experiment-gated bring-up to a normal firmware-described native Linux sensor profile. Remaining work is production integration: remove the temporary initrd/module/provider scaffolding, express the board topology cleanly in the canonical Denali DTS/kernel source, and prepare reviewable patches without regressing Golden.
