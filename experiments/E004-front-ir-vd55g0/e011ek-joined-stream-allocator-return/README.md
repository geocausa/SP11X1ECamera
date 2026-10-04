# E011EK: joined original stream-allocator return

Status: PASS_JOINED_ORIGINAL_STREAM_ALLOCATOR_RETURN.

E011EK joins the E011EJ-qualified selected-stream state back into the retained E011EC 0xCC6078 frame and executes the original continuation from 0xCC60A0 through the real return at 0xCC60D8 -> 0xCED150.

Four placement cases pass. The original continuation reloads the inner result, publishes the selected stream to the outer result record, performs the exact normalization stores, invokes the source-pinned index-8 0xCB7398 leave wrapper, resolves the inherited LeaveCriticalSection binding and releases resource 0x16A3000. The selected object's own logical lock remains held; E011EK does not invent a release. 0xCC6078 returns with exact ABI state to 0xCED150, while parent frames 0xCED0D8 and 0xCED2F0 remain live.

Totals: 8 exact dependency reads, 24 exact source-store chunks and 220 altered-contract rejections. The selected 88-byte object bytes remain unchanged by normalization, redzones remain exact, image bytes remain unchanged and only the retained outer result record changes in the existing stack.

NEXT E011EL resumes at 0xCED150 on the qualified non-null selected-stream path and qualifies the exact setup/call at 0xCED174 -> 0xCFA968 without prematurely assigning semantics. IRQ/DMA/IOMMU and the distinct front hardware-retirement path remain parallel dynamic gates. Native rear runtime remains denied.
