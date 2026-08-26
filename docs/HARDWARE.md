# SP11 camera hardware inventory

This file records facts established from the actual SP11 Windows installation.

## Front RGB — Sony IMX681

- Windows ACPI ID: `SONY0681`
- Surface subsystem: `MSHW0490`
- Windows sensor package: `surfacecamfrontsensor8380`
- Surface extension selects `com.surface.sensormodule.ffc_imx681.bin`
- observed resource clock: `cam_cc_mclk4_clk`
- observed PMIC resource names include `PPP_RESOURCE_ID_LDO3_M`, `PPP_RESOURCE_ID_LDO7_B`

## Rear RGB — OmniVision OV13858

- Windows ACPI ID: `OVTID858`
- Surface subsystem: `MSHW0491`
- Windows sensor package: `surfacecamrearsensor8380`
- Surface extension selects `com.surface.sensormodule.rfc_ov13858.bin`
- observed resource clock: `cam_cc_mclk1_clk`
- observed PMIC resource names include `LDO1_M`, `LDO5_M`, `LDO6_M`, `LDO16_B`

## Front IR / Hello — ST VD55G0

- Windows ACPI ID: `SMO55F0`
- Surface subsystem: `MSHW0492`
- Windows sensor package: `surfacecamauxsensor8380`
- Surface extension selects `com.surface.sensormodule.aux_vd55g0_MSHW0492.bin`
- observed resource clock: `cam_cc_mclk0_clk`
- observed PMIC resource names include `LDO2_M`, `LDO4_M`, `LDO7_M`

## Qualcomm camera platform

Windows enumerates Qualcomm's 8380 camera driver family, including MIPI CSI, ISP, secure ISP, JPEG encoder, platform and Surface AVStream layers. Human-readable descriptions call the main camera path **Spectra 695**.

Linux already contains X1E80100 CAMSS support, but the deployed Denali DT does not currently enable a camera graph.
