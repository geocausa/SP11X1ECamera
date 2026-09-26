# E006h — rear steady MAIN symbolic normalization and offline composer

Parent Git: 37c34f1f (E006g compile-only rear materializer contract PASS).

Status: STAGED / OFFLINE ONLY.

## Goal

Convert the private E006a selected steady MAIN representatives into a safe symbolic command recipe without committing raw Windows command buffers, captured DMI addresses, or observed values for registers already proven request-varying.

The normalizer keeps:

- REG_CONT command grouping and register offsets;
- stable register values as derived hardware register observations;
- DMI register/selector/payload length;
- command offsets needed to verify exact layout.

It replaces:

- every captured DMI address with a symbolic payload source;
- every register offset proven request-varying by E006a with a dynamic producer slot.

The four steady representatives are AC8, A98, 8F0 and 658.

## Safety boundary

This experiment does not authorize startup composition, RT-CDM submission, module loading or rear ISP runtime. It is an offline command-composition proof only.

The private selected corpus stays outside Git and is deleted from SP11 cache after normalization. The original private corpus remains on SP7.

Native rear Linux processed ISP remains DENIED.

## Result — OFFLINE SYMBOLIC COMPOSE PASS

The private selected E006a representatives were reduced once into a safe symbolic recipe and the temporary SP11 cache copy was then deleted. The original private evidence remains on SP7 only.

Per steady MAIN variant:

- AC8: 2760 bytes, 72 commands, 530 register writes, 16 DMI slots
- A98: 2712 bytes, 69 commands, 525 register writes, 15 DMI slots
- 8F0: 2288 bytes, 50 commands, 459 register writes, 13 DMI slots
- 658: 1624 bytes, 29 commands, 345 register writes, 3 DMI slots

The offline composer uses only:

- committed stable register observations;
- symbolic producer-backed register values;
- symbolic Linux-owned DMI addresses;
- DMI register/selector/length descriptors;
- the invariant CDM DMI header middle byte derived from the command format.

It does not use raw Windows command bytes at compose time.

For every variant, the independently emitted command packet is deterministic across two runs, decodes to the exact E006a command/register/DMI shape, and after zeroing all global producer-backed register fields plus DMI address fields its SHA-256 matches the equivalently normalized private representative exactly.

This stronger global-symbolic normalization is required because a register may be producer-driven globally even if it happened not to change across the limited samples of one MAIN variant.

Safe-recipe audit confirms:

- no captured DMI address is committed;
- no observed value is committed for a request-varying register slot;
- no raw Windows command/payload bytes are committed;
- the temporary private E006a copy on SP11 was deleted after reduction.

Two dynamic register offsets still lack a named producer owner:

- 0x49B8
- 0x49BC

They remain symbolic and therefore cannot be accidentally frozen.

Status: **OFFLINE SYMBOLIC COMPOSE PASS**. Startup composition and all Linux rear RT-CDM runtime remain unauthorized.

### Next

Source-lock the exact owner/producer semantics of 0x49B8 and 0x49BC. Then bind the steady symbolic register slots to accepted producer interfaces and compile that integration offline before addressing startup MAIN composition.


## E006i ownership closure

E006i source-locked the last two unnamed dynamic register offsets:

- 0x49B8 -> BPC_ABF411 calculated register word
- 0x49BC -> BPC_ABF411 calculated register word

Both are emitted inside IFEBPCABF411Titan680's 0x49A0..0x49BC register range and are packed by the same request-time BPCABF411 calculated-setting path. The symbolic recipe now labels them BPC_ABF rather than unresolved; their values remain symbolic and are not frozen.

There are now **zero unnamed dynamic register owners** in the E006h steady recipe. This closes ownership, not the Linux implementation of the complete BPCABF411 algorithm.
