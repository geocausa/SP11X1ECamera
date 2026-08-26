# E001 static oracle — sensor power/resource map

Evidence: exact local Windows DriverStore AeoB resources selected for this SP11 installation and decoded read-only with `tools/aeob_resources.py`.

## Front RGB — SONY0681 / IMX681 / MSHW0490 (`\\_SB.CAMF`)

D0 order:
1. vote `/arc/client/rail_mmcx` = `0x40`
2. enable `gcc_camera_xo_clk`
3. enable `gcc_camera_ahb_clk`
4. enable `cam_cc_gdsc_clk`
5. enable `cam_cc_titan_top_gdsc`
6. set `cam_cc_cpas_ahb_clk` = 80 MHz
7. TLMM GPIO 237 low
8. set `cam_cc_mclk4_clk` = 19.2 MHz
9. vote `LDO3_M` = 1.8 V
10. vote `LDO7_B` = 2.8 V
11. delay 1 (AeoB time unit; preserve ordering until dynamic confirmation)
12. GPIO 237 high
13. delay 10

D3 is the reverse lifecycle: GPIO237 low, delay, MCLK4 off, LDO7_B off, LDO3_M off, common camera-domain clocks/footswitch off, MMCX vote 0.

## Rear RGB — OVTID858 / OV13858 / MSHW0491 (`\\_SB.CAMS`)

D0 order:
1. MMCX `0x40`
2. camera XO/AHB/GDSC/Titan domain enable
3. CPAS AHB = 80 MHz
4. GPIO 110 low
5. `LDO6_M` = 1.8 V
6. `LDO1_M` = 1.2 V
7. `LDO5_M` = 2.8 V
8. delay 1
9. `LDO16_B` = 2.9 V
10. MCLK1 = 19.2 MHz
11. GPIO110 high
12. delay 10

D3: GPIO110 low, delay, MCLK1 off, LDO16_B/LDO5_M/LDO1_M/LDO6_M off, common domain teardown, MMCX 0.

## Front IR — SMO55F0 / VD55G0 / MSHW0492 (`\\_SB.CAMI`)

D0 order:
1. MMCX `0x40`
2. camera XO/AHB/GDSC/Titan domain enable
3. CPAS AHB = 80 MHz
4. GPIO109 low
5. delay 1
6. MCLK0 = 19.2 MHz
7. delay 2
8. `LDO4_M` = 1.8 V
9. `LDO2_M` = 1.15 V
10. delay 1
11. `LDO7_M` = 2.8 V
12. delay 1
13. GPIO109 high
14. delay 1

D3: GPIO109 low, delay 5, LDO7_M off, delay 1, LDO2_M/LDO4_M off, MCLK0 off, common teardown, MMCX 0.

## Notes
- GPIO numbers are SoC TLMM numbers from Windows AeoB, not Linux line names guessed from another device.
- Voltage/rate values are exact decoded integers from the selected local Windows package.
- We will translate resource IDs to Linux regulator phandles only after matching them against X1E PMIC DT naming.
