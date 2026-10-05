# E011FT: `0x6BD70` reload prefix to `0x17A1150` read frontier

Status: **PASS_6BD70_RELOAD_PREFIX_TO_17A1150_READ_FRONTIER**.

E011FT continues from the accepted E011FS return and executes the exact 28-byte original prefix at `0x6BD70..0x6BD88`. `x8` retains `base+0x17A1150` while six exact stack reads restore the current formatter tuple into `x1..x6`.

Across four retained placements, all 24 stack reads are checked at their exact source/address/width/value contracts and the restored tuple is exact. Execution stops at untouched `0x6BD8C` before its 8-byte read through `base+0x17A1150`; 2,320 altered current-path contracts plus the inherited 264 producer-API mutations are rejected.

The older E011DY zero for this writable zero-fill cell is only a loader/model assumption, not native runtime authority. No new camera Start, reboot, kernel build, or rear runtime was needed here. NEXT **E011FU** resolves the native/current value before executing the read. Native rear runtime remains denied.
