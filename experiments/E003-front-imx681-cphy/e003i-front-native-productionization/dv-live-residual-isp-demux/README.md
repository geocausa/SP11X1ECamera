# E003i-DV — live residual ISP gain -> Titan680 Demux/BLS

Status: **PASS (static/offline; no camera runtime).**

DV closes the arithmetic/selector seam needed to feed CQ's per-request residual ISP gain into the already-proven Titan680 IQ capsule.

The active ordinary front path is the proven Sensor2 branch. The existing IMX681 Chromatix decoder already verifies that the required IFE module set is invariant across Sensor2 Preview/Snapshot/Video descendants. For Demux/BLS the effective module is Default symbol 31, not one of the unrelated direct Usecase records. Its pointer graph contains empty intermediate triggers and one 16-byte region with black-level terms:

`602, 593, 592, 596`

The channel terms are four `1.0f` values.

The exact Windows Surface common-setting function is `QcDeviceMFT8380.dll` RVA `0x998e70`. ARM64 disassembly proves single-precision subtract/divide/multiply ordering, max-channel common normalization, limit `31.999000549316406f`, Q gain `1024.0f`, and `FRINTA s0,s0` rounding. For Bayer0 the packed values are:

- calc6 <- BLS[1] / channel[1]
- calc7 <- BLS[3] / channel[0]
- calc8 <- BLS[2] / channel[2]
- calc9 <- BLS[0] / channel[3]
- `0x3b70 = calc6<<16 | calc7`
- `0x3b74 = calc9<<16 | calc8`

DV implements those operations with explicit float32 rounding after every ARM scalar FP operation and nearest-integer/ties-away rounding for the final positive Q10 values.

No camera runtime, module load, sensor write, IQ submit, or Windows boot is performed by DV.
