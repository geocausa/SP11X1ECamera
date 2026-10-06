# E011IC — 0x6BDD0 tail return 26 to 0x7ACDC frontier

The original `0x7ACD8 -> 0x6BDD0` callsite fixes return target `0x7ACDC`. Four exact placements execute the 0x6BDD0 tail/epilogue, restore its 0x40-byte frame, preserve `w0=26`, and stop at `0x7ACDC`. NEXT E011ID returns the outer 0x7AC38 wrapper to accepted caller `0x600440`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
