# E003i-EQ — corrected bounded live R5–R9 one-shot

Status: **fresh unexecuted successor; offline/prearm verification required before any arm.**

EQ is the fresh successor to **consumed EO attempt1**. It does not reuse EO's boot entry, helper filename, marker, output directory, or one-shot identity. The bounded schedule is otherwise intentionally unchanged so the single corrected variable is the GainAdj selector/publication logic closed by EP.

Bounded ownership remains:

`R5<-G2, R6<-G3, R7<-G4, R8<-G5, R9<-G6`.

Safety remains six completed video/statistics generations, exactly three possible sensor writes (G1@G2, G2@G3, G3@G4), current-first CQ publication, one helper invocation, fail-closed producer/parent behavior, no same-boot retry, STREAMOFF/health checks, persistent Golden `sp11-audio-fullio-v19c`, and whole-machine reboot after the attempt.

The mandatory new authority is **EP**. EP reruns the real EN producer over EO's archived live snapshots, proves R5–R8 remain byte-identical to the capsules EO actually submitted, and proves corrected G6/R9 follows GainAdj triangle `10 -> 8 -> 16` with capsule SHA256 `209961646647ec9a2747a553c10139f1cd303dc3a5b6cf302deca6636f173191`. EQ prearm refuses to proceed unless EP passes.

A live PASS would prove this bounded five-IQ-request integration only. It would **not** prove unrestricted continuous AEC or the still-unproven true GainAdj two-vertex out-of-mesh fallback.
