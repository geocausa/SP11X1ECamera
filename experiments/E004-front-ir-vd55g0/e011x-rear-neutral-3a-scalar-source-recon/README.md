# E011X — rear neutral-3A scalar source reconnaissance

Parent Git: `b15e23a623f0879ec127cd09ad470b9821bfba61` (E011W). Evidence class: committed source/static contract audit only. No new Windows live identity was consumed and no native rear ISP runtime occurred.

Status: **SOURCE-ONLY RECON PASS; PRODUCER/REQUEST LIVE BINDING OPEN.**

## Scope

E011W closed the remaining AF/BF bootstrap timing question. E008p therefore leaves neutral AEC/AWB scalar state as the next semantic gate before request-tagged LSC/GTM.

This stage deliberately does **not** reuse the retained Windows startup register words as a bootstrap policy. E008p's rule still applies: a packer output is not its semantic producer. Private E006a startup outputs may only validate a source-backed producer after that producer is identified.

## Exact neutral-3A scalar boundary

The accepted E006z provider already fixes the Linux semantic object shape:

- `demux_q10[4]`: four Q10 normalized Demux/BLS channel values;
- `pdpc_q12[4]`: four Q12 AWB ratios;
- `wb_b_q10` and `wb_r_q10`: Q10 B/R WB gains after `predictiveGain`;
- `request_id`, `startup_phase`, and epoch kind for identity/bank policy.

The PDPC ratios are, in order:

1. AWBR / AWBG
2. AWBB / AWBG
3. AWBG / AWBR
4. AWBG / AWBB

No observed rear scalar register value is promoted by this checkpoint.

## Pinned Titan680 calculation boundaries

The already source-locked E006z authority gives the exact module boundaries to follow upstream:

| Module | Common calculation | Interpolation | Packer | CreateCmdList |
| --- | ---: | ---: | ---: | ---: |
| IFEDemuxBLS141Titan680 | `0x998E70` | — | `0xB42840` | `0xB41FF0` |
| IFEPDPC311Titan680 | `0x9C07C0` | `0x943E80` | `0xB3C7D0` | `0xB3BD10` |
| IFEWB201Titan680 | `0x995E60` | — | `0xB560C0` | `0xB559F0` |

The corresponding packed register boundary is already closed:

- Demux/BLS: `0x3B70`, `0x3B74`;
- PDPC AWB ratios: `0x3D78`, `0x3D7C`, `0x3D80`, `0x3D84`;
- WB: `0x456C`, `0x4570`.

E006z leaves the upstream producer state explicit: rear post-sensor gain plus Demux/BLS tuning/interpolation, live AWB G/B/R state plus `predictiveGain`, and coherent request/startup-phase identity.

## Four-packet identity requirement

E008o/E007y forbid collapsing startup into a single mutable neutral state. Each of the four startup packets owns a distinct E007d register state and E007v DMI state. Validation requires startup phase to equal packet index and the scalar request ID to equal the packet semantic request ID. The request ID is explicit; it is not derived from packet number.

Therefore the live closure must establish producer -> common-calculation scalar output -> packer for coherent startup/request states, rather than capture one arbitrary steady AWB snapshot.

## What prior E011 work does and does not close

E011N and E011R close request-1 AEC/AWB **statistics-control** producer/consumer paths. They do not prove the Demux/PDPC/WB gain scalars above. E011T/U/V/W close AF/BF and are not repeated here.

## Next live evidence contract

When PiMaster/SP11 Windows is reachable again:

1. statically reduce the three common-calculation call paths far enough to identify their AEC/AWB/request input fields and request identity;
2. use a fresh one-shot E011X live identity and fresh KDNET only if kernel correlation is required;
3. observe the bounded first startup/request calculations at the common-calculation and packer boundaries;
4. retain raw OEM bytes, process addresses and debugger transcripts privately on SP11;
5. privately compare the produced scalar/packed outputs against the retained E006a startup corpus and publish only aggregate equality plus stable RVAs/scalar relationships;
6. close neutral-3A only when producer provenance and request/phase binding are proved.

LSC/GTM remains a distinct following gate: first-frame lux/CCT/Tintless input for the clean LSC producer and initial TMC semantic inputs for the clean GTM producer. VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains separate.

## Safety

No native camera module was installed or loaded. No Linux rear camera access, MMIO write, DMI submission, RT-CDM submission or reboot occurred. Native rear ISP runtime remains denied.
