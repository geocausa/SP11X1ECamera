# E011AV bounded source-derived cold AWB quad

Starting revision: c53a2a479f5fb816593aee85c94ccc0f42e22371. Hypothesis:
the independently parsed bgStatsConfigV1 v1.0 Default scalar field,
rather than a captured consumer value or constant, produces the initial AWB quad.

## Result

PASS for the bounded scalar field and full detached startup replay.
Three SHA-pinned applicable tuning files each have exactly one 93-byte
bgStatsConfigV1 v1.0 Default root, no same-name mode override, and quad1.
The independent portable integer C decoder reads little-endian wire+24.
The original immutable ARM64 scalar reader materializes this at runtime+32;
137 owned-memory inputs match the 28-byte scalar prefix, including mutations
that produce quad0 and nonboolean values. The latter are rejected atomically
by the clean decoder. Twelve malformed symbol/schema/selector authority cases
are rejected; compiler tests also cover malformed length, schema and null inputs.

E011AU supplies independent live lineage: runtime source+32 -> retained
actor quad -> first cold AWB record. Its 28-byte corresponding scalar prefix
agrees with the independently parsed rear source; its captured bytes are used
only for comparison. Proprietary tuning and the DLL stay private on this SP11.

The E011AS full composer and E011AR exact materialization preflight are reused
through a new additive host derivative. The input cold AWB byte is deliberately
255; the C decoder must overwrite it from the private source record before
the E011AL binder. Captured cold AWB is never read as producer authority.
GCC and Clang ASan/UBSan each pass 510,374 assertions with full packet
differences [0,0,0,0], 36,152 DMI payload bytes and inactive cold gamma.

## Scope and exclusions

This closes the numeric cold-quad policy only for the three qualified Default
roots, whose flag is invariant. Exact loaded tuning filename is not live-proven;
do not claim universal source selection or whole-profile closure.
Original scalar payload instructions and primitive reader are executed unchanged.
Owned metadata/name/security helpers and allocation are stubbed: their behavior
is explicitly outside this proof. Execution stops at RVA2372AC before the
aggregate tail; full deserialization/return is not claimed.

The earlier private whole-deserializer exploration stopped at an original BRK
in the aggregate tail because its complete reader/metadata context was not
reproduced. This is an incomplete fixture, not evidence of an original Windows
driver failure. Ghidra was read-only; disassembly/decompilation stays private.

No new Linux kernel build, integration into a reachable runtime, camera access,
reboot, module load, MMIO, submission, sleep, BCD or boot-setting change occurred.
Golden boot and all three payload hashes are unchanged. Native rear runtime
remains DENIED. Cold AEC weights and normal AWB still use independently observed
semantic inputs. RS normal count/offset policy origins, full bootstrap and
WM16 same-generation IRQ/consumed-IOVA/DMA/IOMMU retirement remain OPEN.

## Continue

Trace independent cold AEC weight initialization next; retain this bounded
source-quad decoder. Resolve RS count/offset authority and exact source-selection
requirements before final deterministic bootstrap/preflight. Do not repeat
verified AWB GetParam2/copy/writer observations, hardcode1, activate a rear
candidate or reuse consumed runtime identities. Private exploration is under
../private/E011AV* on this SP11; safe evidence is SCALAR-SAFE.json,
INTEGRATION-SAFE.json and RESULT.json.

Run offline verification on this SP11:
python3 experiments/E004-front-ir-vd55g0/e011av-rear-source-cold-awb-quad/verify-private.py
