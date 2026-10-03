# E011DM — original RS query through selected empty slots

640 declared scenarios / 1,920 original reader phase calls execute reader 740E70, query 5D4D30, selected-slot helper 5C3758 and the E011DL guard bodies together. The query and slot helper have no return-result fixture. All 18,816 queries write actual null results through their original code; RS absence retains the entire prior 132-byte destination record.

The matrix covers four node placements, two loader indices, two negative CRT epochs, two synthetic normal-namespace registry sets, capacities 1/3/5/9 and request selectors 0/1/17/4294967303/18446744073709551615. Every scenario runs cold, warm and stale-thread phases. Empty-slot state is an explicitly declared zero at slot+30; this does not qualify initialization or publication of a populated slot.

Added query/helper coverage is 1,881,600 + 1,034,880 = 2,916,480 original instruction visits. Reader, tag initialization, CRT guard and frame helpers are inherited coverage reported separately. The owned argument/resource checks reject 356,608 altered dependency bindings; these are independent harness contract rejections, not a claim that the original Windows code safely accepts malformed objects.

Entire mapped nonstack memory and mapping permissions match an independent expected-delta model. Original code, declared node/context/pools/slots and source state remain unchanged except the explicit tag/CRT/settings updates. Incoming SP, X19–X29 and D8–D15 restore; stack redzones pass. Query return cells are checked immediately at the actual returning call, excluding reader fallthrough past calls that were skipped.

## Derived selected path

| Owner | Qualified empty path |
|---|---|
| Node | Pool pointers at +490/+498/+4A8/+4B0; normal namespace here selects +490 |
| Pool | Nonzero declared uint32 capacity at +278; inline pointer array at +298 |
| Request | TLS block+138 is the scalar request selector, not a context pointer |
| Slot | Selected pointer at array + 8 × (selector modulo capacity); disjoint owned slot identities |
| Lookup | Helper receives normalized tag, scalar 1 and node+78 |
| Query ABI | Original reader supplies a ninth uint32 stack argument of zero |
| Empty result | Original helper sees slot+30 zero and returns absence; original query stores null |

With the declared context/default state, selectors 0 and unsigned-64 maximum take both the primary and selector-1 fallback calls; selectors 1/17/4294967303 take primary calls only. This is bounded evidence for these cases, not the complete request/delta policy.

## Explicit scope

Registry values/objects, settings, node/context/pool/slot construction, file-image loader state and standard OS SRW/CV resources remain owned models. Original code runs only in local Unicorn on SP11, without loading the OEM DLL into Windows or touching camera hardware.

Private populated-slot exploration reaches helper 5DF780 → 5C0A58 and an uninitialized metadata registry dependency at image+17350E0. Slot+28 points to an additional typed object; its field+64 controls this path. That exploration is excluded from acceptance. No actual registry values, populated-record identity/generation/lifetime, normal AFD H/V count or zero-offset publisher, Windows concurrency, deterministic startup, enabled-output retirement or native rear optical result is qualified.

NEXT E011DN follows that selected metadata registry and populated-slot ownership, then the normal AFD producer. Reuse E011DL tags, E011DK copy/decoder, E011AM arithmetic, E011M initial defaults and E011AK sampled unity BG gain. Separate factory/enumeration acceptance remains E011DI.

No camera Starts, reboots, kernel builds, optical tests or production C changes. Golden, EFI/GRUB, Windows unmounted state and historical repositories remain protected. Originals, decompilation, records and optical material stay private on SP11.

Run `python3 verify.py --selfcheck` for the read-only source-lock, matrix and scope checks. `source-private.py` requires the original private image on SP11 and emits derived evidence only.
