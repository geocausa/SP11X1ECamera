# E003i-GU — limited redundant-write helper integration

Status: **PASS OFFLINE compile/integration / no camera runtime / changed post-G3 controls remain blocked.**

GU integrates GT's deliberately small repeated-write policy into the consumed GS live-shadow helper while preserving GQ's continuous scheduler and GS's exact DQBUF boundary gates.

Runtime policy encoded by this helper:

- G1..G3 use the already-proven physical write path;
- G4..G6 may reach the same physical ioctl only when the entire candidate control tuple exactly equals the last successfully applied tuple;
- any changed G4..G6 tuple is shadow-only;
- G7..G26 are always shadow-only;
- G27 remains pending at the bounded R27 stop.

Every successful real ioctl updates `last_applied_controls`; a failed or suppressed write never does. The final accounting gate requires exactly three startup writes plus at most three redundant writes, exactly three combined redundant-or-changed decisions for G4..G6, and exactly twenty bounded shadow decisions for G7..G26.

This is the offline integration gate only. It does **not** authorize changed exposure/gain writes after G3.
