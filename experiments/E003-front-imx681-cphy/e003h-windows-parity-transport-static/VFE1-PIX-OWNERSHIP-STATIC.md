# E003h VFE1 PIX buffer/completion ownership — static and unreachable

Date: 2026-08-29

## Why this layer exists

The Windows-parity front path is not representable by CAMSS's generic single-WM completion model. One userspace QC10C VIDEO surface spans FULL WM0/WM1, while DS4/DS16 and five statistics outputs have independent backing storage. `0017` already makes the BUS address mechanics representable but deliberately unreachable; this layer defines who owns those buffers and when a frame slot may be reused, still without connecting any hardware path.

## Same-machine Windows completion model

Five bounded front-camera cycles produced the same observed event sequence:

`VIDEO(0x03) -> AEC_BE_BHIST(0x0d) -> TINTLESS_BG(0x0e) -> AWB_BG(0x10) -> RS(0x12)`

The raw 3,572-byte log is SHA-256 `1e3e810ae170dabb003491b6b8522c3b77dbd5964a14445ce7bbd3636e5b77ec`.

The important static result is stronger than the live ordering. Exact `qccamisp8380.sys` disassembly shows every event passes a group index to helper RVA `0x26460`. That helper selects one queue pointer from `object + (0x66b + group_index) * 8`, pops one record from that queue, decrements that queue's count and advances/wraps that queue's own read index. The active group indices are 0, 5, 6, 7 and 9.

Therefore Windows uses **independent per-group FIFOs**. The five-cycle order is an observation, not a cross-group dependency. Linux must not reject a valid reordered completion sequence.

The groups are:

- VIDEO: FULL Y/C + DS4 + DS16; one userspace QC10C completion;
- AEC_BE_BHIST: AEC_BE + BHIST;
- TINTLESS_BG: TL_BG;
- AWB_BG: AWB_BG;
- RS: RS.

## Linux `0018`

`0018-x1e-vfe1-pix-buffer-ownership-unreachable.patch` changes only `camss-vfe-680.c` and remains private/unreachable.

Each of the two existing CAMSS initial slots owns seven separate coherent Linux auxiliary allocations using the Windows-proven payload sizes (`FRAME_INCR`), not Windows ring spacing. The userspace QC10C allocation remains vb2/caller-owned. A slot begin operation enqueues that slot index into all five independent group FIFOs and produces the Linux DMA IOVA bundle expected by the private `0017` BUS recipe.

A completion maps event ID to one compact Linux group, peeks/pops only that group's FIFO and clears only that group's logical pending bit. VIDEO may return the userspace QC10C buffer immediately. The slot itself is reusable only after all five independent group bits have retired. Cross-group completion order is deliberately unconstrained; FIFO order is preserved within each group.

No captured Windows IOVA appears in the patch. The larger Windows AWB/BHIST slot spacing is not imported: separate Linux coherent allocations only need the exact per-output payload sizes.

## Fail-closed isolation

`0018` does not call `vfe680_x1e_bus_prepare`, `vfe680_x1e_bus_update` or `vfe680_x1e_bus_stop`. It does not modify the live ISR, `vfe_buf_done`, VFE ops, stream enable or sensor path. The ownership helpers are retained only by one private `__used` table; the compiled object has exactly four ABS64 relocations from that table to alloc/free/begin/complete and no relocation/reference to the table itself.

The existing X1E VFE1 PIX gate remains `-EOPNOTSUPP` before stream lock, IRQ or output programming.

## Mechanical proof

- completion extractor SHA-256: `461899f4b32e0208466db17ac23b366987caeb9d59210faba65023ce265c8162`;
- completion oracle SHA-256: `696f476a18bbfe4d6a30e06198c744d6495048b85399d22ff1bfe6c6176763f9`;
- `0018` patch SHA-256: `fb1d0acece63c9acde2f48bb51d1bac19fcdc17d3c7f1fd46de6f2bf0adc924f`;
- ownership inspector SHA-256: `1f91e87fce072a37d7c870b65fd186f3e56d18c271ec6149e465bbf668c27d2e`;
- inspection JSON SHA-256: `bc8bf64152882e8c312e0e1379b544e2ae733dc75b4e571784fac3b88b4b7dcf`;
- `qcom-camss.ko` SHA-256: `7d88c0d6c69d3690c4e83437b41e8afb05560d1390d0d819e8b8374db71e5010`;
- Golden vermagic exact;
- compiler diagnostics: none;
- patch forward/reverse reconstruction: PASS;
- checkpatch: zero code/style findings; only mail-patch metadata diagnostics.

No module was loaded. No BUS write, RT-CDM submission, VFE1 PIX enable, sensor transmission or frame attempt occurred.

## Next gate

Ownership is no longer the blocker. The next static layer is the **RT-CDM command-corpus materializer/orchestrator**: turn the already-captured four Windows IFE main-CDM streams (2,131 ordinary register writes, 46 DMI commands, 16 unique DMI payloads) into a Linux-owned command/data arena while preserving exact command bytes and replacing only fields already classified dynamic. It must remain unreachable and must not submit FIFO0 or enable VFE1 PIX yet.
