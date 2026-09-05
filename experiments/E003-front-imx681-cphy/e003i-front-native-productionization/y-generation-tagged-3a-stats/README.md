# E003i-Y — generation-tagged front 3A raw-stat snapshot

Status: **PASS (static source/build/ABI proof; no camera runtime).**

Stage X closed clean live-LSC compute latency. Stage Y closes the next Linux transport prerequisite: expose the already-programmed AEC_BE, BHist and AWB_BG hardware-statistics outputs to userspace with the same explicit source-generation identity used by the proven TL_BG path.

## Raw authority

No new Windows boot was required. The accepted startup CDM capture and SHA-pinned Surface `QcDeviceMFT8380.dll` (`c241b7fb...41c35`) are sufficient.

The Titan680 AEC and AWB packers encode `(region_count - 1)` in the captured H/V fields. Startup packet1 is the last AEC/AWB programming before CSID start; priming replay1 is byte-identical to startup packet1 except `period_cfg`, and startup packets2/3 do not overwrite these blocks.

Active single-IFE1 geometry is therefore:

- AEC_BE: 32 × 32 = 1,024 regions; Titan680 raw stride `0x50` bytes/region; exact raw prefix **`0x14000`**.
- BHist: 1,024 bins; one 32-bit raw word/bin; exact raw prefix **`0x1000`**.
- AWB_BG: 64 × 48 = 3,072 regions; Titan680 raw stride `0x50` bytes/region; exact raw prefix **`0x3c000`**.

The concatenated 3A raw authority is **`0x51000` (331,776 bytes)**. Existing BUS allocations (`0xa0000`, `0x1800`, `0x151800`) remain untouched ceilings; their unused/padded space is not exported as authority.

`prove-3a-raw-authority.py` rechecks the DeviceMFT identity/function slices, startup register values, startup/priming order and size arithmetic and emits `RAW-AUTHORITY.json`.

## Linux ABI

A new read-only volatile compound V4L2 control, `V4L2_CID_USER_BASE + 0x1242`, exposes one latest-generation 3A bundle on the existing front PIX video fd.

Snapshot size is **`0x51040` (331,840 bytes)**:

- 64-byte little-endian header;
- AEC_BE at payload offset `0x00000`, length `0x14000`;
- BHist at payload offset `0x14000`, length `0x1000`;
- AWB_BG at payload offset `0x15000`, length `0x3c000`.

Header identity fields include independent monotonic snapshot generation, exact CAMSS `source_seq`, and slot. `source_seq` is the authoritative cross-control identity with TL_BG; it is **not** called a request ID.

## Ownership boundary

The existing runner already executes `poll_all_done()` before TL_BG publication and only then retires the four auxiliary completion groups. Stage Y publishes 3A in that same window:

`poll_all_done -> TL_BG copy -> 3A copy -> retire_aux`

The new VFE accessor additionally refuses access unless both AEC_BE/BHist and AWB_BG completion bits are still pending for the expected slot. Thus all three source DMA buffers remain ownership-pinned while their exact prefixes are copied.

This ordering is present for all six bounded source generations, with slots `0,1,0,1,0,1` and the same `source_seq` passed to TL_BG and 3A.

## Static acceptance

- Golden-ABI module builds successfully.
- module SHA256: `42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b`.
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`.
- kernel checkpatch: 0 errors / 0 warnings.
- five-file source patch reverses to the exact preimage and reapplies to the exact postimage.
- six 3A publication windows are mechanically checked.
- no new `readl/writel`/direct MMIO accesses.
- no BUS allocation-size, address-programming or completion-order change.
- no Linux camera runtime was performed by this checkpoint.

`inspect-generation-tagged-3a.py` is the fail-closed static acceptance test and emits `INSPECTION.json`.

## Next gate

Build a distinct Golden-safe one-shot runtime using this exact module and the already-proven U six-frame helper semantics. Read both TL_BG (`0xF020`) and 3A (`0x51040`) after each DQBUF and require source sequences/generations `1..6`, paired identity, correct payload sizes and real nonzero/dynamic AEC/BHist/AWB data. Return to Golden before offline parsing.

Only after that live transport proof should Stage Y/Z proceed to reconstruct the upstream AEC lux-index and AWB CCT algorithms from the captured generation-tagged inputs. No Lux/CCT value is synthesized or guessed by this checkpoint.
