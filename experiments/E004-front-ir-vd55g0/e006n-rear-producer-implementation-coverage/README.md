# E006n — rear producer implementation coverage and reuse matrix

Parent Git: `f62966d0` (E006m startup+steady binding compile PASS).

Status: **OFFLINE GAP AUDIT PASS**. No camera runtime or build mutation.

E006g–E006m closed packet structure, DMI ownership, all 25 steady dynamic register owners, and all 714 startup register owners. E006n asks a different question: **which callbacks already have a usable Linux/clean-room implementation, and which are only named contracts?**

## Reusable clean-room/front work

The mature front lineage is not merely a Windows replay:

- **Demux/BLS** — independent clean arithmetic exists; rear needs rear black-level/channel tuning and live gain state.
- **PDPC/WB** — independent scalar packers exist; rear needs rear AWB/calibration/live state.
- **LSC/Tintless** — the active front Tintless algorithm and Titan680 LSC/GIC packing are clean-room; rear still needs its own tuning/golden/OTP/geometry and live Tintless stats/descriptors.
- **GIC** — no separate algorithm is needed on this Surface; E006d proves the rear uses the same LSC wire alias.
- **GTM** — clean-room transform + Titan680 packing exists; rear needs live TMC/ADRC state and rear tuning/domain authority.
- **bank selection** for PDPC/LSC/GIC/BPC_ABF/GTM/Gamma/DSX already exists as a request-parity rule.

The front GO run proved a bounded 27-frame live producer path with R5..R27 IQ consumption and all producer pipelines under one 33.3ms frame period. That is useful engineering reuse, **not** evidence that front tuning values may be used for rear.

## Partial/open steady producers

- **Gamma** — bank rule exists; clean rear LUT generation is still open.
- **DSX** — bank rule exists; clean rear payload generation from rear/output geometry is open.
- **BPC_ABF** — front bank rule exists, but rear requires full BPCABF411 calculation, including E006i's 0x49B8/0x49BC and startup 0x49D0..0x49E0.
- **BFStats25** — ownership/packing is closed, but AF-derived ROI/gamma/register production remains open.

## Startup-only families

Most startup-only words are phase-invariant and therefore look like role/geometry/configuration state, not continuously changing 3A algorithms:

- BC101, BayerGTM101, BayerLTM101, LCAC111, CST12, UVGamma101
- MNDS23, RoundClamp12, Crop12

The stats families need explicit request/phase configuration:

- AECBEStats17 — 9/18 words vary across startup
- BHistStats16 — 1 startup-different word
- TintlessBGStats17 — startup-only but phase-invariant in E006a
- AWBBGStats17 — 7/18 words vary
- RSStats14 — 3/4 words vary
- BFStats25 — startup register state varies heavily

`0x008C` is VFE680 `PERIOD_CFG` transport state and must be supplied by Linux stream state, not an IQ/tuning producer.

## Largest immediately implementable block

**468 of 714 startup registers are already safe to implement now.**

E006l proves each of those 468 startup values is identical to a committed E006h steady singleton observation in every startup occurrence. No private Windows bytes or new oracle run are needed. The next experiment should therefore turn those committed safe observations into a deterministic compile-only C lookup provider.

This reduces the unknown implementation surface before touching 3A algorithms.

Native rear Linux processed ISP remains **DENIED**.
