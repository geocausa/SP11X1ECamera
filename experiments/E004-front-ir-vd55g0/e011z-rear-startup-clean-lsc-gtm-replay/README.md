# E011Z — rear startup clean LSC/GTM replay and E008o adaptive binding

Parent Git: `180bfee4b58d7831e378f9a09df21ef658b7627e` (E011Y).

Status: **CLEAN STARTUP LSC/GTM REPLAY CLOSED; E008o ADAPTIVE BINDING DEFINED; COMPLETE E008o BASE-OBJECT COMPOSITION STILL OPEN.**

E011Y established the Windows startup schedule. E011Z reproduces those adaptive startup payloads without using captured Windows DMI bytes as producer inputs, then defines how the clean-produced payloads are installed into the four packet-isolated E008o semantic objects.

## Clean LSC startup replay

The replay uses the accepted E007h rear/default OV13858 LSC authority: serialized LSC41 leaves, golden/calibration authority, the source-locked rear geometry resampler and Titan680 LSC wire packer. Tintless is deliberately not invoked for startup because E011Y proved the first actual request-local Tintless callback occurs at request 4.

Two startup states reproduce E011Y/E006B exactly:

- phase 0: producer lux 220.0, CCT 0.0; first lower-CCT leaf 0x29c;
- phase 1: producer lux 232.247802734375, CCT 5000.0; leaf 0x2a0.

The exact `LSC411Interpolation::RunInterpolation` implementation at RVA `0x93C1B0` closes the cold-CCT rule: interval selection initializes lower/upper child indices to 0/0 and ratio to 0, and only changes them on a matching interior/later interval. A trigger below the first serialized [1,3100] CCT region therefore selects child 0 without extrapolation.

Hashes:

| phase | selector 1 | selector 2 |
| --- | --- | --- |
| 0 | `c5a990dc398e6926b2b53c1174219387837029a6051069f4ebc86fc74c8d440b` | `ed004c388d9b0230c31ffc8b5ef8d54dd60d4f21c174837a10e46e3d62374293` |
| 1 | `d8c34f9fc439253e06f30a2fee776c75034dc9206f75b34046351affc127d73e` | `efa6f2616a6a56527d0d5605c405c5a5db7b8f65c6be84890f423d2953c0faa8` |

Selector 3 is the already-closed zero payload, SHA-256 `6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e`.

Phases 2/3 contain no LSC DMI. For recursive E007v validation the E008o objects hold the phase-1 LSC state; those bytes are not materialized by the packet-2/3 command shapes.

## Clean GTM startup replay

The normal E007p/E007q valid-TMC producer is intentionally *not* the startup GTM source. Private E011Y timing showed the first four startup GTM outputs precede the normal request-4 valid-TMC curve.

The source-locked pre-valid-TMC GTM region is 257 points of 4096.0. Feeding that region through the accepted clean Titan680 GTM packer produces exactly 2048 bytes with SHA-256:

`b71d4b3eadec95941586227f171e771ae5dc1c70fd48fa5ebf599dcf8fd77d81`

That is the E011Y/E006B startup GTM hash for all four phases. Thus the startup law is static GTM seed for phases 0..3; normal valid-TMC post-processing begins at the request-4 update.

## E008o binding

`camss-e011z-rear-startup-adaptive-bind.inc` decorates four already coherent non-adaptive E008o packet objects. It does not invent request IDs.

For every packet:

- the caller-supplied E008o request ID must already be >=4 and coherent with the scalar request tag;
- startup phase remains exactly the packet index;
- LSC/GTM handoff request IDs are set to that same packet request ID;
- phase 0 receives LSC state 0;
- phases 1/2/3 receive LSC state 1 (2/3 are validation-only holds because their packet shapes contain no LSC DMI);
- every phase receives the same clean static GTM seed;
- final recursive E008o/E007v validation is required before success.

This deliberately keeps the Windows producer's internal request label (1 during the two startup LSC calculations) separate from the Linux materializer request identity. The latter remains caller-owned and is never derived from the packet number.

## Binding compile check

The E008o adaptive binder passed a host structural compile/run check with the exact nested ownership shape `E007v -> E007u -> E007t -> E007s -> E007q -> E007i`. Four distinct caller-owned materializer request IDs (4, 5, 6, 7) were exercised simultaneously; each remained independent of packet phase and propagated coherently into the nested LSC/GTM request tags.

This is a structural/offline check, not a kernel-module or runtime test.

## Remaining gate

The adaptive LSC/GTM portion is now source-generated. The remaining E008o task is to assemble the already-closed non-adaptive bootstrap semantics (neutral scalars, statistics/AF-BF state, period/register state and stable DMI providers) into the same four base packet objects and pass the complete E008o validator/materializer offline.

VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains a separate hardware gate after semantic composition.

## Safety

Offline only. No module install/load, Linux camera access, MMIO, DMI submission or RT-CDM submission occurred. Native rear ISP runtime remains denied.

E011AG integration portability note: the flat startup curve has zero slopes, so the clean packer output is independent of coordinate-grid values. Replay now supplies a canonical increasing grid, checks an irregular grid for the same result, and checks the existing startup hash. It does not need the private normal-TMC domain binary; normal adaptive GTM is unchanged.
