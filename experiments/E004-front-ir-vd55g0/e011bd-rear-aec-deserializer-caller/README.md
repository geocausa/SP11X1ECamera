# E011BD: original AEC deserializer entry and caller

Status: **PASS qualified entry and bounded caller source; initialization incomplete,
no camera Start; Golden returned**.

One original entry at `0x123CC0` receives alignment **1**. The actual object table
`0x1335598` and slot +8 target match before its reader is used. The original caller
returns at `0x6F35B0`; its private 192-byte code window matches the pinned original,
including the indirect call at `0x6F35AC`.

Nine loaded code ranges and four tables qualified before arming. Native PowerShell
and independent same-SP11 Python validate 21 private records / 2388 bytes. The
48-byte root and complete 404-byte grid match only
`com.surface.tuned.rfc_ov13858.bin` among the three pinned candidates. This is a
root/grid fingerprint, not proof of the exact opened filename or full selection
policy, and it has not been joined to a completed current-run named/cache flow.

## Source-qualified alignment edges

The original loader's temporary context is retained from the stack at
`0x6F22F0`. Instructions `0x6F26C4/0x6F26C8` initialize its eight-byte alignment
member +`0x48` to 1. The actual caller loads that member into its third argument at
`0x6F3594`, loads the original module's virtual slot +8, and calls at
`0x6F35AC`.

Four owned-memory initializer executions agree, preserving every other heap byte.
Twenty-four original caller-prefix executions (six field values at four placements)
forward the field exactly, preserve object/reader arguments and source heap, and
derive the target through the original vtable load. The fixture skips the guard
check at `0x6F35A8` and stops before the indirect call. Zero is a forwarding test
only; the deserializer's zero-divisor guard remains valid. The full loader,
revision/profile work and all-paths policy are excluded.

This supplies independent source initialization/forwarding evidence for the
observed packed-alignment path. No captured value becomes a producer input.
E011BB's complete four-grid proof remains its own bounded evidence.

## Run outcome and observer corrections

Identity `E011BD-20261001-0933A` is consumed. Its holder was entered once.
The first entry handler used unsupported debugger register name `x30`.
A read-only check at the still-held entry verified PC, table, slot, reader size,
alignment and supported `lr` alias. The handler then recorded that same entry
with `lr`; the incomplete first log record is explicitly rejected.

Generated grid-address quoting and the decimal28/hex1C child-reference offset were
corrected before arming. Child bounds are now checked before child-pointer use.
The failure-marker parser now distinguishes an executed marker from text inside
a debugger command. These are observer corrections, not driver fixes.

Initialization did not complete; the holder ended with result1, before READY or
START.GO. There were **zero Start/Stop calls and no frame run**. The cause of the
initialization outcome is not independently diagnosed. Prior E011BA's successful
4K run is separate evidence. The current hardware/cache hooks did not fire.

CDB explicitly detached and exited0; the manual task was removed. Normal reboot
returned protected Golden, boot `50edbeb8-e42d-41b1-8b37-3d536443604f`.
All three protected hashes are unchanged; FullIOv19c is saved, next_entry empty,
NTFS unmounted and camera idle. No production C, kernel build, kernel debugging,
BCD change, system sleep, or native Linux rear activation.

## Next work and reproduction

Resolve the complete loader/profile-selection and revision/materialization path,
then extend the full original parent fixture beyond its excluded helpers. Preserve
the fingerprint's candidate-only scope. Any further Windows observation needs a
fresh identity; never reinvoke this holder. Use `@lr`, not `@x30`, with this CDB.

```bash
python3 experiments/E004-front-ir-vd55g0/e011bd-rear-aec-deserializer-caller/entry-validate-private.py E011BD-20261001-0933A
python3 experiments/E004-front-ir-vd55g0/e011bd-rear-aec-deserializer-caller/caller-source-private.py
```

Evidence: ENTRY-SAFE, CALLER-SOURCE-SAFE, LOADED-QUALIFICATION-SAFE, CLEANUP-SAFE,
GUARD-SAFE, NEXT-SOURCE and RESULT. All original code, tuning, live addresses,
decompilation, and debugger logs remain private on the same SP11.
Native Linux rear runtime remains **DENIED**.
