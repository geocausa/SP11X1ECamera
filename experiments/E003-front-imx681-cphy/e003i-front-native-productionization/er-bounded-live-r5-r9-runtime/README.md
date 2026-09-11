# E003i-ER — corrected bounded live R5–R9 one-shot

Status: **fresh unexecuted live successor; EP-gated and prearm-clean.**

ER is the fresh runtime identity after two consumed predecessors:

- **EO attempt1:** real camera run; R5–R8 submitted, then fail-closed at R9 because the first EL selector rejected a valid multi-side traversal. EP closes that bug and proves corrected `10 -> 8 -> 16` plus R9 capsule SHA256 `209961646647ec9a2747a553c10139f1cd303dc3a5b6cf302deca6636f173191`.
- **EQ boot1:** consumed at runtime preflight only because EN's verifier wrote nondeterministic timing observations into tracked JSON. No camera module loaded, helper did not run, and no stream started. The verifier now measures/enforces timing every run but writes deterministic budgets/pass state.

ER does not reuse EO or EQ boot entries, helper filenames, markers, output directories, or one-shot identities. Its bounded ownership remains `R5<-G2, R6<-G3, R7<-G4, R8<-G5, R9<-G6` with six completed generations, exactly three possible sensor writes, current-first CQ publication, one helper invocation, no same-boot retry, fail-closed producer/parent behavior, and persistent Golden `sp11-audio-fullio-v19c` fallback.

Prearm requires CW exact module authority, deterministic EN R5–R9 verification, EP's full archived EO replay, helper/bootstrap `-Werror` builds, Golden saved-entry integrity and no loaded camera stack.

A live PASS proves this bounded five-IQ-request path only. It does not claim unrestricted continuous AEC or the true GainAdj two-vertex out-of-mesh fallback.
