# Front Windows-parity provenance gate

Date: 2026-08-30

This file makes the existing `AGENTS.md` evidence hierarchy executable for the front IMX681/VFE1 parity path. Same-machine Windows remains the hardware-behaviour authority. Public/upstream Qualcomm or Linux sources may supply register names, structure vocabulary and implementation examples, but they cannot by themselves promote a value, sequence, requester identity or DMA-domain assumption into a parity fact.

## Classifications

- `WINDOWS_OBSERVED` — directly captured on this SP11 while Windows exercised the relevant path.
- `WINDOWS_REVERSED` — mechanically recovered from the exact Surface/Qualcomm Windows binary installed on this SP11, normally cross-checked against live behaviour.
- `LINUX_IMPLEMENTATION` — an independently written Linux representation or safety mechanism. It is explicitly **not** claimed to be a Windows literal and must state an equivalence basis.
- `UNVERIFIED` — provenance is incomplete, inferred, upstream-only, or the exact Windows owner/formula remains unknown.

The machine-readable ledger is `provenance/front-parity.json`; `tools/check-front-parity-provenance.py` verifies every cited evidence file by SHA-256 and fails closed on critical `UNVERIFIED` entries. Evidence hashing uses canonical Git-index bytes, not checkout bytes, so CRLF/autocrlf differences cannot create false drift across SP7 Windows and SP11 Linux.

## Current audit result

The current pass contains 36 runtime/production-relevant facts:

- 18 `WINDOWS_OBSERVED`;
- 8 `WINDOWS_REVERSED`;
- 8 `LINUX_IMPLEMENTATION`;
- 2 `UNVERIFIED`.

For the bounded first VFE1 PIX/QC10C transport target there are now **zero provenance blockers**. This means the evidence ledger no longer contains a runtime-critical `UNVERIFIED` fact; it does not itself authorize hardware execution.

The last blocker, `rtcdm.command_dma_domain_visibility`, was split into two independently classified facts. Same-machine Windows now proves **RT-CDM1 front IFE command fetch -> SID `0x18a0` -> CB16 / `S1_IFE_HLOS`** by combining installed `qciommuext8380.inf` VFE-HLOS aggregate semantics, live IORT group mapping, installed `qcsmmu8380.inf` CB16 grouping, and the accepted `qccamisp8380.sys` hardware-CDM oracle. Public X1E naming is retained only as corroboration. Separately, Linux `0041` plus DMA-core/ARM-SMMU inspection proves `dma_alloc_coherent(camss->dev, ...)` allocates an IOVA in the CAMSS device translation domain that contains SID `0x18a0`. That composite Linux visibility fact is classified `LINUX_IMPLEMENTATION` with `parity_claim=false`.

For production parity two additional open provenance items remain: the ultimate owner of pre-existing `FE_CFG/FIFO0_CFG` state, and an independently implemented live IQ/provider strategy. Neither is allowed to masquerade as a Windows fact.

## Concrete erratum found by this audit

`windows-ife-cdm/RTCDM-IRQ-ORACLE.md` previously ended its parity consequence with `DMA source: CAMSS device DMA/IOMMU domain`. The interrupt oracle did **not** prove that. The document is corrected to say the DMA requester/domain is unestablished and runtime-blocking. Historical patch artifacts are left byte-stable as historical evidence; their `CAMSS DMA domain` comments are now classified as a Linux implementation hypothesis by the provenance ledger rather than retroactively rewritten.

The earlier upstream-only assertion that `SID 0x18a0` is the RT-CDM requester remains recorded as rejected **as upstream-only proof**. It is now superseded by the independent same-machine Windows derivation in `WINDOWS-RTCDM1-REQUESTER-SID.md`; public naming is not used as the behavioral authority.

## Runtime enforcement

`e003h-bounded-vfe1-pix-runtime-candidate/preflight-pix-one-shot.sh` now runs the provenance checker before hashes, boot state or module checks. Until the Windows DMA-domain blocker is closed, this preflight intentionally exits non-zero even if every candidate artifact hash matches.

When a Windows oracle closes a blocker, update the fact's classification/evidence, recompute evidence SHA-256 values, run both:

```text
python3 tools/check-front-parity-provenance.py --target bounded_first_pix
python3 tools/check-front-parity-provenance.py --target production_parity
```

Only a green target may be considered for a new authorization. A green provenance gate is necessary, not sufficient: Golden/preflight/runtime authorization rules still apply.

## Linux IOMMU implementation correction

Static `0041` now fixes the Linux side without promoting it to a Windows fact. The old eight-entry CAMSS list omitted `0x18a0`; the candidate uses the public X1E five-entry set and rebuilds Denali with an `iommus`-only structural change. Inspector `671cdcee8cbe7e21ec9923c4c555f50f139b6d7b32abd5f24e489b71d0a61827` proves the normal Linux DMA/IOMMU path maps CAMSS coherent allocations into the single CAMSS device domain that owns all five fwspec stream entries. The subsequent same-machine requester oracle now proves RT-CDM1 command fetch uses the `0x18a0` route. With that Windows fact plus Linux `0041`, the bounded provenance target has no critical `UNVERIFIED` item.
