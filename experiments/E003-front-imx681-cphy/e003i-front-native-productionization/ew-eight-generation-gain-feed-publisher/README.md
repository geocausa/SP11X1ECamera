# E003i-EW — eight-generation C gain-feed publisher

Status: **PASS OFFLINE / NO CAMERA RUNTIME.**

EW is the fresh bounded extension of EU required for an R10/R11 producer: publish CQ residual gain through G8 while preserving the exact 24-byte wire ABI and request = generation + 3 identity. The only source delta from EU is the accepted generation upper bound 6 -> 8. The compiled C proof accepts G1..G8, rejects G9, and rejects malformed request identity.
