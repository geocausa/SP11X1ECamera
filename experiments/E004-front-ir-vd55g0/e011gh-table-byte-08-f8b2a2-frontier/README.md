# E011GH — table byte 0x08 to F8B2A2 second-lookup frontier

The exact pinned table byte at image RVA `0xF8B2B7` is `0x08`. Four source-exact placements execute the original read at `0xCA95B8`, scale the table value to `72`, combine it with retained parser-state byte `1`, and derive second lookup offset `146` from table base RVA `0xF8B210`.

Execution stops at `0xCA95D8` before the newly selected one-byte table read at RVA `0xF8B2A2`. E011GI must source-qualify that exact byte before the second table read executes.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
