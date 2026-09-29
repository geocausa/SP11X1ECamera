# E011O — rear AWB_BG request-1 cold-to-normal bulk transition

Parent Git: `5a51caae9b749821adcd30b63333ee6746de6ab0` (E011N).

Status: **SOURCE + LIVE SAME-SLOT BULK REPLACEMENT CLOSED; UPSTREAM NORMAL-SOURCE POLICY OPEN.** Native rear ISP runtime remains denied.

Pinned source identifies the AWB statistics consumer as `CamX::AWBBGStats17::Execute` at RVA `0x9FE780`; its request-side dependence copy helper is at RVA `0x9FDF60`. The AWB_BG request record begins at request `+0xCF8`.

Fresh original-Windows rear4K tracing caught the first AWB_BG Execute carrying request ID 1. At that entry the request-owned AWB_BG record was still the cold bootstrap: `64x48` regions, ROI `0,0,3658x2058`, four `0x3ffff` threshold words, and the adjacent scalar `0x12`.

A process-scoped data watch on the same request-owned AWB_BG slot then caught the first semantic-changing replacement. It was not a field-by-field AWB writer: the active IFE request path was bulk-copying a complete ISP/request data structure. Static reduction identifies the copy helper at RVA `0x740D88`, called from `CamX::IFENode::ExecuteProcessRequest`; the full-copy call returns at RVA `0x740E5C` and copies `0xF508` bytes into the IFENode request-data clone at `IFENode + 0x145B0`.

Immediately before the watched store, the upstream source carried AWB_BG `64x48`, ROI `0,0,4064x2286`, four `0x3c3fe` threshold words and the same adjacent `0x12`. Single-stepping the watched store verified the destination changed in place from the cold `3658x2058 / 0x3ffff` payload to `4064x2286 / 0x3c3fe`, while the `64x48` region counts stayed unchanged.

Therefore the request-1 AWB_BG cold-to-normal **same-slot replacement mechanism and immediate source payload are closed**: an upstream normal ISP/request structure is cloned into the IFENode request data during the active request path. What remains open is the earlier policy/producer that populated that upstream normal AWB_BG payload before the bulk copy. This run also did not independently trap a second AWBBGStats17 Execute after the replacement.

The E011O-0110A rear4K holder completed StartAsync and StopAsync with 789 valid 4K handles, and all debugger breakpoints were cleared. No native rear ISP module was installed or loaded and no RT-CDM submit occurred.

Only source-safe scalar relationships and stable RVAs are committed. OEM bytes, raw debugger logs, process addresses and optical payloads remain private on SP11.
