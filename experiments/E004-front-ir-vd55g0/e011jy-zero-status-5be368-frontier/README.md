# E011JY — zero status branch to 0x5BE368 frontier

PASS. E011JY executes the caller branch from `0x5BE674` to `0x5BDEB8`, preserves the accepted E011JP `x25=RVA 0x18A2968` authority, reads the accepted zero at `x25+4`, and proves the `cmp #1` / `b.ne` sequence selects `0x5BE368`. Execution stops before that continuation.

NEXT E011JZ executes the paired stack-cookie restore/check path at `0x5BE368 -> 0x11F0` under the accepted cookie contract and stops at `0x5BE374` before nonvolatile restoration. No new camera Start, reboot, rear runtime, or kernel build is used.
