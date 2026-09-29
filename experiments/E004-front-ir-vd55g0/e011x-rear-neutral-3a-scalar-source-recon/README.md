# E011X — rear neutral-3A scalar source reconnaissance

Parent Git: `b15e23a623f0879ec127cd09ad470b9821bfba61` (E011W). Evidence class: exact installed-source/static reduction only. No new Windows live identity was consumed and no native rear ISP runtime occurred.

Status: **STATIC INPUT/DEPENDENCE REDUCTION CLOSED; LIVE REQUEST/PHASE BINDING OPEN.**

## Scope

E011W closed the remaining AF/BF bootstrap timing question. E008p therefore leaves neutral AEC/AWB scalar state as the next semantic gate before request-tagged LSC/GTM.

This stage does **not** reuse retained Windows startup register words as bootstrap policy. E008p's rule still applies: a packer output is not its semantic producer. Private E006a startup outputs remain validation-only after a source-backed producer is identified.

## Exact installed authority

The current Windows DriverStore copies were re-verified before analysis:

- `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`;
- rear `com.surface.tuned.rfc_ov13858.bin` SHA-256 `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`.

The rear tuning selector graph proves that the Sensor2/Video branch inherits the **Default** records for all three neutral-scalar modules. There is no rear-sensor or Video override for:

- `demuxblklevel14_ife_v2`;
- `pdpc31_ife_v2`;
- `wb20_ife_v2`.

Safe structural fingerprints:

| Module | Root bytes | Root SHA-256 | Non-empty leaf bytes | Leaf SHA-256 |
| --- | ---: | --- | ---: | --- |
| Demux/BLS14 | 64 | `74d7414241013b4470cbe88be9abcaba4f5d59dcae3a1d780855ed67ddc6c817` | 16 | `e1f38cb569bd193ee5f6cedb5a938a5b6a579302a0f9f0366e36cf5b8a9a2f98` |
| PDPC31 | 96 | `081f03e9a7f286b77f83f8e90186555a267d90de633103278020516a565704fc` | 24 | `ccd305f45ef9b5cc3c82bb09dbf239f85239ed261a75a908d10d33107dc42160` |
| WB20 | 56 | `2822385e43c9bf7629dd8c1cbf179f1e5fa21552d2c13cf32b0e1dcfba2a11ea` | 32 | `adaa0328a8d4f654c50b317d314627c9bc406be495768f35066f291633b568ae` |

The raw tuning words and decoded leaf values remain private and are not committed.

## Exact neutral-3A scalar boundary

The accepted E006z provider fixes the Linux semantic object shape:

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

## Exact common-calculation dependence layouts

Offline ARM64 disassembly of the exact installed DeviceMFT removes the remaining structural ambiguity.

### Demux/BLS141 common calculation — RVA `0x998E70`

At entry:

- dependence input is `x0`;
- request-time ISP/post-sensor gain is float `x0 + 0x1C`;
- pixel/Bayer selector is read from `x0 + 0x10`;
- interpolated four-term BLS input is `x1[0..3]`;
- four channel terms are `x2[0..3]`;
- calculated output is `x4`.

The common routine applies the already source-locked `16383/(16383-BLS)` normalization, multiplies by request-time gain and channel terms, then quantizes the four Q10 channel outputs. Rear tuning selection for the BLS/channel side is now static-source closed; the only live scalar still needed here is the request-time gain plus identity.

### WB201 common calculation — RVA `0x995E60`

At entry, dependence input is `x0` and the exact float layout is:

- `x0 + 0x10`: AWB G gain;
- `x0 + 0x14`: AWB B gain;
- `x0 + 0x18`: AWB R gain;
- `x0 + 0x1C`: `predictiveGain`.

The routine independently computes each channel as `round(channel_gain * predictiveGain * 1024)` before Titan680 packing. This pins `predictiveGain` as a first-class request dependence field rather than an inferred constant.

### PDPC311 common calculation — RVA `0x9C07C0`

The existing E006z/E003h proof remains authoritative for the four Q12 AWB ratios and their Titan680 packing. Rear tuning selection is now also source-closed to the inherited Default PDPC record, so the remaining live evidence is the coherent AWB request state and request/phase identity, not a rear-specific tuning override.

## Atomic request boundary available for the live proof

The exact primary IFE request hook recovered in E003h is valid for this same DeviceMFT image:

- `IFENode::ExecuteProcessRequest` complete trigger hook: RVA `0x746F18`;
- request/frame identity: `qwo(x26 + 0x3EF0)`;
- complete trigger block: `x26 + 0x3F78`;
- AWB G/B/R in that trigger block: `+0x3C / +0x40 / +0x44`;
- request-time sensor/ISP `dGain`: `dwo(x26 + 0x1F7C)`.

That gives the next live pass one coherent request identity plus the AEC/AWB inputs needed to correlate the common calculations.

## Four-packet identity requirement

E008o/E007y forbid collapsing startup into one mutable neutral state. Each of the four startup packets owns a distinct E007d register state and E007v DMI state. Validation requires startup phase to equal packet index and scalar request ID to equal packet semantic request ID. Request ID is explicit; it is not derived from packet number.

The remaining live closure must therefore prove producer -> common-calculation -> packed scalar for coherent startup/request states, not one arbitrary steady AWB snapshot.

## Next live evidence contract

Use a fresh one-shot E011X identity only after the environment is intentionally returned to Windows:

1. hook the bounded atomic request boundary at `0x746F18`;
2. correlate the first required startup/request identities with Demux `0x998E70`, WB `0x995E60`, and PDPC `0x9C07C0` or their already-pinned packers;
3. capture only semantic inputs/outputs needed to prove `dGain`, AWB G/B/R, `predictiveGain`, and request/phase identity;
4. use fresh KDNET only if user-mode request correlation proves insufficient;
5. keep raw OEM bytes, process addresses and debugger transcripts private;
6. privately compare produced scalar/packed outputs against retained E006a startup evidence and publish only aggregate equality plus stable RVAs/scalar relationships.

Neutral-3A remains open until live producer values and four-startup request/phase binding are proved. LSC/GTM remains the following semantic gate. VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains separate.

## Safety

No native camera module was installed or loaded. No Linux rear camera access, MMIO write, DMI submission, RT-CDM submission or reboot occurred. Native rear ISP runtime remains denied.
