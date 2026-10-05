# E011HK — F8B2A2 byte 7 through +20 dispatch to CA9838 frontier

The pinned image source separately qualifies second parser-table RVA `0xF8B2A2 = 7`. Four exact placements execute the second lookup, store parser state `7`, and reuse the accepted index-7 signed dispatch entry at `0xCA9908 = +20`. Original dispatch selects `0xCA9838`.

Execution stops before the helper case body. E011HL reuses the already-qualified helper/cookie/dispatch contracts to run only far enough to advance the argument cursor and stop before `0xCACE28` reads the next vararg qword at receiver-relative `+0x650`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
