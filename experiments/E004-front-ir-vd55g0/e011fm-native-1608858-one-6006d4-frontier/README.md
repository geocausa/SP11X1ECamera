# E011FM: native-qualified `0x1608858` one / nonzero branch

Status: **PASS_NATIVE_1608858_ONE_TO_6006D4_FRONTIER**.

Original `0x600410` establishes retained `x21` at image RVA `0x1608000`, making original `0x600474` an exact 4-byte read from RVA `0x1608858`. A bounded Windows front-camera reference read that field as `1` after front initialization but before reader Start, and again as `1` on the same boot after a successful NV12 1920x1080 front-reader Start. The file-static dword is also `1`, but live authority comes from the bounded native reads rather than from assuming the image value persists.

Four retained placements replay original `0x600474` (`ldr w8,[x21,#0x858]`) with the qualified value, execute original `0x600478` (`cbnz w8,...`), and take the nonzero branch to `0x6006D4`. They reject 1,816 altered current-path contracts plus the inherited 264 producer-API mutations. No behavior beyond the `0x6006D4` arrival is claimed.

The Windows reference used one front reader Start, zero rear Starts, and one controlled one-shot Windows round trip under the project reboot-count convention, and SP11 returned to verified Golden Linux with unchanged DTB/initrd/kernel hashes. No kernel build or production camera change was made.

NEXT **E011FN** qualifies the original loop-counter decrement at `0x6006D4` and the `0x6006D8` loop-back before entering the second iteration. Native rear runtime remains denied.
