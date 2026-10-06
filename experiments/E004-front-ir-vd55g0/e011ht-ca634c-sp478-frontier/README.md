# E011HT — CA634C caller branch to SP+0x478 frontier

Using accepted E011FZ caller registers/frame and E011HS return `26`, four exact placements take the bit0-zero and x21-zero paths, qualify `[sp+0x10]=0` versus `x19=640`, take the mismatch branch, write one zero byte at caller output-buffer offset 0, and set `w21=26`. Execution stops before `0xCA63D8` reads `[sp+0x478]`. E011HU reuses E011FZ zero-frame authority for that slot.
