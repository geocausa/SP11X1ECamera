# E011HZ — CAD868 epilogue return 26 to 0x6BD94 frontier

The source contains a unique direct call at `0x6BD90 -> 0xCAD868`, which fixes the architectural return target at `0x6BD94`. Four exact placements execute the `CAD868` epilogue from `0xCAD9B0`, restore its saved register frame and entry stack pointer, preserve `w0=26`, and return via `0xCAD9C4`.

Execution stops at `0x6BD94` before the caller instruction executes. E011IA advances the caller only to its first newly qualified source dependency/frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
