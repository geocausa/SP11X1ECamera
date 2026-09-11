# E003i-GD — combined Windows R4–R24 AWB + Tintless/LSC oracle

Status: **staged offline / unarmed / no GD Windows stream yet.**

GD is a strict three-request extension of the closed FW combined oracle. It reuses the same pinned DeviceMFT and the same four proven hooks:

- AWB GainAdj RVA 0x6bfa68
- AWB publication RVA 0x68fa00
- Tintless/trigger entry RVA 0x88e1e8
- final LSC staging RVA 0xa03b34

Pseudo-register ownership remains disjoint: AWB retains $t0..$t17; Tintless/LSC uses only $t18/$t19 and direct expressions.

The bounded capture range is R4..R24. R24 completion is two-sided: AWB publication sets the high completion bit in $t18, LSC staging records request 24 in $t19, and either terminal hook detaches only after observing the other side complete.

The holder still performs exactly one StartAsync and one StopAsync and waits for explicit START.GO after debugger attachment. Windows is entered only through one-shot UEFI BootNext; persistent Golden GRUB is unchanged.

No GD Windows stream is allowed until verify-gd.py passes from a clean pushed commit.
