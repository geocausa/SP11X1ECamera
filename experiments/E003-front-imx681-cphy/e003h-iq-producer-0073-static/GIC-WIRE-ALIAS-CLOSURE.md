# E003h 0073 — Surface GIC311 wire-alias closure

Status: **accepted exact-binary/offline closure**. Same-machine Windows wire behavior remains the parity authority. No Linux camera runtime was performed or authorized.

## Result

The changing Windows `0x4708 / selector 1 / 0x200-byte` DMI payload previously labelled `GIC0` is **not an independent GIC311-calculated LUT** on this exact Surface Camera 10.9 path. It is a deterministic wire alias caused by the exact Surface `IFEGIC311Titan680::CreateCmdList` passing its DMI offset in dwords to `PacketBuilder::WriteDMI` without converting it to bytes.

The GIC module's node-assigned offset is `0x62e` dwords. `IFEGIC311::RunCalculation` correctly treats that as a dword index, so the logical calculated GIC table is written at byte offset:

`0x62e * 4 = 0x18b8`

That logical 512-byte table occupies `0x18b8..0x1ab8`, immediately before the BPC/ABF DMI region. It is byte-identical between exact request5 and matched request6.

But exact `IFEGIC311Titan680::CreateCmdList` loads that same `0x62e` member and passes it raw as `WriteDMI(..., offset=0x62e, length=0x200)`. Exact `Packet::AddCmdBufferReference` later adds the child CmdBuffer base offset and serializes the nested offset **without any x4 conversion**. Consequently the Windows VFE GIC DMI address uses source byte offset `0x62e`.

## Cross-module proof

This is GIC-specific on the exact Surface binary, not a new global `WriteDMI` unit:

- `IFELSC411Titan680::CreateCmdList` explicitly converts its dword offset with `lsl ..., #2` before its three `0x4308` DMI writes.
- `IFEGTM131Titan680::CreateCmdList` explicitly converts its dword offset with `lsl w4, ..., #2` before its `0x5a08` DMI write.
- `IFEGIC311Titan680::CreateCmdList` does **not** perform that conversion before `0x4708`.
- `PacketBuilder::WriteDMI` and `CmdBuffer::AddNestedCmdBufferInfo` preserve the supplied nested source offset.
- `Packet::AddCmdBufferReference` serializes `child CmdBuffer +0x60 + raw nested offset`; there is no hidden scaling stage.

Pinned exact Surface DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Exact alias geometry

The Windows wire GIC range is `0x62e..0x82e` (512 bytes). It consists entirely of existing LSC bytes:

- `0x62e..0x774`: 326 bytes from the tail of LSC0.
- `0x774..0x82e`: 186 bytes from the head of LSC1.

That explains why the captured wire `GIC0` payload changes request5→request6 whenever LSC0/LSC1 change, even though the separately calculated GIC table at `0x18b8` does not change.

`prove-gic-wire-alias.py` fail-closes the exact DeviceMFT code bytes, request5/request6 DMI-source hashes, dword→byte relation, overlap geometry and both logical/wire payload comparisons. Its machine-readable result is `gic-wire-alias-oracle.json`.

## Parity consequence

For **Windows 1:1 Linux parity**, GIC is no longer an independent dynamic LUT producer to solve. Linux must reproduce the Windows **wire** behavior: the `0x4708` payload is the 512-byte alias of the current LSC source at `0x62e`, including this Surface-specific anomaly.

The independent changing wire-LUT producer problem is therefore reduced from **LSC + GIC + GTM** to **LSC + GTM**. Reconstructing the unused logical GIC311 table can remain a secondary internal-producer parity task, but it is not a gate for matching the actual Windows VFE request bytes.
