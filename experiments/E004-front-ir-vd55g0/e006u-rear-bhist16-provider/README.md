# E006u — Titan680 BHistStats16 semantic startup provider

Parent Git: de4b1f69 (E006t rear small-IQ compile PASS).

Status: **COMPILE-ONLY PASS**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Close the BHistStats16 startup register contract without freezing captured Windows values:

- 0xB258 and 0xB25C — startup1-only DMI-side register range.
- 0xB26C — startup-specific BHist region-count word.

## Source closure

Pinned Surface QcDeviceMFT8380.dll identifies IFEBHistStats16Titan680 for IFE module type 0xB. Initialization maps the exact IFE addresses 0xB258, 0xB260, 0xB264, 0xB268, 0xB270, 0xB2A4 and DMI register 0xB208.

The Titan680 object allocates and zero-initializes an 80-byte register image. Its packer leaves the two words corresponding to 0xB258/0xB25C at zero apart from explicitly clearing bit 0. The startup symbolic topology independently proves that range is emitted only by startup1; startup2–4 omit it.

Modern BHistStats16::CalculateRegionConfiguration computes horizontal region count as max((ROI.width >> 1) - 1, 1) and vertical region count as max((ROI.height >> 1) - 1, 0). IFEBHistStats16Titan680::PackIQRegisterSetting places those counts in the low/high 13-bit fields of 0xB26C.

The provider accepts Linux-owned BHist ROI width/height for 0xB26C; it does not import a Windows ROI or captured register word.

## Private validation

Retained E006a startup packets were used only as a private validation oracle. The safe result records that startup1 contains the 0xB258/0xB25C pair and both match the zero-seeded Titan680 image; startup2–4 omit that pair; and all four startup variants contain 0xB26C with no bits outside the source-locked 13+13 region-count fields.

No raw packet bytes or raw Windows register values are committed.

## Coverage

E006u closes three BHistStats16 startup values: two startup-only words and the startup-vs-steady region-count word.

- startup-only implemented: **126/184**
- concrete startup providers: **595/714 (83.3%)**
- remaining startup-only registers: **58**, all in AECBEStats17, TintlessBGStats17, AWBBGStats17 and RSStats14

## Build result — PASS

The E006g/j/l/m/o/p/q/r/s/t/u verifier chain passed and the staged providers were injected into an isolated copy of the accepted CAMSS source.

- W=1 warnings/errors: 0
- qcom-camss.ko: 13,630,432 bytes
- SHA-256: `b3b8c895a9d89958c91409186444cc36ce654a327315da39d803785d2affb530`
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- retained symbols: `e006u_bhist16_lookup`, `e006u_bhist16_recipe`
- install/load/camera/RT-CDM submission: none

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED** until the remaining stats/state producers and integration gates are closed.

Next: close RSStats14, then the three 18-word stats families.
