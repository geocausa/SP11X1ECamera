# E011HB — CAD1F0 epilogue return to CAB62C frontier

Four exact placements integrate the accepted second `CAD1F0` path through its epilogue and return to `0xCAB590`. Receiver `+0x20` is `1`, so the sign branch at `0xCAB598` is not taken; receiver `+0x28 = 0`, so the bit-2-zero branch at `0xCAB5A4` is taken.

Execution stops at `0xCAB62C` before the `CAB178` helper writes its return value. E011HC reuses E011GL/E011FZ's opaque cookie frame contract to execute the return-value path, cookie check, helper epilogue, and return to `0xCA9840`, stopping before that caller instruction executes.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
