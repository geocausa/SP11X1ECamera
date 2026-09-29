# E011AC — rear BPCABF411 source tuning selection and interpolation

Status: PASS for the observed tuning-root selection, five reserve anchors and independent 107-field blend. Runtime trigger interval selection and complete E008o composition remain OPEN. Prepared parent: 0453a72ab7f0fd77266581dc7026fdd287958618; E011AB bridge parent: 69c1ec68f562d269e9aff5bae7bf20b3fc4ed1de.

One fresh Windows identity, E011AC-20260929-2140A, completed rear4K Start/Stop with 713 valid handles. Three common inputs at phase marker 0, request1 and request2 directly identify roots 0x1a, 0x100, 0x100. Two GetModule calls expose Default [(0,0)] and [(0,0),(1,1),(2,2),(3,2),(4,0),(5,0),(6,0)]. Source selector traversal resolves the first to Default and the second to Sensor1 / Video. Feature1 has value2; no feature interpretation is promoted. Earlier output-based Sensor2 guesses cannot identify this BPC branch. Other modules retain their separately proven selectors and request schedules.

## Source producer and validation

authority.py reads the SHA-pinned rear OV13858 authority locally on SP11. It reuses the existing header/symbol decoder, independently reads the 20-byte selector records, and resolves only supported unaliased direct paths with Default inheritance when a deeper mode is absent. It rejects ambiguous/linked paths, unsupported roots and foreign leaves. This is bounded BPC selection support, not a complete generic Chromatix alias resolver.

Original CheckAndUpdateChromatixData RVA0xA09430 calls GetModule at0xA09524 and returns at0xA09528. Arguments are x2=8-byte selector array and w3=count; returned module+0x120 is the runtime root. Original DataManager logging identifies root+0 as SymbolTableID. IQInterface takes the root from dependence+8 and passes reserve at root+0xA0. All three observed pointer relations agree. Runtime reserve floats1..5 exactly equal serialized root float words27..31: 15 anchor comparisons.

interpolate.py independently implements callback RVA0x94E570 over 107 fields. Inputs and ratio are binary32; FCVT promotes them to binary64 for separate FSUB/FMUL/FADD, then FCVT rounds once back to binary32. There is no fused operation. This corrects the prepared README's binary32-intermediate claim. Strict edge epsilon is binary64 1e-6; aliased source pointers copy the lower region even with an otherwise out-of-range finite ratio. The independent implementation deliberately rejects nonfinite inputs.

verify-private.py executes the original callback only in local Unicorn memory, with PAC/RETAB emulation accommodation, never in camera hardware. All 235 valid cases match byte-for-byte across all 107 fields: 25,145 matches. Cases cover installed adjacent leaves, deterministic synthetic distinct regions, edge tolerances and source-pointer aliasing. Two distinct-pointer invalid ratios are rejected with output unchanged; six authority/domain guards also reject unsupported input.

All three live regions equal leaves belonging to their directly observed source roots: 321 field matches. The explicit-leaf producer API also reproduces those 321 fields and derives seven words through the already validated E011AA common producer. Explicit leaf choices in this check are validation inputs, not a recovered exposure decision. All six Default leaves are identical across all107 fields, so cold_seed produces the complete cold region without choosing an arbitrary exposure leaf; 107 live cold fields match. Active leaves have equivalence classes, so matching region/output bytes cannot prove a unique active interval.

## Observation limits and execution record

The 14 private capture files contain three root/region/reserve triplets, two selector arrays and three interpolation vectors. Each captured 72-byte outer vector consists of three nested begin/end/capacity triplets. The nested numeric trigger vectors were NOT captured. Runtime exposure interval/ratio selection therefore remains unproven. producer.py requires explicit caller-owned leaves/ratio for active production; do not infer that policy from equal outputs.

At the first SELECT breakpoint the original observer paused on an unsupported MASM logical-OR expression before capture. Both bound scripts were repaired with nested .if guards while the same camera session remained paused; execution continued from the same instruction. This was not a new camera invocation or same-boot retry. The first SELECT metadata line appears twice, but only one first selector file was written. The corrected generator's SELECT and INTERP output exactly matches the two repaired scripts used live. The pause may affect timing; this trace proves these bounded inputs, not unperturbed timing.

The holder used atomic CreateNew at entry, a manual-only task and automatic bounded stop. The task was removed. After successful holder Stop, normal Windows reboot cleaned up the debugger; do not claim a successful normal detach. SP11 returned to Golden FullIO v19c, boot139e500e-1170-47c7-b512-36c34b2ab99b, with no camera nodes/modules/processes. Windows source and raw runtime files remain private on SP11; committed JSON contains derived facts only.

## Next gate

Source-close and bind the nested exposure trigger interval/ratio decision, then complete the remaining E008o per-packet base objects. Preserve E011AB's cold/request1/request2/request3-hold BPC schedule. Independently close VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement and ownership. Native rear Linux hardware ISP runtime remains denied. No Linux camera/module/MMIO/DMI/RT-CDM invocation was made.

Local reproduction: run python3 verify-private.py from this directory on SP11 with the SHA-pinned private tuning/DeviceMFT and E011AC private capture directory installed. VALIDATION-SAFE.json records the aggregate result; RESULT.json records the session and remaining gates.
