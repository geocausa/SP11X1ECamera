# E011IB — 0x6BD48 epilogue return 26 to 0x6BE0C frontier

The unique direct callsite `0x6BE08 -> 0x6BD48` fixes return target `0x6BE0C`. Four exact placements execute the `0x6BDC0..0x6BDC8` epilogue, restore the 0x50-byte saved frame, preserve `w0=26`, and return to `0x6BE0C` without executing the caller instruction.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
