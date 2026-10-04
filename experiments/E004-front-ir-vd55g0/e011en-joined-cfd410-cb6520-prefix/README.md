# E011EN: joined CFD410 / CB6520 prefix

Status: **PASS_JOINED_CFD410_CB6520_PREFIX**.

E011EN extends the retained E011EM path through original `0xCFCC98 -> 0xCFD410` and the first dependency helper `0xCFD460 -> 0xCB6520`. Under the previously accepted owned cold-start authority from E011DY, `0x16A2A84` is zero and the file-initial pointer pair at `0x16072D8` is copied into the helper local state. `0xCB6520` returns with exact ABI state.

Across four selected-object placements, the new prefix qualifies 12 dependency reads, 36 exact local-store chunks and 428 altered-contract rejections. The selected stream object and retained 640-byte formatted output remain unchanged. The selected-object logical lock remains held and the index-8 global lock remains released.

Execution stops **before** `0xCFD46C` dereferences the selected pointer at `0x1607180 + 0x0C = 0x160718C`. Although the underlying file-initial bytes are known, no runtime/lifetime authority for that pointed field is claimed here. Native selection of the cold flag and pointer pair also remains unqualified.

NEXT **E011EO** establishes source-qualified authority/lifetime for that pointed-field dependency before allowing the branch to advance. IRQ/DMA/IOMMU and front hardware retirement remain parallel dynamic gates. Native rear runtime remains denied.

Zero camera Starts, reboots, kernel builds, production-C or PM changes were made. Golden payloads, EFI/GRUB and historical repositories remain untouched.
