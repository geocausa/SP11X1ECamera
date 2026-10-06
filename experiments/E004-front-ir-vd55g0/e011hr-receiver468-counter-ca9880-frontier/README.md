# E011HR — termination counter 1→2 to CA9880 return-load frontier

Accepted E011GA authority supplies receiver `+0x468 = 1`. Four exact placements execute `0xCA986C..0xCA987C`, increment/store the counter to `2`, and take the equality branch to `0xCA9880`.

Execution stops before `0xCA9880` reads receiver `+0x20 = 26`. E011HS executes that return load and the original `CA94E8` epilogue, stopping at caller RVA `0xCA634C`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
