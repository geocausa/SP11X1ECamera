# E002j result — ACCEPTED

The exact accepted E002h-r1 binaries were reused with no code or DT change. The only experiment variable was the standard OV13858 `V4L2_CID_TEST_PATTERN` control.

## Runtime

Controls before stream:

- exposure 1600;
- analogue gain 128;
- digital gain 1024;
- VBLANK 408;
- test pattern `1` = `Vertical Color Bar Type 1`.

One 4076x2806 packed-GRBG10 frame dequeued normally, sequence 0, `bytesused=14321824`, capture rc 0. RAW SHA-256:

`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`

## Optics-independent integrity proof

Packed RAW10 decoded to exactly 11,437,256 pixels. The entire image contains only two digital levels:

- 64: 5,763,524 pixels;
- 1023: 5,673,732 pixels.

Every one of the 1,403 even rows is bit-identical to every other even row, and every one of the 1,403 odd rows is bit-identical to every other odd row. Bayer-channel transition positions form deterministic vertical bars; the y1x1 channel has seven transitions at x=487,999,1511,2023,2535,3047,3559 and alternates exactly 1023/64.

This is the expected signature of an internally generated vertical color-bar pattern, independent of lens, illumination, exposure response or scene content. It proves the RAW10 packing/stride decode and the sensor -> CSIPHY1 -> CSID0 -> VFE0 RDI0 -> userspace ordering are coherent.

## Teardown

After capture:

- `test_pattern` restored to 0 / Disabled;
- exposure/gains/VBLANK restored/retained at defaults;
- sensor runtime PM `suspended`, usage 0;
- MCLK1 enable count 0;
- CSIPHY1 enable count 0;
- CSI1 timer enable count 0;
- no kernel Oops/BUG;
- Wi-Fi, ALSA playback and ALSA capture healthy.

The raw frame remains local-only; only its hash and derived statistics are committed.

**E002j sensor-generated RAW10 integrity gate: ACCEPTED.**
