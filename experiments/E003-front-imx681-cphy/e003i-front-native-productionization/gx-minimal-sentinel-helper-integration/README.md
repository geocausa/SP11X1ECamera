# E003i-GX — minimal changed-sentinel helper integration

Status: **PASS OFFLINE compile/integration / no camera runtime / exactly one changed post-G3 opportunity.**

GX integrates GW's +1 digital-gain sentinel into the consumed GS continuous scheduler helper.

Runtime contract:

- G1..G3 remain the already-proven native physical control path;
- only source G4 can request the sentinel;
- G4 can write only if native G4 is still bit-identical to the last successfully applied G3 tuple;
- when allowed, the physical tuple changes only digital gain 1471 -> 1472 (`0x05bf` -> `0x05c0`), leaving frame timing/exposure/analogue gain unchanged;
- if native G4 changed by itself, the sentinel is suppressed and no G4 write occurs;
- G5..G26 are always shadow-only;
- G27 remains pending at the bounded stop.

The exact DQBUF pre-write and post-write timing gates remain unchanged. The helper accounts one sentinel decision total and twenty-two G5..G26 shadow releases. A suppressed sentinel is safe but does not constitute live proof; any future live verifier must require exactly one G4 sentinel hardware transaction before declaring the new frontier closed.
