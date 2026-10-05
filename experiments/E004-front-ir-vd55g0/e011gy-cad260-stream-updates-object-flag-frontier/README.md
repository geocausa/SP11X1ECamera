# E011GY — CAD260 stream updates to object-flag frontier

Four exact placements resume at `0xCAD260` after the accepted one-byte copy. The receiver-owned stream object qword0 advances from `receiver+0x6b0` to `receiver+0x6b1`, its count at object `+0x10` advances from `0` to `1`, and the stream-object slot is reloaded at `0xCAD280`.

Execution stops at `0xCAD284` before reading object `+0x18` (receiver-relative `-0x8`). E011GZ source-qualifies that byte from the accepted E011FZ CA6280 setup and executes only the immediate branches, stopping before the receiver `+0x20` read at `0xCAD294`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
