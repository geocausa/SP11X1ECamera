# E003h same-machine Windows RT-CDM1 command-requester SID oracle

Date: 2026-08-30

This closes the last provenance blocker for a bounded first VFE1 PIX/QC10C experiment. The result is derived only from same-machine Windows configuration/data plus the already-accepted same-machine RT-CDM1 activity oracle. Public X1E Linux material is retained solely as an independent naming/implementation cross-check.

## Exact Windows evidence

The installed `qciommuext8380.inf` is 22,974 bytes, SHA-256 `18e06ef557a9b0ef7d22fa3c8f97909699e915946aeec0a758f3e32cb9676a6c`. Its S1 aggregate table describes VFE HLOS input base `0x01030000`, count **5**, as:

`S1_IFE_HLOS — Camera CDM IFE, IFE/SFE RD/WR non-protected stream`

The live IORT from this same Windows boot is 5,366 bytes, SHA-256 `c561d68b2c3e731c927481ca37bc97302a2f3dcd24747ebf530b8be19795445b`. It maps the five VFE-HLOS aggregate input IDs exactly as:

- `0x01030000 -> SID 0x18a0`
- `0x01030001 -> SID 0x0800`
- `0x01030002 -> SID 0x0860`
- `0x01030003 -> SID 0x0840`
- `0x01030004 -> SID 0x0820`

The independently decoded installed `qcsmmu8380.inf` groups the four `0x0800`-family IDs with mask `0x0060`, and leaves `0x18a0` as the singleton mapping, all in CB16 / VM4 / `S1_IFE_HLOS`. Thus the four masked IDs are the four IFE/SFE RD/WR members and the remaining singleton member of the five-entry VFE-HLOS aggregate is the **Camera CDM IFE** requester.

Separately, the exact installed `qccamisp8380.sys` and same-machine live RT-CDM oracle prove the accepted front IFE command engine is hardware **RT_CDM1** at `0x0ac26000`. Combining these independent Windows facts yields:

**RT-CDM1 front IFE command fetch -> SID `0x18a0` -> CB16 / `S1_IFE_HLOS`.**

This is not inferred from upstream Linux ordering. Public X1E CAMSS material happens to name the fifth IOMMU entry `CDM IFE`, but that source is only corroboration after the Windows derivation above.

## Linux consequence

Static Linux `0041` independently supplies the five-entry CAMSS fwspec set including `0x18a0`, and Linux DMA-core/SMMU inspection proves `dma_alloc_coherent(camss->dev, ...)` uses the CAMSS IOMMU DMA domain and installs all CAMSS fwspec entries into the same translation domain/context bank. Therefore the Linux implementation can make its coherent command-buffer IOVA visible to the Windows-proven RT-CDM1 requester.

That Linux wiring remains classified `LINUX_IMPLEMENTATION`, not a Windows literal. This document closes only the Windows requester identity.

## Runtime status

No Linux PIX execution occurred while closing this oracle. A green provenance gate does not itself authorize another hardware attempt; the separate Golden/preflight/one-shot authorization discipline still applies.
