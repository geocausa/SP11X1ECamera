# E005l — GROUP3 STAT metadata exports aggregate queue key/tag, not BF queue8 requestId proof

Parent Git `29187cbea2f0e749d4773d97565e947a3e4c34fe`. SP11 Golden Linux, read-only static analysis of SHA-pinned original Windows camera binaries. No camera stream, reboot, module, MMIO, KD, kernel debugger or BCD change in this stage.

## Result

This stage closes an important ambiguity in the non-halting STAT-metadata route.

The original qccamisp group-ring producer RVA `0x26838` builds one **local packed descriptor** on its own stack, then iterates 13 software groups and offers that same descriptor to every selected/non-full group ring. Group 4 is COMBO_STATS; group 8 is BF. These are separate ring pointers:

- group4 COMBO_STATS: device + `(0x66b+4)*8 = 0x3378`;
- group8 BF: device + `(0x66b+8)*8 = 0x3398`.

The producer's input request object does contain a field at input+`0x08` that its own diagnostic names `requestId`, but the ring descriptor is **not a direct copy of that object**. The local ring record's +`0x08` lane is explicitly assembled separately (including a byte store at stack+`0x08` and a separate status dword at stack+`0x0c`) before the common copy helper copies from `sp` into each selected ring. Therefore the group-ring +`0x08` value must remain an **opaque queue key** unless a later source/dynamic proof establishes stronger semantics.

The BF dispatcher independently pops **group8** and, when its WM16 CFG gate is set, passes:

- FIFO8 entry+`0x08` 64-bit key;
- FIFO8 entry+`0x16` 16-bit tag

to matcher RVA `0x25078`, which compares those fields against the six outstanding-slot key/tag domains.

The GROUP3 sender RVA `0x26170` does **not** pop group8. It pops **aggregate queue index4**. Its source record uses the same offsets:

- aggregate entry+`0x08` -> GROUP3 packet active-entry+`0x28`;
- aggregate entry+`0x16` -> GROUP3 packet active-entry+`0x38`.

GROUP3 raw ID `0x19` is normalized by the original AVStream parser. For the **first active** one of the six GROUP3 entries, the parser copies:

- packet entry+`0x28` -> normalized notification+`0x08`;
- packet entry+`0x38` -> normalized notification+`0x10`.

The custom stats metadata writer RVA `0x91990`, called directly by `CPin::CompleteFrame`, constructs metadata item `0x8000000f` of size `0x8a0`. It then copies:

- normalized notification+`0x08` **low 32 bits** -> metadata item+`0x10`;
- normalized notification+`0x10` -> metadata item+`0x18`.

Thus a user-mode STAT completion can expose the **aggregate GROUP3 queue key (low32) and tag** without kernel debugging.

## Critical boundary

That is useful, but it is **not** the missing BF proof.

The common producer uses the same packed local source record for group4 and group8 only when each ring is independently selected, exists, has capacity and reaches its copy branch. The rings have independent counters/cursors, and the existing producer increments its pending count after the copy-helper call without checking that helper's return value. Therefore:

- a group4 COMBO_STATS metadata key/tag is not automatically a physically observed group8 BF dequeue;
- the metadata key is not source-proven to be the camera/IFE `requestId`;
- the GROUP3 parser picks the first active stats entry and does not source-bind that selected entry specifically to BF resource `0x300d`;
- neither STAT delivery nor its key/tag proves the BF outstanding matcher returned non-NULL;
- none of this proves exact WM16 IRQ/ACK, DMA/IOMMU quiescence, safe buffer reuse or owner-safe stop.

This corrects the tempting but unsupported shortcut “STAT metadata key == BF requestId”.

## Consequence

A future non-halting Windows trace may safely sample item `0x8000000f` offsets `+0x10/+0x18` as **aggregate stats key/tag scalars**. It becomes a BF queue8 identity only if a separate source or dynamic observation proves the same producer transaction successfully populated both group4 and group8 and the group8 consumer/matcher reached the expected exact key/tag.

Otherwise the decisive gate remains the same: same owner/frame, nonempty BF FIFO8, non-NULL matched WM16 object, and independently trusted exact-buffer hardware completion/ACK plus DMA/IOMMU-safe lifetime. External KD may be used only when SP7 is restored as the debugger host.

Native rear processed ISP runtime remains **DENIED**.

Run:

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py`
