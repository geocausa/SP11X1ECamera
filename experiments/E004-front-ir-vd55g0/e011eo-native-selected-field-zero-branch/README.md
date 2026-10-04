# E011EO: native-qualified selected field zero branch

Status: **PASS_NATIVE_QUALIFIED_SELECTED_FIELD_ZERO_BRANCH**.

E011EO closes the pointed-field dependency left by E011EN without promoting the whole file image to runtime truth. A bounded native front-camera reference was taken after successful `InitializeAsync` and before `StartAsync`. In that state the runtime flag at `0x16A2A84` was zero, the first runtime pointer selected the source static object at RVA `0x1607180`, and the selected 32-bit field at `0x160718C` was zero. An independent KD memory read confirmed the selected field value.

The same native reference also showed why the authority is deliberately narrow: the second pointer was not its file-static `0x1607650` target, the global `0x16A2A88` pointer was not the file-static `0x1607180` target, and the second static object had changed. Therefore E011EO does **not** claim broad persistence of file-initial runtime state. The exact native instruction at `0xCFD46C` was not trapped and is not claimed as observed.

Using only the qualified first-pointer/field authority, the unchanged original source executes the `0xCFD46C` read as zero, compares it against `0xFDE9`, and takes the zero/non-match path to `0xCFD498`. Four retained placements remain byte-for-byte equal to their E011EN ancestors except for executed instruction/read accounting; each rejects 112 altered contract requests, 448 total. Selected object/output state is unchanged; the selected logical lock remains held and index-8 global lock remains released.

The next frontier is the original call `0xCFD498 -> 0xCB9F68`; that helper immediately depends on global `0x1B60000`, which is not qualified here. NEXT **E011EP** closes that callback/cache dependency before advancing further. IRQ/DMA/IOMMU and front hardware retirement remain open. Native rear runtime remains denied.

The native reference used four front-only Start/Stop runs (all successful) and one Windows round-trip (two reboots). SP11 returned to Golden Linux with the persistent boot order and Golden kernel/initrd/DTB hashes unchanged. No kernel build, production-C or PM change was made. Raw process addresses and debugger transport secrets remain private.
