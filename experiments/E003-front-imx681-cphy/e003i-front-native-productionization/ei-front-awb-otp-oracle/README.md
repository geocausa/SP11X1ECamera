# E003i-EI — same-device front AWB OTP oracle

Status: **PASS same-device raw OTP + Windows factor-table authority; clean `ComputeCalFactors` replay remains the next gate.**

The Windows oracle read the physical front IMX681 EEPROM at the exact EH boundary before streaming. Bytes `0x941..0x94c` are preserved in `AWB-OTP-RAW.bin` and decode as six little-endian u16 values: `854, 369, 1023, 605, 589, 1020`. Dividing by the sensor-module qValue 1023 reproduces the two Windows formatted AWB records bit-for-bit: 2850 K `(RG=0x3f55b56d, BG=0x3eb8ae2c)` and 5000 K `(RG=0x3f1765d9, BG=0x3f1364d9)`.

A bounded stream was then used only to enter `CAWBCtrlV1::ComputeCalFactors`. Its ten final factor pairs were captured. `CTrigleAdjV1` uses their reciprocals. Slots 0..3 therefore yield `(0x3f80a277,0x3f83427b)`, exactly the pair that EG had independently solved from R4 barycentric weights and then validated through R11. This converts that earlier solved constant into an independent same-device calibration oracle.

`verify-ei.py` is deliberately fail-closed. It proves EEPROM byte order/quantization, Windows formatted OTP values, all ten captured factor pairs and their reciprocal scale bits. It does **not** yet claim a clean Linux implementation of `ComputeCalFactors`, and it does not claim a Linux runtime EEPROM read path.
