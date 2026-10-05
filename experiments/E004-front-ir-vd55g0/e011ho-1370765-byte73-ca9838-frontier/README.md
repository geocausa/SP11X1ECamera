# E011HO — RVA 0x1370765 byte 0x73 to CA9838 helper frontier

The pinned image source qualifies RVA `0x1370765 = 0x73`. Four exact placements execute the signed read, advance the retained pointer to `0x1370766`, and reuse the accepted byte-`0x73` parser chain: first table `0xF8B2B7 = 8`, second table `0xF8B2A2 = 7`, signed dispatch `+20`. Parser state becomes `7`.

Execution stops before target `0xCA9838` executes. E011HP source-qualifies the next formatter vararg at receiver `+0x658` and its 24-byte string, then carries the repeated helper through copy/return to the `0x1370766` read frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
