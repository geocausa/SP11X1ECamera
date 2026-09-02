# E003h 0073 — adaptive LSC/GTM output boundary

Status: **accepted offline/static**. The proof uses the exact IMX681 tuning blob and the matched Windows request6 DMI slot; it performs no camera runtime.

For LSC, the exact 4999 K base Chromatix interpolation produces four 221-point channels. The proof applies the exact Q10/14-bit quantization and tests **all 24 possible channel assignments** to the two Titan680 `0x374`-byte LSC tables. None reproduces matched Windows LSC0+LSC1. The closest assignment still differs in **1,496 bytes**. This closes the possibility that the remaining Windows LSC is merely a channel-order or base-CCT interpolation mistake.

For GTM, the selected static GTM13 region is exactly 257 copies of `4096.0`. The matched Windows GTM0 decodes to base values spanning **4097..4442**, with 61 distinct base values and **zero** entries equal to 4096. The packed q field is uniformly 30. Therefore the downstream dynamic TMC path is not optional bookkeeping: it materially changes the Windows GTM curve.

Combined with `EEPROM-LSC-BOUNDARY.md`, the remaining producer work is now bounded to the per-device/request adaptive inputs themselves, not unresolved static tuning math. The GTM side is additionally reduced by `GTM-TMC-READ-BOUNDARY.md`: for the exact generation-5 path the hardware calculation consumes seven sparse internal TMC ranges totaling at most `0x108c` bytes, with the IFE call uniquely filterable by GTM HW-setting RVA `0x9aa6e0` / LR `0x180a28f2c`.
