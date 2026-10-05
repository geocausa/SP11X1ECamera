# E011GG — source byte 0x73 to F8B2B7 lookup frontier

The exact pinned source byte at image RVA `0x1370761` is `0x73` / decimal 115. Four source-exact placements execute the original signed read at `0xCA984C`, advance the retained source pointer to `0x1370762`, retain the byte at receiver `+0x39`, and take the original nonzero branch at `0xCA9858`.

Original parser arithmetic derives lookup offset `166` from that byte with lookup base RVA `0xF8B211`, selecting table-byte RVA `0xF8B2B7`. Execution stops at `0xCA95B8` before reading that table byte. E011GH must source-qualify the exact byte at `0xF8B2B7` before the table read executes.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
