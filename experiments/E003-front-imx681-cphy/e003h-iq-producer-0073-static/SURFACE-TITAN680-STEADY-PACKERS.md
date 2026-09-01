# Surface Titan680 steady packer checkpoint — E003h 0073

Status: **accepted offline checkpoint**. No Linux request6 execution is authorized.

The exact Surface DeviceMFT now closes **six of the eight** true frame-varying scalar fields. The other sixteen changing register fields in the 0x958 shape are the already-separated ping-pong bank parity bits.

## White balance — closed

The exact WB common setting function (RVA `0x995e60`) computes Q10 channel values as `round(channel_gain × predictiveGain × 1024)`. `IFEWB201Titan680::PackIQRegisterSetting` (RVA `0xb560c0`) shifts those Q10 values left 17. Matched request6 has AWB G/B/R = `1.000000000`, `1.936495066`, `1.781167150` and is reproduced exactly with effective predictive gain 1.0: G/B/R Q10 = `1024/1983/1824`, yielding `0x4568=08000000`, `0x456c=0f7e0000`, `0x4570=0e400000`. Predictive gain is a real producer input and must not be globally hard-coded.

## PDPC — four dynamic scalars closed

The exact PDPC311 interpolation/HW setting functions are RVA `0x943e80` and `0x9c07c0`; Titan680 packing is RVA `0xb3c7d0`. The four true dynamic steady registers are Q12 AWB ratios:

- `0x3d78 = round((R/G) × 4096)` → `0x1c80`
- `0x3d7c = round((B/G) × 4096)` → `0x1efc`
- `0x3d80 = round((G/R) × 4096)` → `0x08fc`
- `0x3d84 = round((G/B) × 4096)` → `0x0843`

All four reproduce matched Windows request6 byte-for-byte from the matched AWB trigger vector. The PDPC 0x200-byte DMI payload did not change from request5 to request6.

## Demux/BLS — packing closed, producer inputs remain

`IFEDemuxBLS141Titan680::PackIQRegisterSetting` is RVA `0xb42840`; the exact common HW setting is RVA `0x998e70`. `0x3b70` and `0x3b74` pack four 15-bit calculated channel values. For request6 all four are `1064`, producing `0x04280428` twice. The setting function proves each channel is a rounded Q10 normalized value built from ISP gain, four interpolated BLS terms and four channel terms, with the exact `16383/(16383-BLS)` correction and common max-channel normalization. The remaining scalar task is therefore only to recover those request-time/interpolated inputs from the decoded IMX681 tuning tree.

## Changing DMI packers

Exact Titan680 packers remain pinned for GIC311 (`0xb4b500`), GTM131 (`0xb5b3d0`) and LSC411 (`0xb3d8a0`). Their bank selection/output layout is known. Exact follow-up proof shows the Windows GIC wire payload aliases LSC rather than the logical GIC table, so independent wire-producer work is now LSC and GTM.

No new MMIO, RT-CDM submission, sensor operation or Linux camera runtime was performed.
