# E011GX — F5D480 one-byte copy to CAD260 stream-update frontier

Four exact placements execute `0xCAD25C -> 0xF5D480` with source RVA `0x1370780`, destination `receiver+0x6b0`, and length `1`. Reusing accepted E011GR source authority, the original helper reads byte `0x2e` and writes exactly that byte to the destination, then returns to `0xCAD260`.

Execution stops before the stream object is updated. E011GY advances the qualified object qword0 and count by one, reloads the object pointer at `0xCAD280`, and stops before the unqualified object `+0x18` flag read at `0xCAD284`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
