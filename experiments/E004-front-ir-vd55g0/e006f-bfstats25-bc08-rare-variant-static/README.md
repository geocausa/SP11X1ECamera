# E006f — source-lock rear 0xBC08 BFStats25 ownership and rare-variant residual

Parent Git: e8872642 (E006e A98 cross-variant result).

Status: STATIC/OFFLINE PASS WITH ONE DELIBERATE RESIDUAL. No Linux camera runtime was performed. No Windows reboot/KD run was required.

## Why

E006e proved the 12 AC8-stable DMI identities remain byte-identical in a healthy A98 request, but steady 0x8F0 and true steady 0x658 were not observed. The remaining question was whether those rare variants contain an unknown payload producer or only already-understood modules.

## Exact 0xBC08 owner

A scalar-immediate xref pass over the pinned Surface QcDeviceMFT8380.dll found exactly one function containing literal 0xBC08:

- VA 0x180b4f4e0
- exact source strings identify CamX::IFEBFStats25Titan680::CreateCmdList
- exact source path: camxifebfstats25titan680.cpp

The function programs:

- 0xBC08, selector 1 — BF ROI DMI buffer
- 0xBC08, selector 2 — BF gamma LUT DMI buffer

Selector 1 length is numROI * 12 bytes. The rear corpus carries 300 bytes, corresponding to 25 packed ROI records.

Selector 2 is exactly 128 bytes and is emitted when the BF gamma-LUT enable path is active.

The same function programs BF module registers in the 0xBC58..0xBCF0 range. This identifies 0xBC08 as the BF/BAF statistics configuration DMI block, not an image-IQ tuning LUT.

## Upstream dependency behavior

Exact DeviceMFT CamX::BFStats25::CheckDependenceChange / validation code shows that the BF DMI content is derived from the request's AF-stats configuration:

- ROI configuration is validated/adjusted from pAFStatsUpdateData->statsConfig;
- invalid current AF ROI input can fall back to the previous valid configuration;
- ROI and gamma banks are tracked/toggled by the module;
- ROI/gamma regeneration is conditional on dependency changes.

Therefore 0xBC08 is configuration/state data. It is not proven globally immutable by static analysis.

E006c and E006e nevertheless provide strong same-role evidence that the concrete rear VideoRecord configuration is stable across:
- two consecutive steady AC8 requests;
- a separate healthy A98 request at generation 12.

Both selector 1 and selector 2 were byte-identical across those observations.

## Rare steady variant topology

E006a structural decode shows:

### MAIN 0x8F0
13 DMI records:
- LSC 0x4308 selectors 1/2/3
- GTM 0x5A08 selector 1
- Gamma 0x5F08 selectors 1/2/3
- DSX 0xA008 selectors 1/2
- DSX 0xA208 selectors 1/2
- BFStats25 0xBC08 selectors 1/2

There is no new module in 0x8F0.

### MAIN 0x658
3 DMI records only:
- GTM 0x5A08 selector 1
- BFStats25 0xBC08 selector 1
- BFStats25 0xBC08 selector 2

There is no new module in steady 0x658.

## Consequence

The missing rare-variant problem is now reduced to already-identified producers:

- dynamic LSC/Tintless where present;
- dynamic GTM/TMC;
- BFStats25 ROI/gamma configuration state;
- previously cross-variant-stable Gamma/DSX/other static candidates.

A future 0x8F0/steady-0x658 capture is not required to discover another producer class. It may still be useful as a validation oracle.

The one unresolved static/runtime boundary is whether the rear VideoRecord AF-stats configuration can change after the observed request range. Do not promote 0xBC08 to an unconditional static template yet.

## Next

Prefer source/control-path closure of rear pAFStatsUpdateData->statsConfig ownership and update cadence before spending another Windows identity hunting rare MAIN variants. If that proves the rear role's BF configuration invariant, the missing 0x8F0/steady-0x658 payload uncertainty can be closed without another physical capture. Otherwise run one minimal validation capture focused only on distant-request 0xBC08 hashes rather than waiting for a rare MAIN size.

Native rear Linux ISP remains DENIED.
