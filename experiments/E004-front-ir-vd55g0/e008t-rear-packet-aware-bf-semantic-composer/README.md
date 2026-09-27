# E008t — rear packet-aware BF semantic composer

Parent Git: `27dde4e79feb19f7dab5ac6807fc85d9d52c123a` (E008s).

Status: **OFFLINE SEMANTIC COMPOSER PASS / NO CAMERA RUNTIME**.

## Purpose

E008o made each of the four rear startup packets own independent register and
DMI semantic state. E008q/r/s then source-closed the BFStats25 bootstrap
policy. E008t finally writes those source-derived BF semantics into the four
isolated E008o packet states.

This is deliberately **not** a final RT-CDM/DMI parity checkpoint. The
BFStats25 ROI boundary validation/adjustment step remains downstream of the AF
seed and can alter the final selector-1 ROI payload. E008t therefore composes
the clean semantic seed only and keeps final selector-1 byte parity gated.

## Packet-aware state

Packet 0 uses the IFENode hardcode fallback source-locked by E008s:

- LUT banks: phase 0;
- gamma disabled;
- scale disabled;
- hardcode 13-tap FIR enabled;
- hardcode H1/V IIR coefficients;
- IIR shifts **-3 / 0**;
- hardcode coring profile;
- hardcode centered 5x5 ROI seed;
- BF selector-2 gamma state remains invalid.

Packets 1–3 use normal rear AF/BAF Default tuning:

- LUT banks: phases 1 / 0 / 1;
- gamma preset 0 enabled;
- scale disabled;
- FIR disabled;
- normal rear H1/V IIR coefficients;
- IIR shifts **3 / 3**;
- normal coring preset 0;
- centered 25% HAF default window split into the normal 5x5 zero-overlap ROI
  semantic seed.

The unchanged input/luma hardware selections remain zero in both phases,
matching the source-initialized policy and the private phase validation from
E008s.

## Source generation

`generate-e008t.py` derives the committed include from only:

- pinned `QcDeviceMFT8380.dll`;
- pinned `com.surface.tuned.rfc_ov13858`;
- the existing clean chromatix container decoder.

The packet0 hardcode coefficient block comes from the pinned DeviceMFT source
at the E008s-identified RVA. Normal gamma/IIR/coring values come from the
selected rear tuning records. Captured Windows register values and DMI bytes
are not inputs to generation and are not embedded.

## ROI boundary

E008s proved two distinct upstream seed policies:

- packet0: IFENode hardcode centered 5x5 construction;
- packet1+: AF HAF centered 25% window, 5x5, zero overlap.

Private validation also showed that the final selector-1 payload is not a
single frozen byte image: BFStats25 performs a downstream ROI
validation/adjustment pass and startup/steady payload hashes differ.

E008t therefore fills the semantic ROI seed and stops there. The next
checkpoint must either source-implement the BFStats25 ROI adjustment in the
offline path or prove an equivalent Linux adjustment before final command
materialization can claim BF DMI parity.

## Isolation

E008t is additive and has no ordinary driver call site. It does not modify
E007 or E008o historical files. The host-only harness instantiates simplified
copies of the already-existing state wrappers, includes the real E007b/E007e
packers plus the generated E008t composer, and verifies:

- four independent packet states;
- bank sequence 0/1/0/1;
- packet0 gamma rejection on selector 2;
- packet1+ gamma production;
- 25 ROI records for every semantic seed;
- packet0 versus normal BC60 FIR/gamma/IIR phase bits.

No module is installed or loaded.

## Safety

No MMIO, DMA, RT-CDM submission, camera activation, reboot, V4L2/probe
attachment or autostart change. Golden, rear fallback, front and IR-off
policies are unchanged.
