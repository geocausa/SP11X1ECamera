# E006j — compile-only rear steady producer binding

Parent Git: 98364b02 (E006i BPC/ABF411 scalar ownership PASS).

Status: STAGED / COMPILE-ONLY.

## Objective

Bind every request-varying steady rear IFE register in the safe E006h symbolic recipe to an explicit producer family, and compile that binding together with the E006g DMI/payload materializer contract.

The safe recipe contains 25 dynamic register offsets across 10 producer families:

- DEMUX_BLS
- PDPC
- LSC
- WB
- GIC
- BPC_ABF
- GTM
- GAMMA
- DSX
- BFSTATS25

E006i closes the final two unnamed offsets, so BPC_ABF owns:

- 0x4958
- 0x495C
- 0x49B8
- 0x49BC

The first two are the already-known bank words. The latter two are BPC/ABF411 calculated-setting words.

## Contract

E006j generates the register-owner table directly from E006h. No dynamic register value is embedded.

The compile-only producer bundle contains:

- E006g payload/DMI producer hooks;
- E006j scalar-register producer hooks.

Validation rejects a missing producer callback and specifically asserts that 0x49B8/0x49BC are BPC_ABF-owned.

This closes **binding/ownership**, not implementation of all producer algorithms.

## Safety

The generated include is injected only into an isolated copy of accepted CAMSS source. The retained binding recipe has no runtime caller. The build script performs no install, module load, camera stream, RT-CDM submission, MMIO write or boot mutation.

Native rear Linux processed ISP remains DENIED.
