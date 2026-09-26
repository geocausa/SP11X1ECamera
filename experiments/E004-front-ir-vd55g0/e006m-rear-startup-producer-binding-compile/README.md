# E006m — compile-only rear startup producer binding

Parent Git: `daf6885f` (E006l startup register ownership PASS).

Status: **STAGED / COMPILE-ONLY**. No runtime authorization.

## Objective

Make E006l's complete 714-register startup ownership model compiler-visible together with the already-passing E006g payload/DMI materializer and E006j steady dynamic producer binding.

The generated startup table is exhaustive and sorted:

- 468 registers -> safe steady-singleton provider;
- 25 registers -> exact E006j steady dynamic dispatch;
- 35 startup-vs-steady differences -> existing shared producer callbacks (PDPC, WB, BPC_ABF, BFStats25);
- 186 startup-specific callbacks -> 184 startup-only registers plus BHistStats16 and VFE680 PERIOD_CFG.

Startup-specific module callbacks cover:
BC101, BayerGTM101, BayerLTM101, LCAC111, CST12, UVGamma101, MNDS23, RoundClamp12, Crop12, AECBEStats17, BHistStats16, TintlessBGStats17, AWBBGStats17 and RSStats14.

`0x008C` has its own `VFE680_PERIOD_CFG` callback and is never treated as an IQ constant.

## Safety

No Windows value, pointer, IOVA or command byte is embedded. The contract contains register addresses and owner identities only.

The generated include is injected into an isolated copy of accepted CAMSS solely for W=1 compilation. Its retained recipe has no runtime caller. The build script performs no install, module load, stream, RT-CDM submission, MMIO write, boot change or camera access.

Passing this experiment closes **compiler-visible startup ownership/binding**, not implementation of all algorithms/providers.

Native rear Linux processed ISP remains **DENIED**.

## Build result — PASS

The single isolated E006m build completed against the pinned accepted CAMSS source.

All prerequisite contracts re-verified before compilation:

- E006g DMI/payload materializer: PASS
- E006j steady dynamic producer binding: PASS
- E006l startup ownership partition: PASS
- E006m 714-register dispatch table: PASS

Build result:

- W=1: zero warnings/errors
- qcom-camss.ko: 13,569,320 bytes
- SHA-256: aec7dee1d2aad766e3bfc484199dcdc21830362bbaa23cdefa92561d4593698f
- vermagic: exact protected Golden kernel
- retained compiler-visible contracts include E006g, E006j and E006m recipes.

No module installation/load, camera stream, RT-CDM submission, MMIO write or boot mutation occurred.

Status: **COMPILE-ONLY PASS**.

The rear command topology plus steady/startup ownership is now compiler-closed. What remains is producer/state implementation and later guarded runtime integration. Native rear processed ISP remains **DENIED**.
