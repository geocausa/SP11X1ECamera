# E011AF — live AEC/context to source BPC startup lineage

Status: **SOURCE + LIVE SHARED-OBJECT LINEAGE + STARTUP COMMON/C PACKET BINDING PASS.** Complete E008o composition and independent WM16 retirement remain OPEN. Parents: E011AE0e2952a0; prepared observer102a111c; RunA/corrected hooks297a924f.

## What closed

E011AE's explicit semantic AEC/context producer now reproduces the actual startup BPC path without using captured trigger scalars, tuning regions, common outputs or register words as producer inputs.

Fresh RunB E011AF-20260930-0535B completed original rear Color/VideoRecord/NV12 3840x2160 Start/Stop with705 valid handles and250 private files. Actual driver ownership was discovered after initialization/CreateFrameReader READY; all11 breakpoints were concrete and enabled before Start.

The directly observed chain is selected gain/sensitivity fields -> generic shared vector -> ordinary typed-vector builder -> full BPC interpolation -> common calculation/packer. Pointer/thread identity, source call membership, event ordering, captured input equality and observed request transitions establish the link. The active request1/2 BPC builder uses the exact shared-vector descriptor and buffer written by the preceding generic producer.

Source caller membership comes from the installed original DeviceMFT, read-only Ghidra analysis:

| Boundary | Caller return RVA | Original containing function |
| --- | --- | --- |
| typed-vector builder |0xA08DCC|0xA08850|
| BPC interpolation |0xA08DFC|0xA08850|
| BPC common calculation |0xA08E38|0xA08850|

The function's original diagnostic identity is CamX::IQInterface::BPCABF411CalculateSetting. Its builder call at0xA08DC8 targets0x890208; interpolation/common calls are original indirect calls. The original-source membership distinguishes BPC from other observed builders using the same [2,5,1] type list. No upstream caller is guessed from an output match.

verify-live-private.py SHA-checks the original DeviceMFT and seven exact source instructions, including the primary IFE IQSetup call0x746E6C, generic setup call0x746F4C and the correct generic positive-return epilogue0x897D6C. The source order is IQSetup -> atomic observation hook0x746F18 -> generic setup.

## Request ordering correction

The observer's global request tag at the gain-selection point can still name the preceding request. In four captured transitions, the actual atomic request hook lies between gain production and generic setup. The validator requires that intervening hook plus same ISP object/thread and unchanged relevant AEC/context inputs before binding to generic setup's observed request ID. It never increments a source ID merely because the gain values match.

All three startup BPC builders are uniquely identified by their source caller, request and thread. Active request1/2 additionally require exact shared descriptor/buffer identity and full current-vector equality with the generic producer. Ordinary typed vector fields then match those actual shared inputs. The parser uses exact numeric event grammars because CDB can concatenate command text and event output on one physical line.

## Private verification

Only counts/derived code facts are exported:

- 16 selected gain fields and16 sensitivity fields reproduced from observed upstream semantic inputs/context;
- 33 snapshot metadata returns bound to those gain records;
- 16 selected-gain/generic object pairs,48 exact produced generic scalars;
-three unique startup BPC builders, two active same-request shared-object bindings;
- 18 ordinary typed-vector fields;
- 321 full source region fields,90 selected common scalars and15 reserve anchors;
- retained E006a phases0/1/2:21 exact register words.

The producer's inputs remain semantic AEC gains, sensitivities, DRC gain, resolved contexts and source mode selectors. Source tuning/algorithms calculate the outputs. Snapshot metadata lookup and full AEC algorithms are not newly ported by this checkpoint; the live producer binding is closed within the observed startup domain, not for arbitrary node/QLL/scene policy.

The cold source seed uses the independently invariant six Default leaves, not a guessed zero initial gain or the observed zero vector. The cold zero-vector producer is not independently inferred as policy.

## C startup integration

The three source-generated common states pass through the actual E011AE C binder and existing E007a register provider. All four packet semantic states,28 provider words and schedule[cold,request1,request2,held request2] match, with explicit host fixture materializer IDs4/5/6/7 preserved. Phase3's held BPC state is semantic continuity, not a new claim of captured phase3 BPC register writes; phase3 has no seven-word BPC block in the retained startup MAIN.

compile-check.c gained a bind-source private host mode to exercise the real binder on these clean-produced states. The output remains unready/unsealed. Full recursive E008o DMI validation and kernel integration are not exercised by the shape-adapter host test. E011AE's674 native input cases,1348 full downstream differential chains and existing host rejection checks still pass after this addition.

## RunA and same-session observer repair

RunA E011AF-20260929-2235A was consumed once on September30 UTC. It completed711 valid4K handles and106 private files, but the old CalculateSetting hook0x893AD0 and null-input generic return0x897DC0 were not hit. Its upstream lineage result remains INCOMPLETE. No missed-hook reason is promoted beyond the source-proven null/positive return distinction.

Its task was removed and normal reboot returned to Golden bootc04ce22e-b7f9-416c-a5b3-34b354cd7772 before fresh RunB. Corrected RunB observes the positive return at0x897D6C and the actual generic builder0x890208, filtering [2,5,1] and recording shared-object identity rather than guessing an ISP base from another wrapper.

During held RunB startup, WinDbg rejected architectural register name @x30 in caller tracing. Three own command files were changed to WinDbg's @lr; the existing paused builder at0x890208 was then observed and resumed in the same session. No second StartAsync or camera retry occurred. All complete numeric records validate; failed partial caller headers are excluded. The generator now uses @lr and checks that register alias before arming breakpoints. No further observer errors occurred after the repair marker.

RunA and RunB were distinct camera identities on distinct Windows boots, with verified Golden return between them. Raw original logs/files remain private on SP11; no successful normal debugger detach is claimed.

## State and next step

Both tasks are removed. RunB debugger cleanup used normal Windows reboot after Stop. Current idle Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 is verified with no camera modules/nodes/processes. NTFS was mounted read-only for private same-SP11 copy and unmounted. No Linux camera/module/MMIO/DMI/RT-CDM invocation, IR activation, suspend or Golden replacement occurred.

Next compose the remaining independently produced E008o base objects, combine the existing BPC and LSC/GTM binders, and validate all four unsubmitted packet objects through the full recursive contract. Independent VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains a separate hardware gate. Native rear Linux ISP remains denied.

On SP11, run python3 verify-live-private.py. Original drivers/tuning,250 RunB files and retained E006a corpus stay on SP11. LIVE-VALIDATION-SAFE.json, CALLER-SOURCE-SAFE.json, RUN-A-SAFE.json and RESULT.json contain derived facts only.
