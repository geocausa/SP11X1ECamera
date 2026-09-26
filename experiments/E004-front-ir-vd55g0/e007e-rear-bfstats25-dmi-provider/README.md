# E007e — rear BFStats25 DMI provider

Parent Git: `56b8fe74` (E007d register-provider integration PASS).

Status: **COMPILE-ONLY PASS**.

## Goal

Implement the exact Titan680 BFStats25 DMI encoding boundary for:

- `0xBC08` selector 1 — BF ROI table;
- `0xBC08` selector 2 — BF gamma LUT.

This checkpoint starts from already-adjusted/sorted semantic AF BF state. It does **not** implement AF policy, ROI validation/adjustment/sorting, change detection, force-update policy, or DMI bank scheduling.

## Source lock

Pinned same-SP11 `QcDeviceMFT8380.dll` source-identifies:

- `CamX::BFStats25::UpdateROIDMITable`;
- `CamX::BFStats25::GammaGetHighLowBits`;
- `CamX::IFEBFStats25Titan680::CreateCmdList`.

The request path builds two 12-byte ROI representations. The hardware-submitted DMI source is the **compact** table at the request-state boundary; `CreateCmdList` copies its selector-1 buffer verbatim before `WriteDMI(0xBC08, 1, ...)`.

### Selector 1 compact ROI record

Each 12-byte record is three little-endian words:

- word0: `height[12:0]`, `width[11:0] << 14`, low five bits of `top` at bit 27;
- word1: remaining nine bits of `top`, `left[12:0] << 9`, `rid << 23`, low bit of `oid` at bit 31;
- word2: remaining seven bits of `oid`, `merge << 7`, `eob << 8`, `type << 9`.

The EOB bit is asserted only on the final emitted ROI record.

For the retained rear corpus the hardware payload is 25 records × 12 bytes = 300 bytes.

### Selector 2 gamma LUT

The request path produces 32 packed 32-bit words:

- low 14 bits: current gamma sample;
- high field from bit 14: signed next-minus-current delta, saturated to `[-8192, 8191]`;
- terminal next sample: `0x4000`.

Total payload size is 128 bytes.

## Private validation

`validate-private.py` uses only retained private E006b source windows and emits aggregate-safe results.

Current result:

- 5 captures containing BF DMI checked;
- 5 selector-1 payloads;
- 125 compact ROI records;
- EOB location and unused high bits checked for every ROI payload;
- 4 selector-2 payloads;
- 128 gamma words;
- exact byte-for-byte repack for both selectors;
- no raw payload values emitted or committed.

## Build result — PASS

The full E006/E007 provider chain plus E007d integration and E007e DMI encoding compiled in an isolated accepted CAMSS source copy.

- private validation: 5 captures;
- selector-1 ROI payloads: 5 / 125 compact ROI records;
- selector-2 gamma payloads: 4 / 128 gamma words;
- exact byte-for-byte repack for both selectors;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,736,888 bytes;
- SHA-256: `9e4ce04df6613513e2d0cbcf19d1548de736af6e7f3a24214603906e124de486`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007e_bfstats25_dmi`, `e007e_bfstats25_dmi_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

## Boundary

This closes **BFStats25 DMI encoding**, not BFStats25 AF policy.

Still upstream:

- AF BF ROI validation/adjustment/sorting;
- gamma resampling/input production;
- ROI/gamma change tracking and force-update policy;
- independent BF DMI bank state;
- request-time integration into the rear DMI materializer.

## Safety

No module install/load, camera access, MMIO, DMI submission or RT-CDM submission is part of this checkpoint.
