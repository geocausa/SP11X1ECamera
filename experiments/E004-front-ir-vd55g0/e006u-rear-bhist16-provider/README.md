# E006u — Titan680 BHistStats16 semantic startup provider

Parent Git: de4b1f69 (E006t rear small-IQ compile PASS).

Status: **STAGED / COMPILE PENDING**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

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

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED** until the remaining stats/state producers and integration gates are closed.
