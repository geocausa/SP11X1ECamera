# E011GS — length store and CACDF8 return to CAB288 local-write frontier

E011GS executes the accepted scan result store at `0xCACE94`, writing receiver `+0x48 = 1`, then completes the `0xCACDF8` epilogue and returns to `0xCAB1F8`. The common helper continuation sees truth value `1`, receiver `+0x38 = 0`, and receiver `+0x28` low word `0`. Execution stops at `0xCAB288` before the first write through `x22`.

`x22` itself is already source-owned: `0xCAB19C` assigns it to the helper's 16-byte local stack area, whose first qword is the signed sentinel `-2`. E011GT executes only the deterministic local-formatting path to the `0xCAB3EC -> 0xCAD1F0` call frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
