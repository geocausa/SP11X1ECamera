# E000 Windows camera oracle inventory

Source: the Windows installation on the same SP11, inspected read-only on 2026-08-26.

This file contains derived identities and hashes only. Proprietary payloads are not stored in Git.

## Enumerated hardware

- Front RGB: `ACPI\\SONY0681`, Surface `MSHW0490`, Sony IMX681.
- Rear RGB: `ACPI\\OVTID858`, Surface `MSHW0491`, OmniVision OV13858.
- Front IR: `ACPI\\SMO55F0`, Surface `MSHW0492`, ST VD55G0.
- Camera platform: `ACPI\\QCOM0C32`, Surface `MSHW0495`, Qualcomm Spectra 695 family.

## Selected Windows driver versions

Surface sensor drivers/extensions observed: `1.0.4258.7908` dated 2025-04-25.
Core Qualcomm camera components observed: `1.0.4258.7900` dated 2025-03-06.

## Selected sensor/configuration files

The SHA-256 table below is a provenance index only. The binaries themselves are intentionally excluded from this repository.

| Sensor | File | SHA-256 |
| --- | --- | --- |
| front | `SCFG_FRONT_MSHW0490.bin` | `e6e3d828a1e4f5bc94c545848a091c20be399a4b22c938ed4a3df072dd033d99` |
| front | `CAMF_RES_MSHW0490.bin` | `379a03154511922428ea27f56de625f579f39ca483fb97398953278b6b5f2851` |
| front | `com.surface.sensormodule.ffc_imx681.bin` | `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c` |
| front | `com.surface.tuned.ffc_imx681.bin` | `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d` |
| rear | `SCFG_REAR_MSHW0491.bin` | `fa1d4b79ac3305ed822aae7fb2d1676d28eb130cb651b2b7f84d208aab64652a` |
| rear | `CAMS_RES_MSHW0491.bin` | `2d356bbfaf07ced1e5c03014a5c496b12107f5dc489c4333052565d5a5a5dcc2` |
| rear | `com.surface.sensormodule.rfc_ov13858.bin` | `f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14` |
| rear | `com.surface.tuned.rfc_ov13858.bin` | `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635` |
| ir | `SCFG_AUX_MSHW0492.bin` | `1c848ac4ddbe12948cae4affee421e3a457cac61f98dacb30043841bf0bd1bff` |
| ir | `CAMI_RES_MSHW0492.bin` | `fb058d3c966f4b48412d48c2de7f58b861103a8aa06f0bb8c1d198e12431d908` |
| ir | `com.surface.sensormodule.aux_vd55g0_MSHW0492.bin` | `e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794` |
| ir | `com.surface.tuned.aux_vd55g0_MSHW0492.bin` | `41518f81eadb61e824df1a8bc21f60c163190f555432210ec96c78d87afcdffd` |
| platform | `CAMP_PCFG_MSHW0495.bin` | `0933a645ea55c95953ac3f0b6829e01c27133d52f369596f62fb3c5e99f5807f` |
| platform | `CAMP_PRLD_MSHW0495.bin` | `4ee30fe5decd46d49880057faf14d0e28cb7ab4eb381b06ce445d84ce4a9fa18` |

## Resource-name observations already established

- front IMX681 resource package references `cam_cc_mclk4_clk`, `LDO3_M`, `LDO7_B`;
- rear OV13858 references `cam_cc_mclk1_clk`, `LDO1_M`, `LDO5_M`, `LDO6_M`, `LDO16_B`;
- IR VD55G0 references `cam_cc_mclk0_clk`, `LDO2_M`, `LDO4_M`, `LDO7_M`;
- common package vocabulary includes camera XO/AHB clocks, CPAS, Titan top GDSC, MMCX rail, TLMM GPIO, delays and PMIC regulator votes.

These names do not yet establish order, voltage, polarity or timing. E001 exists to decode/trace those details.
