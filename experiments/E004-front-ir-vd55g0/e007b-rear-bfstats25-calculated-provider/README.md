# E007b — rear BFStats25 calculated-output provider

Parent Git: `6705a2f5` (E007a BPC/ABF411 compile PASS).

Status: **COMPILE-ONLY PASS**. No module install/load, camera access, reboot, MMIO write, DMI submission or RT-CDM submission is part of this experiment.

## Goal

Close the 29 remaining BFStats25 register contracts using the exact Titan680 low-level calculated-output packing boundary, while keeping AF policy and BF ROI/gamma DMI generation explicitly upstream.

Registers:

- 0xBC58, 0xBC5C, 0xBC60;
- 0xBC6C..0xBCA8 in the source-locked sparse ranges;
- 0xBCAC..0xBCD0.

No observed Windows register value is embedded.

## Source lock

Pinned Surface `QcDeviceMFT8380.dll` analysis uses the already-closed E006f functions:

- `IFEBFStats25Titan680::CreateCmdList` at 0x180B4F4E0;
- `IFEBFStats25Titan680::PopulateLUTConfig` at 0x180B4FC20;
- BFStats25 request logic at 0x180A1D340;
- shared tail pack helper at 0x180B4F860.

CreateCmdList proves the exact Titan680 register windows and also independently keeps BF ROI DMI at 0xBC08 selector 1 and BF gamma LUT DMI at selector 2.

## Calculated-output boundary

The provider consumes only low-level state after AF/BF request policy has produced it:

- DMI LUT bank and module LUT bank;
- explicit module/config flags for luma selection, gamma LUT, luma conversion, scaling and the three source-locked filter groups;
- 13 signed 6-bit values packed into sparse byte lanes;
- two ten-value signed-16 quantized groups, preserving the two reserved halfword holes in the second group;
- two signed 4-bit values;
- two tail blocks, each one 17-bit scalar plus seventeen 5-bit values placed at 6-bit spacing.

The neutral names for low-level coefficient groups are intentional. This checkpoint does not invent higher-level AF tuning semantics where current clean/public source does not provide them.

## Private validation

`validate-private.py` decodes retained E006a MAIN packets locally, inverts all 29 BFStats25 words to this calculated-output boundary, repacks them, and requires exact equality.

Only aggregate results are written to `PRIVATE-VALIDATION-SAFE.json`; no captured register values or packet bytes are committed.

Validation result:

- 35 records checked;
- all 4 startup records;
- 31 steady records;
- 1,015 exact register round-trip checks;
- all 29 words exact;
- no unknown bits set in the 0xBC60 config word.

## Coverage on compile PASS

If the isolated build passes:

- concrete startup register providers become **713/714 (99.9%)**;
- the only register contract left open is **VFE680 PERIOD_CFG 0x008C**, already classified as opaque upstream transport state rather than IQ state.

This does **not** mean camera-stack parity is complete.

BFStats25 still requires the Linux AF producer to generate validated/adjusted ROI state, ROI DMI records, the 128-byte gamma LUT, independent DMI bank state and change/force-update policy. Other live rear DMI/IQ/3A state-production gaps also remain.

## Build result — PASS

The complete E006/E007a/E007b verifier chain passed and the staged provider was injected into an isolated copy of the accepted CAMSS source.

- private validation: 35 records, 1,015 exact 29-register round-trip checks;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,674,856 bytes;
- SHA-256: `c5174f717f05e7494af97aff3b3ee39f6a7d2d7b0a63de067801e919de99087f`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007b_bfstats25_lookup`, `e007b_bfstats25_provider_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

Concrete startup register providers are now **713/714 (99.9%)**. The sole remaining register contract is VFE680 PERIOD_CFG 0x008C, already classified as opaque upstream transport state rather than IQ state.

## Runtime gate

Native rear Linux ISP and RT-CDM submission remain **DENIED**. This checkpoint is compile-only register-packing closure.
