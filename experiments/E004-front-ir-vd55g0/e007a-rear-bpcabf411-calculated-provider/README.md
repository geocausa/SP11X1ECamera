# E007a — rear BPC/ABF411 calculated-output provider

Parent Git: `a32928cd` (E006z clean scalar + bank provider PASS).

Status: **COMPILE-ONLY PASS**. No module install/load, camera access, reboot, MMIO write, DMI submission or RT-CDM submission is part of this experiment.

## Goal

Close the seven remaining non-bank BPC/ABF411 register contracts without embedding observed Windows register values or pretending the complete rear BPC/ABF algorithm is already ported.

Registers:

- 0x49B8, 0x49BC
- 0x49D0, 0x49D4, 0x49D8, 0x49DC, 0x49E0

E006i already source-locked 0x49B8/0x49BC to `IFEBPCABF411Titan680`. Fresh pinned-binary tracing extends the same exact Titan680 packer through the 0x49C8 count-9 range and proves the remaining five words are calculated-output packing, not independent constants.

## Exact calculated-output boundary

The provider consumes only values already produced by the BPCABF411 common calculation:

- two signed 10-bit fields;
- two unsigned 9-bit fields;
- two 4-bit fields;
- four groups of four bytes;
- two groups of four 4-bit values.

Those neutral names are intentional. The current clean/public reference tree does not expose reliable higher-level field names for this BPCABF41 generation, so this checkpoint does not invent tuning semantics.

Titan680 packing is exact:

- 0x49B8/0x49BC: signed10 in bits 0..9, unsigned9 in bits 16..24, nibble in bits 28..31;
- 0x49D0/0x49D4 and 0x49D8/0x49DC: four byte values packed little-endian;
- 0x49E0: eight 4-bit values packed consecutively.

## Private validation

`validate-private.py` decodes retained E006a MAIN packets locally, unpacks the seven words to this calculated-output boundary, repacks them, and requires exact equality.

Only aggregate counts are written to `PRIVATE-VALIDATION-SAFE.json`; no captured register values or packet bytes are committed.

Current validation:

- 22 records checked;
- 3 startup records;
- 19 steady records;
- 154 exact register round-trip checks;
- all seven words exact.

## Coverage on compile PASS

If the isolated build passes:

- concrete startup register providers become **684/714 (95.8%)**;
- remaining register contracts become **30**:
  - VFE680 PERIOD_CFG: 1;
  - BFStats25: 29.

This is register-provider closure only. Full rear BPC/ABF parity still requires the actual rear interpolation/common calculation inputs plus selector-1 DMI generation and live request-state integration.

## Build result — PASS

The full E006/E007a verifier chain passed and the staged provider was injected into an isolated copy of the accepted CAMSS source.

- private validation: 22 records, 154 exact seven-register round-trip checks;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,656,584 bytes;
- SHA-256: `1875123610a3d54b30e78333d1002a1b7ecd86353ca832762b8faaccae4d2059`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007a_bpcabf411_lookup`, `e007a_bpcabf411_provider_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

Concrete startup register providers are now **684/714 (95.8%)**. The remaining register contracts are exactly **30**: VFE680 PERIOD_CFG (1) and BFStats25 (29).

## Runtime gate

Native rear Linux ISP and RT-CDM submission remain **DENIED**. This checkpoint is compile-only producer-boundary closure.
