# E007o — rear TMC141 immediate post-return discriminator

Parent Git: `87bfc6fc` (E007n unfiltered TMC141 input oracle preparation; E007n live capture subsequently completed underneath the UI and is retained privately).

Status: **PREPARED / NOT YET CONSUMED**.

## Why this experiment exists

E007n supplied the exact TMC141 family-2 solver inputs for the useful settling window. A clean port of the source-locked seven-knot generator now reproduces the family-2 destination knots along the observed progression once the ARM64 `FRINTA` rounding semantics are respected, but the first two source knots remain different from the later GTM-facing state.

E007o answers one narrow question: **what are family-2 SRC/DST/COEF immediately after `CalculateAnchorKneePoints` returns?**

If POST matches the clean solver, the remaining difference is downstream state publication/marshalling. If POST already contains the observed GTM-facing SRC law, the missing term is inside the solver port.

## Hook

The same two direct TMC141 solver callsites proven by E007n are used:

- callsite 1: `QcDeviceMFT8380+0x9241C0`, return `+0x9241C4`
- callsite 2: `QcDeviceMFT8380+0x924258`, return `+0x92425C`

The callsite breakpoint increments a monotonic hit counter, records site/mode, saves the live descriptor pointer, captures the bounded input state, then executes exactly one `gc`.

The matching return breakpoint captures family-2 arrays through the saved descriptor pointer:

- SRC: descriptor +0x28 -> 7 f32 / 28 bytes
- DST: descriptor +0x30 -> 7 f32 / 28 bytes
- COEF: descriptor +0x50 -> 15 f32 / 60 bytes

Only H01..H20 are captured. H20 return clears all breakpoints, closes the debugger log, detaches and exits.

## Bounded input capture

Per hit:

- TUNE: 0x170 bytes
- RUNTIME: 0x498 bytes
- DESC: 0x88 bytes
- PRE_SRC / PRE_DST / PRE_COEF
- COMMON: 0x80 bytes when non-null
- CTRL: 0x40 bytes when non-null
- FACE: 0x40 bytes when non-null

The 4 KiB HIST input is intentionally **not** captured again: E007n already proved it constant across the useful H01..H19 settling window, and the exercised branch has null runtime_p7 / ctrl8254=0 so the histogram refinement helper is not invoked.

No optical pixel buffer is copied.

## Streaming discipline

`holder.ps1` is mechanically inherited from E007n and renamed to E007O. It selects the unique **Surface Camera Rear / Color / VideoRecord / NV12 3840x2160** source, creates the reader, waits for `E007O-START.GO`, runs for five seconds while only counting valid handles, then stops cleanly.

This identity is single-use through `SCRIPT-ENTRY-CONSUMED.marker`.

## Acceptance

After return to Golden Linux:

1. require H01..H20 PRE and POST family-2 arrays at exact expected sizes;
2. compare POST against the clean TMC141 generator and against E007n/E007j GTM-facing states;
3. retain only safe structural conclusions/hashes in Git;
4. never replay captured SRC/DST as a Linux producer.

No Linux camera, DMI, RT-CDM or native rear ISP submission is part of E007o.
