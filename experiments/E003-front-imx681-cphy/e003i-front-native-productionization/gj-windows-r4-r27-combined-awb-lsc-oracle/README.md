# E003i-GJ — combined Windows R4–R27 AWB + Tintless/LSC oracle

Status: **staged offline / unarmed / no GJ Windows stream yet.**

GJ is a strict three-request extension of the closed GD combined oracle. It reuses the same pinned DeviceMFT and the same four proven hooks:

- AWB GainAdj RVA 0x6bfa68
- AWB publication RVA 0x68fa00
- Tintless/trigger entry RVA 0x88e1e8
- final LSC staging RVA 0xa03b34

Pseudo-register ownership remains disjoint: AWB retains $t0..$t17; Tintless/LSC uses only $t18/$t19 and direct expressions.

The bounded capture range is R4..R27. R27 completion is two-sided: AWB publication sets the high completion bit in $t18, LSC staging records request 27 in $t19, and either terminal hook detaches only after observing the other side complete.

The holder still performs exactly one StartAsync and one StopAsync and waits for explicit START.GO after debugger attachment. Windows is entered only through one-shot UEFI BootNext; persistent Golden GRUB is unchanged.

The GJ analyzers have already regression-passed against GD's sealed R4..R24 evidence: AWB 21/21 bit-exact and Tintless/LSC 21/21 byte-exact.

No GJ Windows stream is allowed until verify-gj.py passes from a clean pushed commit.
