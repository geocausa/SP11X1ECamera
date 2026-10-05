# E011FS: current `0xEDD0` leaf return to `0x6BD70`

Status: **PASS_EDD0_CURRENT_LEAF_RETURN_6BD70_FRONTIER**.

E011FS executes the accepted current `0x6BD6C -> 0xEDD0` call. The exact 12-byte original leaf (`ADRP`, `ADD`, `RET`) executes under the E011FR frame, visits three instructions per retained placement, returns `base+0x17A1150` in `x0`, and preserves the current stack/nonvolatile ABI at `0x6BD70`.

Four retained placements reject 2,212 altered current-path contracts plus the inherited 264 producer-API mutations. Execution stops at `0x6BD70` before the consumer begins; the next unqualified dependency is the 8-byte read at `0x6BD8C` through `base+0x17A1150`. `0xCAD868` remains later and unexecuted.

No new camera Start, reboot, kernel build, or rear runtime was needed. NEXT **E011FT** qualifies the `0x6BD70` reload prefix and stops before that 8-byte dependency read. Native rear runtime remains denied.
