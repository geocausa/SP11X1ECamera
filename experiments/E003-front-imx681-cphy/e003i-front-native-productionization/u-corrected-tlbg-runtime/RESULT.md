# E003i-U corrected TL_BG runtime result

**PASS.** One bounded U boot and one helper invocation completed six QC10C frames in indices `[0,1,2,3,0,1]` / sequences `[0..5]`, with R4 before STREAMON and R5/R6 submitted live on the same fd after DQBUF0/DQBUF1.

The corrected TL_BG V4L2 ABI returned exactly six **61,472-byte (`0xF020`)** snapshots: 32-byte header + **61,440-byte (`0xF000`)** Titan680 raw payload. Generations/source sequences were `[1..6]`, slots `[0,1,0,1,0,1]`. Offline stage-N parsing consumed each complete payload; every generation had all 768 records populated, all six raw payloads were unique, and no legacy zero tail remained.

STREAMOFF completed, the candidate critical-fault scan was empty, and SP11 returned to protected Golden with empty `next_entry` and camera modules absent. Source generation remains explicitly **not** a request ID.
