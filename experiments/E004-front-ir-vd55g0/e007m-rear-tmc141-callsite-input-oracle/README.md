# E007m — rear TMC141 call-site input oracle

Parent: E007l consumed/inconclusive plus E007k static TMC141 contract.

Status: **CONSUMED / INCONCLUSIVE — RETIRED. DO NOT RERUN.**

The fresh one-shot streamed successfully (114 valid 4K handles), but the inherited pre-dump filtering caused every breakpoint action to continue before any dump or input marker was emitted. The oracle log contains 71 target-execution/event-handler warnings, zero E007M_INPUT markers, zero completion markers and zero raw input files. E007m is permanently retired. E007n removes all request/mode early-exit filtering and captures a bounded sequential hit window before the single final `gc`.

E007l is permanently retired: its in-callee conditional plus return breakpoints produced CDB expression/event-handler failures and zero solver dumps.

E007m instead breaks at the two source-locked BL instructions that call TMC141's anchor solver:

- QcDeviceMFT8380+0x9241C0 (site 1)
- QcDeviceMFT8380+0x924258 (site 2)

Immediately before either BL, x0/x1/x2 already contain the solver tuning block, request/runtime state and descriptor. The branches are mutually exclusive. There are no solver-entry or return breakpoints.

For rear R4..R18, gated by dwo(x1+8)==0x60800, E007m privately captures TUNE, RUNTIME, DESC, the 1024-float processed histogram, PRE_SRC/PRE_DST/PRE_COEF and bounded optional COMMON/CTRL/FACE slices. Files are tagged S1/S2 so evidence cannot overwrite if an unexpected second invocation occurs.

No optical pixels are copied. Raw values stay private.

Acceptance is offline: produce SRC/DST semantically from these inputs and compare to the already accepted E007j post-solver vectors; then regenerate COEF with E007k's proven helper. Captured-state or request-number replay is not accepted.
