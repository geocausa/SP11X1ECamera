# E011HA — receiver+0x20 zero-to-one to CAD1F0 epilogue frontier

Accepted E011FZ setup source-qualifies receiver `+0x20` as u32 zero via original `0xCA6318`. Four exact placements then execute `0xCAD294..0xCAD29C`: the value is read as `0`, incremented by the selected copy count `1`, and stored back as `1`.

Execution stops at `0xCAD2A0` before the `CAD1F0` epilogue. E011HB executes the epilogue and return to `0xCAB590`, qualifies receiver `+0x20 = 1` and `+0x28 = 0`, and stops at `0xCAB62C` before the helper return value is written.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
