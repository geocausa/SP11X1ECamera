# E011FL: native-qualified `0x160A218` zero / bit-16 fallthrough

Status: **PASS_NATIVE_160A218_ZERO_TO_600474_FRONTIER**.

E011FL closes the 8-byte dependency first exposed by E011FK without inferring live state from the file image. Under a bounded Windows front-camera reference, an independent KD process-context read of RVA `0x160A218` returned zero before a reader Start. A single front-only reader Start then succeeded at NV12 1920x1080, and the same-boot field read remained zero afterward. The exact `0x60046C` instruction breakpoint was armed at the stable live module address but was **not** observed; that limitation is retained explicitly rather than converted into a false hit.

Four retained placements replay original `0x60046C` (`ldr x8,[x24,#0x28]`) using the native-qualified zero, execute original `0x600470` (`tbnz x8,#16,...`), prove bit 16 clear, and take the fallthrough to `0x600474`. They reject 1,768 altered current-path contracts plus the inherited 264 producer-API mutations. The file-static qword is also zero, but file state is not used as native authority.

The bounded Windows reference used one front reader Start, zero rear Starts, and one controlled reboot back to the verified Golden Linux state. No kernel build or production camera change was made.

NEXT **E011FM** qualifies the retained `x21` owner at `0x600474` and the exact 4-byte `[x21+0x858]` dependency before taking its following branch. Native rear runtime remains denied.
