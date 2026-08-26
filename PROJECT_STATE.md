# Project state

**Updated:** 2026-08-26  
**State ID:** E000 baseline  
**Golden remains:** SP11 Audio FullIO v19c

## What is mechanically proven

The current SP11 Linux boot is `7.1.5-sp11-render-parity-v4+` from the dedicated FullIO v19c payload. Audio playback and capture enumerate and the custom soft-pause lifecycle remains present. Camera work has not modified this Golden.

Linux currently exposes **no `/dev/video*` and no `/dev/media*`**. The deployed Denali DT has no enabled camera media graph even though camera reserved memory exists and the kernel contains X1E80100 CAMSS support.

The running kernel configuration already includes `CONFIG_VIDEO_QCOM_CAMSS=m`, V4L2 subdevice API and media-controller support. Installed modules include `qcom-camss.ko.zst` and `i2c-qcom-cci.ko.zst`.

## Exact SP11 camera hardware proven from Windows

The Windows SYSTEM hive and selected Surface camera packages identify:

- front RGB: `SONY0681` / **Sony IMX681**, Surface subsystem `MSHW0490`;
- rear RGB: `OVTID858` / **OmniVision OV13858**, subsystem `MSHW0491`;
- front IR/Hello: `SMO55F0` / **ST VD55G0**, subsystem `MSHW0492`;
- camera platform: `QCOM0C32` / Qualcomm **Spectra 695** camera platform, Surface subsystem `MSHW0495`.

Windows also installs Qualcomm MIPI CSI, ISP, secure ISP, JPEG encoder, flash/platform and Surface AVStream components.

## Oracle evidence already extracted

Selected Surface packages contain sensor-specific Qualcomm Chromatix data and board-resource packages. We have observed structure/field names for sensor slave addresses, I2C mode, power sequencing, resolution/mode data, stream configuration, lane assignment and C-PHY/D-PHY combo metadata.

Board-resource observations include:

- IMX681 front: `cam_cc_mclk4_clk`, PMIC votes including `LDO3_M` and `LDO7_B`;
- OV13858 rear: `cam_cc_mclk1_clk`, PMIC votes including `LDO1_M`, `LDO5_M`, `LDO6_M`, `LDO16_B`;
- VD55G0 IR: `cam_cc_mclk0_clk`, PMIC votes including `LDO2_M`, `LDO4_M`, `LDO7_M`;
- common camera XO/AHB/CPAS/Titan-top GDSC/MMCX resources and TLMM GPIO/delay resources.

These observations are clues, not yet a complete decoded sequencing table.

## Upstream/community assessment

X1E80100 CAMSS support exists and should be reused. Current upstream CSI-PHY work is still evolving; as of the E000 research snapshot, the new standalone X1E CSI2 PHY series is D-PHY-first and C-PHY work remains a follow-on. Therefore the IMX681 physical-link mode must be proven from Windows before we encode a DT assumption.

Community SP11 camera work is valuable research but does not yet provide a proven complete SP11 Snapdragon camera stream. Treat its proposed DT snippets as hypotheses until validated.

## Architecture decision

We are starting a **new native Surface-specific implementation** while retaining upstream Qualcomm infrastructure.

Bring-up order:

1. static Windows oracle decode;
2. dynamic Windows trace plan;
3. common X1E CAMSS/CCI/PHY infrastructure and test pattern;
4. rear OV13858 first;
5. front IMX681 second;
6. IR VD55G0 last;
7. ISP/libcamera image-quality parity after stable transport.

## Next action

**E001: build the Windows-oracle camera map before touching Linux DT.**

Decode the selected MSHW049x resource/configuration packages far enough to produce, for each camera:

- sensor I2C/CCI controller and slave address;
- exact MCLK and rate;
- ordered regulator/GPIO/reset/power delays;
- CSI PHY/index, lane/trio arrangement and D-PHY vs C-PHY mode;
- first useful sensor mode: dimensions, bit depth, link frequency/timing;
- stream-on/off register lifecycle.

Then design the smallest Linux CAMSS test-pattern/DT experiment from evidence rather than from community templates.
