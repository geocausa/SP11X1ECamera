# E003h replay / Epoch0 pacing oracle

Focused same-machine Windows trace of the first two post-sensor selector-2 priming consumes. This closes a pacing ambiguity exposed while composing the first callable Linux PIX runner.

The first raw Epoch0 after IMX681 stream-on performs one complete nine-client BUS address retarget, then consumes replay2 (`0x904` bytes, requestId 2), and the first VIDEO completion follows. The next Epoch0 performs another complete nine-client BUS address retarget before replay3 (`0x4e8`, requestId 3). Therefore replay2/replay3 are **not** immediate sequential submissions after sensor-on.

Linux consequence: a bounded one-QC10C-frame diagnostic needs only the first Epoch0 -> BUS update -> replay2 -> VIDEO prefix, then may enter the already-proven bounded stop/rollback path. It must not pre-submit replay3 before the first VIDEO. The later Epoch0-without-consume observations are not interpreted because debugger breakpoint overhead plus the three-second holder makes that tail intrusive.
