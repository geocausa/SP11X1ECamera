# E011DP: cold literal bounds and first-helper guard prefix

The unchanged registry initializer writes its first two bounds and enters the original first helper. That helper reaches its real fresh TLS guard, executes the original guard-acquisition body, restores the guard caller ABI and stops BEFORE its next construction dependency. No bound, first-helper or guard result fixture supplies this outcome.

128 cases vary four stack placements, two loader indices, two negative signed thread epochs, two prior bound sentinels, two diagnostic X0 values and two OS void X0 values. The parent bound and helper guard start at zero. Loader/TLS objects, initial epochs, native resource readiness and OS operations are explicit owned models.

| Derived source fact | Result |
| --- | --- |
| Literal definition 0x5DE82C, store 0x5DE830 | uint32 239 at 0x17350EC |
| Literal definition 0x5DE834, store 0x5DE838 | uint32 282 at 0x17350E4 |
| First helper 0x5B80A8 | Original caller return 0x5DE844; actual input X0 is zero |
| Fresh guard 0xCE7AD8 | Original caller return 0x5B9074; guard at 0x17A4220 |
| Original guard store 0xCE7B14 | uint32 FFFFFFFF; owned SRW acquisition/release balanced |
| Next dependency 0x2EE1A0 | Stop before entry; return 0x5B9094, pointer 0x17A7088, scalar 65535 |

The bounds are literal immediates independently checked against private original instruction operands. They are not inferred packed-table sums. The helper body is pinned to its exact 4,104-byte contiguous source extent; the older wider unwind extent is not used. Only 33 original helper visits per case are accepted, not the complete helper body.

All 18,560 original instruction visits pass: 4,224 first-helper visits, 3,328 guard-body visits and 1,536 frame-helper visits are subsets of that total. Owned OS calls (384) and diagnostics calls (128) are excluded from original counts. Exact effects are 4,992 stack-store chunks and 384 nonstack field-store chunks. All 6,528 invalid owned contracts reject before effects.

Each executed instruction matches the immutable private image. Whole mapped memory and permissions match the entry snapshot, allowing only exact independently declared field stores and tracked stack effects. Loader regions, IAT bindings, source and all other metadata remain unchanged. The original lock callback and guard preserve SP, X19..X29 and D8..D15 at their actual caller returns. Entire stack and redzones are covered. Arbitrary volatile OS/diagnostic X0 values do not supply the bound or guard outcome.

The registry logical lock remains held and both parent and first-helper frames are active at the stop. The helper guard is in-progress, not published. Full helper return, descriptor construction/allocation/publication, real native OS resource construction/contention, and selected reader/request/profile integration remain open. This fresh-prefix proof does not qualify warm/stale or concurrent helper initialization. E011DO retains its separate initialized-registry reuse acceptance; E011DI retains separate factory/enumeration acceptance.

Run python3 experiments/E004-front-ir-vd55g0/e011dp-original-cold-bounds-helper-guard/verify.py --selfcheck to check the matrix, evidence locks and scope. source-private.py reruns Unicorn emulation on SP11 with preserved private originals. Raw instruction text, OEM bytes, decompilation, records and optical material remain private on SP11.

No camera Start, reboot, kernel build, production camera C change or power-policy change occurred. Golden boot, payloads, permanent EFI/GRUB and historical repositories remain unchanged.

Next E011DQ qualifies 0x2EE1A0 in this actual caller and continues toward first-helper construction/publication. Selected input/profile deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement precede clean-colour front/rear/off acceptance. Native rear runtime remains denied.
