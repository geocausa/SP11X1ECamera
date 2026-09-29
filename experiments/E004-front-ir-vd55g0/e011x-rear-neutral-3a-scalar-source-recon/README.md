# E011X - rear neutral-3A scalar bootstrap closure

Parent Git: `b15e23a623f0879ec127cd09ad470b9821bfba61` (E011W). Source-only E011X checkpoint Git before this live closure: `683b21194ef770e1103119ae053e7ae96dabd020`.

Status: **SOURCE + LIVE + PRIVATE-AGGREGATE CLOSED. REAR NEUTRAL-3A SCALAR BOOTSTRAP GATE CLOSED.**

## Scope

E011W closed AF/BF bootstrap timing. E011X then source-locked the rear Demux/BLS141, PDPC311 and WB201 dependence layouts and the exact Titan680 packing boundary. This closure adds one fresh bounded Windows rear4K trace and compares the source-derived scalar outputs against the retained private E006a startup command corpus.

Captured Windows register words and command bytes remain validation-only. No captured scalar register value is promoted as policy.

## Exact installed authority

The installed source authority remains:

- `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`;
- rear `com.surface.tuned.rfc_ov13858.bin` SHA-256 `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`.

Sensor2/Video inherits the Default Demux/BLS14, PDPC31 and WB20 tuning records; no rear-sensor or Video override was found for those three modules. Raw tuning words and decoded leaf values remain private.

## Source-locked scalar producers

The exact common-calculation boundaries are unchanged:

- Demux/BLS141 common calculation RVA `0x998E70`, Titan680 packer `0xB42840`;
- PDPC311 common calculation RVA `0x9C07C0`, interpolation `0x943E80`, packer `0xB3C7D0`;
- WB201 common calculation RVA `0x995E60`, packer `0xB560C0`.

Demux consumes the request-time post-sensor gain plus four interpolated BLS terms and four channel terms, applies the exact `16383/(16383-BLS)` normalization, and quantizes four Q10 outputs. WB consumes G/B/R plus `predictiveGain` and quantizes `round(channel_gain * predictiveGain * 1024)`. PDPC consumes the same AWB tuple and produces Q12 ratios in the accepted order R/G, B/G, G/R, G/B.

The Linux E006z boundary remains the semantic target: four Demux Q10 values, four PDPC Q12 values, WB B/R Q10, and explicit startup/request identity.

## Fresh live identity E011X-1412A

A fresh original Windows rear Color VideoRecord NV12 3840x2160 session was staged so the debugger attached after initialization and before `StartAsync`. The trace used the exact primary IFE request hook RVA `0x746F18` and the three common-calculation RVAs above.

Each breakpoint was bounded to eight hits and then self-disabled. The trace observed:

- eight atomic request hooks with sequential request IDs 1 through 8;
- eight Demux common-calculation entries;
- eight PDPC common-calculation entries;
- eight WB common-calculation entries;
- one stable four-term rear BLS input tuple across the sampled window;
- one stable four-term Demux channel-input tuple across the sampled window;
- `predictiveGain == 1.0` for all eight sampled WB calculations;
- coherent request-time dGain and AWB evolution across the atomic trigger and common-calculation boundaries.

The event order also exposes the startup hold behavior: one scalar calculation occurs before request 1, request 1 and request 2 each produce a new scalar state, and no scalar common-calculation update occurs between the request-3 and request-4 atomic hooks. Therefore request 3 holds the preceding scalar state rather than inventing a fourth scalar set.

The holder completed cleanly:

- `StartAsync`: Success;
- `StopAsync`: PASS;
- valid rear 4K handles: 1,807;
- debugger detached normally.

Raw debugger output, process addresses and holder transcripts remain private.

## Private E006a comparison

The retained private E006a corpus was recovered from SP7 and transferred to SP11 with exact SHA-256 preservation. The existing E006a decoder was used; no packet bytes or captured register values were emitted publicly.

Startup scalar coverage is exactly the coverage already implied by E006z's 26 scalar round-trip checks:

| startup phase | scalar register instances present | source-derived live match |
| --- | ---: | ---: |
| 0 | 8 | 8/8 |
| 1 | 8 | 8/8 |
| 2 | 8 | 8/8 |
| 3 | 2 | 2/2 |

Phase 3's only scalar registers are Demux `0x3B70` and `0x3B74`; PDPC/WB scalar registers are absent from that 0x658 MAIN. Those two Demux words exactly match the held preceding Demux calculation. Total: **26/26 exact scalar register instances**.

This is an output comparison only after the producer inputs, formulas and request ordering were independently source/live established. The E006a captured words remain validation evidence, not bootstrap constants.

## Closure

The neutral-3A scalar gate is closed:

- rear tuning provenance: closed;
- Demux request-time gain/BLS/channel producer boundary: closed;
- AWB G/B/R and WB `predictiveGain` producer boundary: closed;
- PDPC AWB-ratio producer boundary: closed;
- startup scalar phase/hold schedule: closed;
- all E006a startup scalar instances reproduced from semantic inputs: 26/26 exact.

This does **not** close the complete E008o packet semantic objects. Request-tagged LSC selectors 1/2 and GTM still need their initial semantic inputs, and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains a separate hardware gate.

## Next

Proceed to the next semantic gate: request-tagged LSC/GTM initial state.

- LSC: close the first-frame lux/CCT/Tintless inputs feeding the already-clean E007h/E007i producer/handoff.
- GTM: close the initial TMC TUNE/RUNTIME/COMMON/CTRL/FACE inputs feeding E007p/E007q.
- Preserve four independent E008o startup packet semantic objects and explicit request tags.
- Keep VFE1 WM16 same-generation retirement/lifecycle separate.

## Safety

No native Linux rear camera access occurred. No native camera module was installed or loaded. No MMIO write, DMI submission or RT-CDM submission occurred. Native rear ISP runtime remains denied.
