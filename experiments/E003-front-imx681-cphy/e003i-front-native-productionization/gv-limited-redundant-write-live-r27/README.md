# E003i-GV — limited redundant-write R27 live candidate

Status: **PREPARING / UNARMED / NO GV CAMERA RUNTIME YET.**

GV is the first post-GS physical-write expansion. It preserves the continuous scheduler and exact DQBUF gate but allows at most three additional physical writes: sources G4/G5/G6 may use the real sensor ioctl only when each complete control tuple is bit-identical to the last successfully applied tuple. Any changed G4..G6 control remains shadow-only. G7..G26 are always shadow-only.

Thus GV can perform between three and six physical writes total, never a changed post-G3 write. It is a repeated-ioctl/lifecycle proof, not changed-light feedback authority.

Safety contract: fresh identity, one candidate boot, one stream maximum, consumed guard before stream, no same-boot retry, archive immediately, return protected Golden, retire candidate.
