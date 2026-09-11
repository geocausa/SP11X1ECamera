# E003i-GJ — combined Windows R4–R27 AWB + Tintless/LSC oracle

Status: **PASS / consumed — one bounded Windows stream captured combined AWB + Tintless/LSC authority through R27; Golden returned.**

GJ is the strict R27 successor to the closed GD combined oracle. It reused the same pinned DeviceMFT and the same four proven hooks:

- AWB GainAdj RVA 0x6bfa68
- AWB publication RVA 0x68fa00
- Tintless/trigger entry RVA 0x88e1e8
- final LSC staging RVA 0xa03b34

Pseudo-register ownership remained disjoint: AWB used $t0..$t17; Tintless/LSC used only $t18/$t19 and direct expressions.

Exactly one Windows holder stream captured R4..R27. The R27 terminal handshake was two-sided, both debugger and holder exited 0, 72 raw dumps were produced with the expected sizes, and no GJ_FAIL marker occurred.

Post-capture clean analysis closes the new authority tail:

- FY-based AWB replay: R4..R27 **24/24 bit-exact**
- clean Tintless/LSC replay: R4..R27 **24/24 byte-exact** for LSC0/LSC1/LSC2/GIC
- shared R27 AWB+LSC completion: PASS in the same stream

The sealed Windows evidence ZIP SHA256 is `0e6dd761bf85fb39de25bc62a93003912b77d7a0c0385220c1eb9b9ab001faeb`.

SP11 returned to protected Golden after the capture. GJ proves bounded Windows differential authority through R27; it does not claim unrestricted continuous AEC.
