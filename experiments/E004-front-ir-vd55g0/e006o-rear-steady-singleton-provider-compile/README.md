# E006o — compile-only 468-register rear steady-singleton provider

Parent Git: `8936b623` (E006n implementation coverage audit).

Status: **STAGED / COMPILE-ONLY**.

## Objective

Implement the largest already-safe rear startup value provider before touching any new 3A algorithm.

E006l proved that **468 of the 714 unique startup registers** have exactly the same value as a committed E006h steady `STABLE_OBSERVED` singleton in every startup occurrence.

E006o generates a sorted C lookup table directly from those two committed safe artifacts:

- E006h `STEADY-SYMBOLIC-RECIPE.json`
- E006l `STARTUP-REGISTER-OWNER-MAP.json`

Generation refuses any register with zero or multiple E006h values.

## Privacy/provenance

No private E006a corpus is read. No Windows buffer, pointer, IOVA or command packet is consumed.

The 468 values are not newly imported evidence: they are the same derived hardware register observations already committed in E006h and separately proven reusable by E006l.

## Runtime boundary

The provider has the exact E006m callback type, but is retained only for compile/link inspection. There is no runtime caller and no module installation/load.

A passing build means 468/714 startup values have an actual compiler-checked provider. It does **not** authorize rear RT-CDM submission or native rear ISP runtime.

Native rear Linux processed ISP remains **DENIED**.

## Build result — PASS

The single E006o isolated build passed after re-verifying E006g, E006j, E006l, E006m and E006o.

- 468/468 safe singleton entries exactly match E006h
- W=1: zero warnings/errors
- qcom-camss.ko: 13,576,664 bytes
- SHA-256: f94bbdf3d41344549c980e1a757005c4d9284be9af29fc9743e43a3b5b6cc3c7
- vermagic: exact Golden
- singleton table + lookup + prior E006g/E006j/E006m recipes retained

No module install/load, camera access, RT-CDM submission, MMIO write or boot mutation occurred.

Status: **COMPILE-ONLY PASS**. An actual provider now exists for 468/714 startup registers.
