# Surface Titan680 steady packer checkpoint — E003h 0073

Status: **accepted offline checkpoint**. No Linux request6 execution is authorized.

The exact Surface DeviceMFT packers now separate the remaining producer work from simple register/DMI packing. This removes another layer of ambiguity: the Linux-side output format is no longer the unknown.

## White balance is closed

`IFEWB201Titan680::PackIQRegisterSetting` (RVA `0xb560c0`) stores Q10 channel gains shifted left 17. For matched Windows request6, AWB G/B/R = `1.000000000`, `1.936495066`, `1.781167150`. Nearest-Q10 values are `1024`, `1983`, `1824` and reproduce `0x4568=08000000`, `0x456c=0f7e0000`, `0x4570=0e400000` exactly. The two frame-varying WB fields (`0x456c`, `0x4570`) are therefore closed from the matched trigger vector.

## Demux/BLS boundary

`IFEDemuxBLS141Titan680::PackIQRegisterSetting` (RVA `0xb42840`) proves `0x3b70` and `0x3b74` are pure packings of four 15-bit calculated values. Request6 recovers all four as `1064`/`1064`/`1064`/`1064`. The remaining task is only the common calculation that produces these four values from trigger + tuning inputs.

## PDPC boundary

`IFEPDPC311Titan680::PackIQRegisterSetting` (RVA `0xb3c7d0`) proves the four true dynamic steady words are direct 17-bit calculated values at calculation-structure byte offsets `+0x24/+0x28/+0x2c/+0x30`. Matched request6 gives `0x1c80/0x1efc/0x08fc/0x0843`. The request5→6 PDPC DMI table is unchanged.

## Changing DMI packers

Exact Titan680 packers are pinned for GIC311 (`0xb4b500`), GTM131 (`0xb5b3d0`) and LSC411 (`0xb3d8a0`). Their bank selection and output construction are known; what remains is reproducing their interpolation/calculation inputs from the decoded IMX681 Chromatix and matched request trigger vector.

No new MMIO, RT-CDM submission, sensor operation or Linux camera runtime was performed.
