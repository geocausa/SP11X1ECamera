# E011DO: original registry lock and initialized reuse

The unchanged registry initializer now executes its original default lock callbacks and complete already-initialized branch. The cold branch executes only through acquisition and its zero-bound check, then stops before registry-bound construction.

64 scenarios vary four stack placements, four pre-existing bound fixtures, two diagnostic X0 values and two OS void X0 values. One nonzero bound fixture is the scalar from E011DN's before-Start snapshot; the others are explicit synthetic bounds. Supplying a nonzero bound does not construct or qualify a registry.

| Path | Cases | Original visits per case | Result |
| --- | ---: | ---: | --- |
| Cold prefix | 16 | 65 | Stops before 0x5DE800, logical lock held, parent still active |
| Initialized reuse | 48 | 121 | Actual parent return, balanced logical lock, preserved ABI, no nonstack writes |

All 6,848 original instruction visits, 112 original callback returns and 1,232 stack-store chunks passed. The two callback bodies contribute 2,576 visits, counted inside that total. Standard OS API and diagnostics adapters account for 112 calls each and are excluded from original instruction counts. All 2,512 altered owned dependency requests rejected before effects.

## Source and dependency contract

| Derived authority | Finding |
| --- | --- |
| Original initializer 0x5DE700 | Selects table 0x1330A68 via object 0x1626898 |
| Default acquire 0x1DF30 | Calls EnterCriticalSection via IAT 0xF7E0B8 with object+8 |
| Default release 0x1DF90 | Calls LeaveCriticalSection via IAT 0xF7E0C0 with the same resource |
| Original CFG check 0x1A8C0 | One unchanged four-byte nop-check body; native CFI enforcement unqualified |
| Ghidra body 0x11F0 | 60 bytes in three disjoint ranges; gaps excluded from execution authority |
| Cold frontier | Stop BEFORE 0x5DE800; later first helper 0x5B80A8 has caller return 0x5DE844 |

Each actual source instruction is checked against the private hash-pinned image. The actual mapped memory and permissions match the entry snapshot exactly outside the independently tracked stack stores. Callback SP, X19..X29 and D8..D15 restore at the original caller return; complete initialized parent return restores the same ABI state. Stack redzones and unchanged source, IAT bindings, callback table and registry fields are covered.

OS critical-section readiness and enter/leave operations are explicit owned logical models. The diagnostics helper is an explicit no-effect model with checked original caller/arguments. Arbitrary volatile X0 values demonstrate that these declared results do not supply the original callback/reuse outcome. Native diagnostics, OS lock bytes/construction, contention and failure paths are not qualified. The callback body and parent result are not replaced by fixtures.

Cold-path exploration reached helper 0x5B80A8 after two scalar stores, but that exploration is excluded from this checkpoint: accepted cold execution stops earlier, before either store. The table's slot0 was also excluded from resource-construction proof; its OS import is DeleteCriticalSection, not InitializeCriticalSection. Full cold bounds, allocation, descriptor construction/publication, selected normal reader/profile authority and populated RS generation/lifetime remain open.

## Validation and next step

Accepted source is unchanged from private candidate v3. Candidate v1 failed because its harness assumed the wrong target register for the CFG check; it is excluded. The corrected harness validates the actual original CFG caller return addresses instead. V3 also binds the preserved scalar snapshot to the published E011DN evidence hash before emulation effects. No original instructions were patched.

Run `python3 experiments/E004-front-ir-vd55g0/e011do-original-registry-lock-reuse/verify.py --selfcheck` for matrix, source locks and scope verification. `source-private.py` reruns only Unicorn emulation and reads preserved private scalar evidence on SP11. Raw instructions, decompilation, OEM binaries and records remain private on SP11.

Golden payload hashes, boot identity, EFI/GRUB and historical repositories are unchanged. No camera Start, reboot, optical capture, kernel build, production camera C change or OS power-policy change occurred.

Next E011DP resumes at 0x5DE800 for cold-bound construction and the original 0x5B80A8 dependency. Resource readiness/construction, selected input/profile deterministic startup/preflight and independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement remain open. E011DM is still the latest original RS-query proof, E011DN the limited Windows metadata snapshot, and E011DI the separate factory/enumeration proof. Native rear runtime remains denied.
