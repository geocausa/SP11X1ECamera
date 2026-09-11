# E003i-GD — combined Windows R4–R24 AWB + Tintless/LSC oracle

Status: **PASS / consumed — one bounded Windows stream captured combined AWB + Tintless/LSC authority through R24; Golden returned.**

GD is a strict three-request extension of the closed FW combined oracle. It reuses the same pinned DeviceMFT and the same four proven hooks:

- AWB GainAdj RVA 0x6bfa68
- AWB publication RVA 0x68fa00
- Tintless/trigger entry RVA 0x88e1e8
- final LSC staging RVA 0xa03b34

Pseudo-register ownership remains disjoint: AWB retains $t0..$t17; Tintless/LSC uses only $t18/$t19 and direct expressions.

The bounded capture range is R4..R24. R24 completion is two-sided: AWB publication sets the high completion bit in $t18, LSC staging records request 24 in $t19, and either terminal hook detaches only after observing the other side complete.

The holder still performs exactly one StartAsync and one StopAsync and waits for explicit START.GO after debugger attachment. Windows is entered only through one-shot UEFI BootNext; persistent Golden GRUB is unchanged.

The GD stream was armed only after verify-gd.py passed from a clean pushed commit.

GD completed with one Windows stream. The pushed scripts used on Windows match semantically after CRLF normalization. Post-capture clean analysis passes AWB R4..R24 21/21 bit-exact using FY and Tintless/LSC R4..R24 21/21 byte-exact for LSC0/LSC1/LSC2/GIC. The two-sided R24 completion handshake fired once, both jobs exited 0, and SP11 returned to protected Golden.

The sealed Windows evidence ZIP SHA256 is 3bcc24b109de30922fc7547e072044313cdcc82f6838a8bfae6a269336a66593.
