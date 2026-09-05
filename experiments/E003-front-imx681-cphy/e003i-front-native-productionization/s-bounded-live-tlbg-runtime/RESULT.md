# E003i-S bounded live TL_BG runtime result — 2026-09-05

Status: **PASS transport / ABI size correction required**.

The single authorized one-shot completed with helper RC 0 and no same-boot retry. Six QC10C frames arrived as indices `[0, 1, 2, 3, 0, 1]` and sequences `[0, 1, 2, 3, 4, 5]`, each 7,778,304 bytes. R4 was submitted before STREAMON; R5 was submitted on the same fd after DQBUF0 and R6 after DQBUF1. STREAMOFF completed normally, and SP11 returned to protected Golden Linux afterward.

Generation-tagged TL_BG delivery worked across the bounded run: generations/source sequences `[1, 2, 3, 4, 5, 6]` on slots `[0, 1, 0, 1, 0, 1]`. All six authority payloads are unique and every one of the 768 raw records contains data. Offline Titan680 parsing produces flags=3, 768 regions, 18-bit statistics, four `0x3ffff` thresholds and stretch=1.0 for every generation.

A pre-existing arithmetic error was discovered during offline validation. Stage-N's durable parser proof correctly says the raw hardware/parser authority is **768 × 0x50 = 61,440 bytes (`0xF000`)**. Later handoff/Q text incorrectly stated that product was `0x25800` (153,600). S therefore exposed 153,600 raw bytes, but bytes `0xF000..0x25800` are all zero in all six Linux generations and in both preserved Windows live dumps. The real first `0xF000` is valid, nonzero and parser-clean. Production must shrink the control to `0xF000` raw bytes / `0xF020` total snapshot; no hardware programming change is indicated.

`source_seq` remains a completion generation, **not** a request ID. This run does not prove a numerical request-delay mapping.
