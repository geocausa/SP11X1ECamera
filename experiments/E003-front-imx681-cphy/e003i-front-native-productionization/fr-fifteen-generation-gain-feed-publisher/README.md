# E003i-FR — compiled gain publisher G1–G15

Status: **PASS OFFLINE G1–G15 C PUBLISHER.**

FR preserves FK's exact 24-byte gain-feed ABI and changes only the C validation upper bound from generation 12 to generation 15.

The verifier compiles and calls the actual C publisher for G1..G15, validates every emitted record and request = generation + 3 identity, rejects G16, and rejects malformed request identity.

No camera runtime is performed.
