# E011Y — rear startup LSC/GTM semantic binding

Parent Git: `8e7056d54f77704a2eb6d13f5d7e3222b944bf4e` (E011X neutral-3A closure).

Status: **WINDOWS SOURCE/LIVE STARTUP BINDING CLOSED; CLEAN OFFLINE REPLAY OPEN.**

## Scope

E011X closed the rear neutral AEC/AWB scalar bootstrap. E011Y now binds the two remaining adaptive first-frame families — LSC411/Tintless and TMC141/GTM131 — to the exact four-packet Windows startup schedule.

This checkpoint does not promote captured DMI bytes into Linux policy. The existing clean producers remain authoritative:

- E007g/E007h: rear OV13858 LSC/Tintless producer, already byte-exact for requests 4..18;
- E007p/E007q: clean TMC141 -> GTM131 producer/handoff;
- E006k/E008o: four independent startup packet semantic objects.

Private E006B source payloads are used only as final byte-equality validation.

## Exact source boundaries reused

Installed DeviceMFT SHA-256 remains
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

Pinned boundaries:

- atomic IFE request hook: RVA `0x746F18`;
- LSC411 CalculateSetting: RVA `0x88E1E8`;
- Tintless wrapper: RVA `0xC95FD0`;
- LSC post-calculation staging: RVA `0xA03B34`;
- TMC141 direct solver callsites: RVA `0x9241C0` and `0x924258`;
- GTM final cached staging: RVA `0xA290A8`;
- Titan680 LSC packer: RVA `0xB3D8A0`.

For LSC, the authoritative validation input is the 0x18A0 post-calculation staging object. Direct DMI pointers at the selected post hook can still be zero placeholders and are not used as proof.

## Fresh bounded Windows evidence

Three single-use rear `Color / VideoRecord / NV12 3840x2160` identities were consumed.

### E011Y-1610A — startup adaptive schedule

The first eight request IDs and the adaptive producer boundaries were observed in one stream. The primary run completed Start/Stop successfully with **1,865 valid 4K handles**.

Startup order:

1. before the first atomic request hook:
   - LSC calculation #0, request label 1;
   - TMC calculation state #0;
   - GTM output #0;
2. atomic request 1;
3. LSC calculation #1, still request label 1;
4. TMC calculation state #1 and GTM output #1;
5. requests 2 and 3 arrive with no new LSC or TMC solve;
6. request 4 is the first observed request-local Tintless callback and the next LSC/TMC update.

Thus the startup is a producer/hold schedule, not four unrelated adaptive snapshots.

### E011Y-1637B — LSC common-state ordering

A second bounded run confirmed both startup LSC calculations enter with the common Tintless-enable flag asserted, while the first actual Tintless wrapper callback is still not reached until request 4. The run completed Start/Stop with **1,454 valid 4K handles**.

The pre-request startup LSC calculations are therefore pre-Tintless materializations even though the module capability/common enable is set.

### E011Y-1641C — exact two LSC semantic triggers

A final micro-trace read only the per-call ISPInputData lux/CCT values at the first two LSC calculations:

| startup LSC state | request label | lux | CCT |
| --- | ---: | ---: | ---: |
| cold seed | 1 | 220.0 | 0.0 |
| populated request-1 seed | 1 | 232.247802734375 | 5000.0 |

The run completed Start/Stop with **533 valid 4K handles**.

No raw process addresses or memory dumps are committed.

## Startup LSC wire validation

The two observed LSC post-calculation staging objects were packed offline with the exact source-locked Titan680 packing law.

Private E006B comparison:

| startup phase | LSC DMI present | selector 1 | selector 2 | selector 3 |
| --- | --- | --- | --- | --- |
| 0 | yes | exact | exact | exact zero |
| 1 | yes | exact | exact | exact zero |
| 2 | no | n/a | n/a | n/a |
| 3 | no | n/a | n/a | n/a |

Phase 0 and phase 1 are genuine distinct active-bank semantic meshes, not one constant payload viewed through alternating banks. In each staging object the inactive bank is zero, while the active bank reproduces the corresponding E006B selector-1/selector-2 payload exactly.

Safe hashes:

- phase 0 selector1: `c5a990dc398e6926b2b53c1174219387837029a6051069f4ebc86fc74c8d440b`;
- phase 0 selector2: `ed004c388d9b0230c31ffc8b5ef8d54dd60d4f21c174837a10e46e3d62374293`;
- phase 1 selector1: `d8c34f9fc439253e06f30a2fee776c75034dc9206f75b34046351affc127d73e`;
- phase 1 selector2: `efa6f2616a6a56527d0d5605c405c5a5db7b8f65c6be84890f423d2953c0faa8`;
- selector3 zero payload: `6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e`.

These hashes are validation targets only; the startup producer must recreate them from source semantic state.

## Startup GTM semantic schedule and wire validation

The TMC input capture reuses E007o's bounded semantic ABI: TUNE / RUNTIME / COMMON / CTRL / FACE.

Two startup semantic states are required:

- **TMC seed state 0**, before the first atomic request;
- **TMC request-1 state 1**, after request 1.

For the documented fields, the meaningful transition is:

- runtime `+0x488`: 0.0 -> 1.0;
- control byte `+0x1C`: 0 -> 1.

The stable startup metadata includes mode `0x60800`, generation/common state 5, and no face state. The source tuning/common/face blobs are stable across the observed startup window.

Both TMC semantic states produce the same GTM wire payload, and no new TMC solve occurs for requests 2 or 3. All four startup GTM outputs therefore match the same E006B startup payload exactly:

`b71d4b3eadec95941586227f171e771ae5dc1c70fd48fa5ebf599dcf8fd77d81`

Startup GTM schedule:

- phase 0: TMC seed state 0 -> GTM seed;
- phase 1: request-1 TMC state 1 -> same GTM bytes;
- phase 2: hold state 1 -> same GTM bytes;
- phase 3: hold state 1 -> same GTM bytes.

Again, captured GTM bytes are validation only; E007p/E007q remain the clean producer authority.

## What is closed / what remains

Closed on the original Windows stack:

- exact four-phase LSC DMI presence schedule;
- exact two startup LSC semantic trigger states;
- exact startup LSC staging -> Titan680 payload equality to E006B;
- exact two-state TMC semantic startup transition;
- exact GTM phase-0/1 solve plus phase-2/3 hold schedule;
- exact four-phase GTM payload equality to E006B;
- request-4 boundary where normal sequential Tintless state begins.

Still open before the complete E008o semantic objects can be declared source-generated:

- run the two startup LSC seeds through the clean rear LSC upstream path offline and require the phase-0/1 safe hashes above;
- run the two startup TMC semantic states through the clean E007p/E007q chain offline and require the common GTM safe hash above;
- bind those produced states into the four explicit E008o packet objects and validate phase/request ownership.

That next step is offline only and should be performed on SP11 Linux. It does not authorize a native rear camera run.

## Safety

No Linux camera access occurred in this checkpoint. No native camera module was installed or loaded. No MMIO write, DMI submission or RT-CDM submission occurred. Raw debugger transcripts, bounded input dumps and process addresses remain private. Native rear ISP runtime remains denied.
