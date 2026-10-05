# E011HE — RVA 0x1370762 byte 0x25 to CA9590 loop frontier

The pinned image source separately qualifies RVA `0x1370762` as byte `0x25` / decimal `37`. Four exact placements execute the signed read at `0xCA984C`, advance receiver `+0x10` to RVA `0x1370763`, store byte `37` to receiver `+0x39`, and take the nonzero branch at `0xCA9858`.

Execution stops before target `0xCA9590`. E011HF reuses the accepted first parser-table byte at `0xF8B21B = 1`, executes the first lookup under parser state `7`, derives second lookup RVA `0xF8B230`, and stops before reading it.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
