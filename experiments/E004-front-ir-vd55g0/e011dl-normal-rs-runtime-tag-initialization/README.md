# E011DL — original runtime statistics tag initialization and reuse

**PASS, bounded unchanged-source qualification.** The statistics reader contains its own first-use initializer. The previous E011DK test supplied a runtime tag-vector fixture and used a warm thread epoch; that proof remains correct within its stated boundary. E011DL executes the initializer and the unchanged CRT guard bodies, without supplying their results.

The exact seven registry fields are +C0, +D8, +48, +60, +78, +90 and +A8. The initializer ORs each value with property namespace mask 0x08000000 and writes the seven 32-bit cells at RVA17A30E0. RS is slot5 / cell17A30F4, derived from registry+90. The reader's actual guard is RVA1B303FC; original guards CE7AD8 and CE7A48 provide acquisition, publication and stale-thread epoch synchronization under owned SRW/CV resources.

| Check | New bounded evidence |
| --- | --- |
| Matrix | 192 scenarios, 576 full reader calls: four placements, two loader slots, two negative epochs, four synthetic registry sets, three record states |
| First use | Seven exact source stores per cold call; 1,344 tag-field stores total |
| Reuse | Warm and stale-thread calls preserve published tags despite changed registry inputs |
| Caller/guard join | Actual reader calls unchanged acquisition/publication helpers; 18,048 guard instruction visits reuse E011DE's bodies |
| Instruction accounting | 5,376 initializer-path visits within 262,848 total original instruction visits; totals include the previously exercised reader and guard bodies |
| Dependency rejection | 76,224 incorrect query/API bindings rejected; query slots, arguments, caller and lock ownership checked |
| Memory and ABI | Entire mapped nonstack memory and mapping permissions match the independent final model; source/code immutable, saved registers and stack redzones intact |

No-result-fixture claims apply to the tag vector and CRT guard results only. Registry objects/values, settings, metadata query returns and standard OS SRW/CV resources remain explicit owned models. This does not qualify real registry contents, the actual query body, Windows loader/concurrent wait behavior, record publication or the upstream AFD normal count policy. The 132-byte present/absent/fallback contract is reused from E011DK; absent metadata retains the old record. The default owned settings profile is checked at its exact four store sites; broader settings behavior remains unqualified.

Run `python3 -B verify.py --selfcheck` for read-only source locks, matrix/scope checks and 13 rejected evidence/scope mutations. `source-private.py` runs only on SP11 against private original bytes in Unicorn; it is authored qualification code, not an OS/driver invocation. Private exploratory versions and diagnostics stay in ../private/E011DL-explore. Earlier exploratory failures and a report-aggregation failure are excluded; accepted v9 completed with exit0 and empty diagnostics.

**NEXT E011DM:** qualify the actual metadata-query dependency (RVA5D4D30), selected registry/context/pool and RS record lifetime, then the actual normal count/offset publisher. Reuse E011M initial counts, E011AM arithmetic, E011DK decoder and E011AK sampled unity binding. No guessed normal count defaults, captured packets as runtime producers or wholesale factory scaffolding.

Required selected input/profile integration and deterministic startup/preflight remain open. Independent enabled-output IRQ/exact-buffer/generation/DMA/IOMMU retirement still precedes the finite eight-fresh-frame normal-colour front/rear/off ordinary-app milestone. Native rear runtime remains denied. Factory/enumeration acceptance remains E011DI.

No camera Starts, reboots, module loads, kernel builds, optical tests or production C changes occurred. Golden FullIO v19c, EFI/GRUB and historical checkouts are preserved. The user reaffirmed autonomous one-shot Windows oracle/external KD boots and installation of missing tools on 2026-10-03; keep original bytes and optical data on SP11 and use SP7 for external debugging.
