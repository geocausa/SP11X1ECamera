# E003i-GY — minimal changed post-G3 sentinel R27 live candidate

Status: **PREPARING / UNARMED / NO GY CAMERA RUNTIME YET.**

GY is a transport/lifecycle proof for exactly one changed control after G3. G1..G3 remain the proven native writes. At source G4 only, if native G4 is still bit-identical to the last applied G3 tuple, GY changes only `digital_gain_code` by +1 LSB (1471 -> 1472) and submits that atomic cluster after completed G5 for expected effect G7. If native G4 changed on its own, the sentinel is suppressed. G5..G26 are always shadow-only.

The sentinel is deliberately synthetic and tiny (+0.06798% digital gain) and changes no frame timing. A GY PASS proves one post-G3 changed sensor-transaction lifecycle; it does not claim that the synthetic value is a production AEC decision.

Safety contract: fresh identity, one candidate boot, one stream maximum, consumed guard before stream, no same-boot retry, archive immediately, return protected Golden, retire candidate.
