# E006k — fully symbolic rear startup MAIN normalization and offline composer

Parent Git: e0e10433 (E006j steady producer binding compile PASS).

Status: STAGED / OFFLINE ONLY.

## Goal

Close the **structural** startup MAIN composition problem without promoting a single Windows startup register snapshot into Linux constants.

All register values in all four startup MAINs are symbolic. All DMI addresses are symbolic. The safe recipe retains only:

- CDM command order/grouping;
- register offsets and counts;
- DMI command invariant header bits;
- DMI register/selector/payload lengths;
- named DMI producer families.

The independent offline composer must reproduce the exact private startup packet after both packets are normalized by zeroing every register value field and every DMI address field.

## Startup DMI ownership

Known families are:

- 0x3D08 -> PDPC
- 0x4308 -> LSC
- 0x4708 -> Surface LSC/GIC wire alias
- 0x4908 -> BPC_ABF
- 0x5A08 -> GTM/TMC
- 0x5F08 -> Gamma
- 0xA008 / 0xA208 -> DSX
- 0xBC08 -> BFStats25

E006k also source-locks startup-only 0xB208 to **BHistStats16**:

CamX::IFEBHistStats16Titan680::CreateCmdList emits:

- selector 1, 0x1000 bytes
- selector 2, 0x50 bytes

matching E006a startup MAIN 1 exactly.

## Safety

The selected private E006a corpus is used only for one-way normalization in SP11 private cache and is deleted immediately afterward. Raw bytes, captured addresses and captured startup register values are never committed.

This experiment closes structure only. Startup register producer ownership/integration remains a later step.

Linux rear RT-CDM submission and native processed rear ISP remain **DENIED**.


## Result — OFFLINE FULLY SYMBOLIC STARTUP COMPOSE PASS

The four startup MAIN representatives were normalized once from the private E006a selected corpus, and the temporary SP11 cache copy was deleted immediately afterward.

Results:

- startup1 MAIN 0xF1C: 3,868 bytes, 118 commands, 714 register writes, 17 DMI slots
- startup2 MAIN 0xEBC: 3,772 bytes, 111 commands, 705 register writes, 16 DMI slots
- startup3 MAIN 0xA00: 2,560 bytes, 63 commands, 504 register writes, 10 DMI slots
- startup4 MAIN 0x658: 1,624 bytes, 29 commands, 345 register writes, 3 DMI slots

Total startup register-value slots: **2,268**. Every one remains symbolic.

All startup DMI sources are named; unresolved DMI sources: **0**.

For each startup MAIN, the independent composer:

- uses synthetic register values only;
- uses synthetic DMI addresses only;
- reproduces the exact command count/register-write count/DMI shape;
- is deterministic across repeated composition;
- matches the private representative exactly after both are normalized by zeroing every register-value field and every DMI address field.

No raw Windows command bytes, captured addresses or captured startup register values are committed.

This closes startup **structure/composition**, not startup register-value producer implementation.

Status: **OFFLINE FULLY SYMBOLIC STARTUP COMPOSE PASS**.

### Next

Compile a combined rear startup+steady command contract that accepts startup register values only through an explicit provider callback and uses the already named DMI producer families. Keep the provider unreachable and unloaded. After that, remaining work is producer implementation/state, not RT-CDM packet structure discovery.

Native rear Linux processed ISP remains **DENIED**.

## Result — OFFLINE FULLY SYMBOLIC STARTUP COMPOSE PASS

The existing E006k reduction/composer artifacts were independently audited before checkpointing.

All four startup MAIN packets compose deterministically from symbolic structure only:

- startup1: 3868 bytes, 118 commands, 714 register writes, 17 DMI slots
- startup2: 3772 bytes, 111 commands, 705 register writes, 16 DMI slots
- startup3: 2560 bytes, 63 commands, 504 register writes, 10 DMI slots
- startup4: 1624 bytes, 29 commands, 345 register writes, 3 DMI slots

For every startup packet:

- all register value fields are synthetic/symbolic at compose time;
- all DMI addresses are synthetic/symbolic at compose time;
- the command count, register-write count and DMI shape match E006a;
- after zeroing every register-value field and DMI-address field, the independently composed packet SHA-256 matches the equivalently normalized private Windows representative exactly;
- no captured register value is embedded in the safe recipe;
- no unresolved DMI producer remains.

Startup-only 0xB208 ownership is corroborated by the earlier pinned front static proof:
IFEBHistStats16Titan680 owns selector1 0x1000 bytes and selector2 0x50 bytes.

The temporary SP11 private selected-corpus copy is absent. Raw private evidence remains off-repo.

Status: **OFFLINE FULLY SYMBOLIC STARTUP COMPOSE PASS**.

This closes startup packet structure, not startup register producer implementation. Linux RT-CDM submission and native rear processed ISP remain **DENIED**.

### Next

Classify every unique startup register offset into a named producer/transport owner and separate true producer-generated state from fixed hardware configuration. Then compile a startup register binding contract, still unreachable, before any runtime integration.
