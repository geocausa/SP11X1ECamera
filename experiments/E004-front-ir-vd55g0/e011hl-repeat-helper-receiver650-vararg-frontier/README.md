# E011HL — repeat helper to receiver+0x650 vararg frontier

Four opaque-cookie placements execute the repeated `0xCA9838 -> CAB178` helper path using the already-qualified range/dispatch/CACDF8 contracts. The current argument cursor at receiver `+0x18` advances from receiver-relative `+0x650` to `+0x658`.

Execution stops at `0xCACE28` before dereferencing the qword at receiver `+0x650`. E011HM joins the accepted formatter vararg layout to qualify that qword as RVA `0x10F03B0`, qualifies its one-byte string, and executes the repeated helper through its complete copy/return path to the next parser byte frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
