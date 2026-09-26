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


## Build result — PASS

The isolated E006j build completed against the pinned accepted CAMSS source with E006g and E006j injected together.

- W=1: zero warnings/errors
- qcom-camss.ko bytes: 13,553,664
- qcom-camss.ko SHA-256: 9fce856515f9fb52dd14ba55696e938f94d3e2908d21374f880dc830868b6c85
- vermagic: exact protected Golden kernel
- E006g materializer recipe retained
- E006j register binding recipe retained
- E006j dynamic register map: 25 entries
- producer families: 10
- unresolved owners: 0
- BPC_ABF register set: 0x4958, 0x495C, 0x49B8, 0x49BC

No module install/load, camera stream, RT-CDM submission, MMIO write or boot mutation occurred.

Status: **COMPILE-ONLY PASS**.

### Next

Close startup MAIN composition without treating one captured Windows startup value set as immutable truth. Prefer a fully symbolic startup register recipe first, then source-bind its producer ownership before any runtime integration.

Native rear Linux processed ISP remains **DENIED**.
