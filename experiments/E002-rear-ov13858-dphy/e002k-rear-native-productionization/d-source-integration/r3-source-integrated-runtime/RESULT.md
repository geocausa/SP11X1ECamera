# E002k-D-R3 result — ACCEPTED: source-integrated production rear camera

## Result

**PASS.** The maintained-source camera integration was booted one-shot on the exact Golden v19c Image and Golden module environment, with only the reconciled production DTB and production OV13858 module supplied by the isolated R3 initrd.

Runtime proved:

- exact R3 boot marker with Golden saved default preserved and `next_entry` consumed;
- native stock `qcom-rpmh-regulator` PM8010-M provider;
- production OV13858 loaded from R3 initrd, srcversion `9366B03E91F9212A1501AEC`;
- four-lane 592.8 MHz firmware-selected Surface profile;
- native `OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0 -> /dev/video0` graph;
- negotiated 4076x2806 packed GRBG10 (`pgAA`), 5104 bytes/line, 14,321,824-byte frame;
- deterministic sensor color-bar SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
- 16/16 normal frames, sequences 0..15, every frame 14,321,824 bytes;
- mean frame interval 33.3885 ms, 29.9504 fps;
- clean STREAMOFF/close teardown: test pattern disabled, sensor runtime PM suspended, usage 0, MCLK1/CSIPHY1/timer enable counts 0, camera regulator enable counts 0;
- no kernel Oops/BUG/SError/camera error in the post-test fault scan;
- Wi-Fi connected, MultiMedia1 playback and MultiMedia3 capture present, Microsoft Surface G6 Touch present.

## Productionization conclusion

The source-integration gate is closed. The accepted source base is mechanically **true Golden-repro + exactly three intentional source-file differences**: `drivers/media/i2c/ov13858.c`, `arch/arm64/boot/dts/qcom/hamoa.dtsi`, and `arch/arm64/boot/dts/qcom/x1-microsoft-denali.dtsi`. The latter also preserves the previously deployed FullIO v19c and Phase91 touch/QSPI semantics.

No custom camera regulator provider, private power shim, or alternate audio kernel is required.
