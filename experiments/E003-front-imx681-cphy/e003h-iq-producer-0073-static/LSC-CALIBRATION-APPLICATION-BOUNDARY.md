# E003h 0073 — exact IFELSC411 calibration application boundary

Status: **accepted static + Windows-live boundary proof**. This checkpoint does not run the Linux camera or Linux request6. It narrows the remaining Windows oracle requirement from a conservative five-slot calibration blob to the single `0xdf0` slot actually consumed by this physical SP11 front-camera stream.

> **Live-authority correction (2026-09-02):** this document proves the calibration algorithm, slot layout, ratio direction, green averaging, and pre-geometry/pre-Tintless placement. Its decoded `com.surface.tuned.ffc_imx681.bin` golden object is the **nominal front-package golden**, not the live LSCTRIGSRC golden authority. Recovered front x22/x23 equations now uniquely select rear/default OV13858 `lscgolden41_ife_v2` region `0x2ae`, SHA `f771e54d183281251bf0ef6d94e94a0d439c641f8b8ed9a3ad60ead4094487d6`. See `LSC-LIVE-GOLDEN-AUTHORITY.md`.

> **Calibration-payload authority update (2026-09-03):** the exact older rear OV13858 VSS runtime slot SHA `fb14d234…`, together with the live rear/default golden, reproduces the complete verified-front req5/req6 x23 payloads byte-for-byte. The algorithm in this document remains unchanged; see `LSC-FRONT-REAR-CALIBRATION-AUTHORITY.md`.

## Surface golden LSC is explicit and separate from EEPROM

`IFELSC411::CheckAndUpdateChromatixData` at RVA `0xa02420` resolves three independent Surface tuning modules: `lsc41_ife_v2`, `tintless23_sw_v2`, and **`lscgolden41_ife_v2`**. The golden module is published at LSC common input `+0x10`.

In the exact front tuning blob, `lscgolden41_ife_v2` is root symbol **42**, version 4.1 / Default. Its leaf region is symbol **1229**, SHA256 `b0023db8b7254a9922c60506db58fd9bf2d717e09a8f088d31f33b2316538f6e`, and is exactly **884 float32 values = four 221-point meshes**. Every value is integer-valued float32; the table spans 133 through 1023.

This is not the physical EEPROM table. Windows uses the golden table and the formatted sensor EEPROM together.

## Exact formatted-EEPROM translation

`IFELSC411::CheckDependenceChange` at RVA `0xa028b0` reads the formatted EEPROM object from `ISPInputData+0x2070`. It allows up to five candidate `0xdf0`-byte LSC slots at offsets:

`0x168, 0xf58, 0x1d48, 0x2b38, 0x3928`.

A slot is accepted when its first dword is `1`. Accepted slots are copied into the module's `0x45b0` calibration store at `module+0x1978`, and common `+0x60` points to a five-entry descriptor array. For each copied slot the four 221-float channel pointers are exactly slot `+0x0c`, `+0x380`, `+0x6f4`, and `+0xa68`. Common `+0x68` records the number of valid slots; `+0x6c` and `+0x80` are asserted when calibration is valid and applied.

The live Windows request4/5/6 common-input captures all report the same branch:

- descriptor capacity `common+0x58 = 5`;
- valid calibration slots `common+0x68 = 1`;
- calibration enable `common+0x6c = 1`;
- calibration apply `common+0x80 = 1`.

Therefore this SP11 front module has **one valid LSC calibration slot in the observed stream**. No five-slot or lens-position interpolation is needed for reproducing this stream.

## Exact calibration math

The exact `LSC411Interpolation::RunInterpolation` at RVA `0x93c1b0` proves the ratio direction and ordering. After normal LSC41 Chromatix interpolation, Windows forms per-channel calibration ratios as:

`ratio[channel] = lscgolden41[channel] / formatted_EEPROM[channel]`.

Those ratios are applied to the interpolated LSC mesh **before geometry resampling and before Tintless**. The two green channels have a deliberate Windows-specific rule: after their independent ratios are applied, Windows averages them and writes the same result into both green meshes:

`G = 0.5 * (ratio1 * tuning_G1 + ratio2 * tuning_G2)`.

So after calibration, the two base green meshes are equal even though the underlying Surface tuning G1/G2 meshes are not equal. This behavior must be reproduced exactly rather than simplified into one arbitrary green channel.

The EEPROM formatter (`EEPROMData::FormatLSCData`, RVA `0x723e40`) converts the extracted integer samples directly to float32 with `SCVTF`; no gain-scale multiply occurs at those conversion sites. This is consistent with the previously closed EEPROM layout: one 221-point table, four contiguous u16 arrays, physical EEPROM bytes `0x103d..0x1724`.

## Why the earlier replay missed

The earlier request4 experiment performed exact CCT interpolation, exact Surface geometry resampling, and then applied the captured Tintless correction table. It missed the final Q10 mesh by hundreds of units at some points. That experiment omitted this **golden / EEPROM calibration stage**, which Windows executes before geometry resampling. The miss is therefore expected and no longer points to the resampler or Titan680 packer.

## Reduced next capture

The old conservative capture plan allowed the entire `0x45b0` five-slot module store. The live branch proves that is unnecessary. The next Windows oracle needs only **one exact `0xdf0` copied formatted calibration slot**.

The safest capture is after translation has established `common+0x68 == 1`: dump `module+0x1978` for exactly `0xdf0` bytes. That is the exact copied slot consumed by `LSC411Interpolation`, and it avoids any pointer-unit ambiguity in debugger expressions involving `ISPInputData+0x2070`.

After that slot is captured in the same atomic Windows stream, the remaining offline chain is fully bounded:

`LSC41 trigger interpolation -> golden/EEPROM calibration -> exact geometry resample -> sequential Tintless -> Q10 staging -> closed Titan680 LSC packer -> closed GIC alias`.

GTM is already independently byte-exact. Linux request6 remains blocked until this complete same-stream producer replay matches byte-for-byte.

Proof artifacts: `prove-lsc-calibration-application-boundary.py` and `lsc-calibration-application-oracle.json`. Raw Windows captures and proprietary binaries remain local/untracked.
