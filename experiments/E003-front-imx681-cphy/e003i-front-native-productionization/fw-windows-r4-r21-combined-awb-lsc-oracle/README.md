# E003i-FW — combined Windows R4–R21 AWB + Tintless/LSC oracle

Status: **PASS / consumed — one bounded Windows stream captured combined AWB + Tintless/LSC authority through R21.**

FW combines the already-proven FA/FH AWB GainAdj/publication hooks with the already-proven FI/FP Tintless/trigger/final-LSC-staging hooks in one bounded Windows holder stream.

Four pinned DeviceMFT breakpoints are used:

- AWB GainAdj: RVA 0x6bfa68
- AWB publication: RVA 0x68fa00
- Tintless/trigger entry: RVA 0x88e1e8
- final LSC staging: RVA 0xa03b34

Register ownership is deliberately disjoint. AWB retains $t0..$t17 between its two hooks. Tintless/LSC uses only $t18/$t19 and direct target expressions, so it cannot clobber the AWB retained values.

R21 completion is two-sided: AWB publication sets a completion bit in $t18 and final LSC staging records R21 in $t19. Either hook detaches only when it sees the other side already complete. This prevents an early detach from losing either R21 authority.

The holder still contains exactly one StartAsync and one StopAsync and waits for an explicit START.GO file after debugger attachment. Boot to Windows is armed only through UEFI BootNext; persistent Golden GRUB is unchanged.

No Windows stream is allowed until verify-fw.py passes from a clean pushed commit.

Post-capture clean analysis is closed: FY replays AWB R4..R21 18/18 bit-exact, the clean Tintless/LSC chain replays R4..R21 18/18 byte-exact for LSC0/LSC1/LSC2/GIC, and the two-sided R21 completion handshake occurred in the same single Windows stream. RESULT.json is the durable combined authority record.
