# E011FY — `CA6280` entry to cookie-producer frontier

Four source-exact placements execute the current `0xCAD93C -> 0xCA6280` call and the five original `CA6280` prologue instructions. The helper creates an exact 48-byte frame, saves the current nonvolatile tuple, sets `x29` to the new SP, and preserves the FX call arguments. Execution stops before `0xCA6294 -> 0x11D0`.

`0x11D0` is the image security-cookie producer. This checkpoint does not substitute a file-image cookie for live process authority and does not execute that dependency. No camera Start, reboot, rear runtime, or kernel build is used. NEXT is E011FZ.
