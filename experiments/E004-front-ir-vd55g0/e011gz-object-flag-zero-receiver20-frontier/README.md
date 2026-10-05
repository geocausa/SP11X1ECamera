# E011GZ — object flag zero to receiver+0x20 read frontier

The accepted E011FZ CA6280 setup is replayed at the original flag producer and qualifies object `+0x18` (receiver-relative `-0x8`) as byte `0`. Four exact consumer placements execute `0xCAD284`; the nonzero flag branch is not taken, `x22=x23=1`, and the inequality branch at `0xCAD290` is also not taken.

Execution stops at `0xCAD294` before receiver `+0x20` is read. E011HA source-qualifies that u32 as zero from original `0xCA6318`, performs the resulting increment/store to `1`, and stops before the `0xCAD2A0` epilogue.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
