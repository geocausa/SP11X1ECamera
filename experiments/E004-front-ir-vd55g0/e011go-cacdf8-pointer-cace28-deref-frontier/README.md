# E011GO — CACDF8 receiver pointer update to CACE28 dereference frontier

E011GO derives the retained receiver `+0x18` pointer from already accepted E011FX/E011FZ placement authority: the pointer is receiver-relative `+0x648`. Four source-exact placements execute helper `0xCACDF8` through its frame setup, pointer alignment, and owned update. The pointer is already 8-byte aligned, so the alignment delta is zero and receiver `+0x18` advances to receiver-relative `+0x650`.

Execution stops at `0xCACE28` before the 8-byte dereference from the original receiver-relative `+0x648` location. That qword is not yet claimed. Source inspection shows the next bounded call frontier is `0xCACE48 -> 0xCA65A8`; E011GP first qualifies the qword, then may execute only to that call frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
