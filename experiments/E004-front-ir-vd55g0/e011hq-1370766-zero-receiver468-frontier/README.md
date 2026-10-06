# E011HQ — zero source byte to receiver+0x468 termination-counter frontier

The pinned image source qualifies RVA `0x1370766 = 0`. Four exact placements execute the signed zero-byte read, advance the retained pointer to `0x1370767`, store receiver `+0x39 = 0`, fall through the nonzero branch, and qualify parser state `7` through the state checks.

Execution stops before `0xCA986C` reads receiver `+0x468`. E011HR reuses accepted E011GA authority that this counter is `1`, executes the termination increment to `2`, and stops at `0xCA9880` before the parser return value is loaded.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
