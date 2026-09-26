# E007j — rear GTM/TMC Windows oracle

Parent Git: `ed72bb8e` (E007i rear LSC DMI handoff PASS).

Status: **PASS — WINDOWS ONE-SHOT CONSUMED / CLEAN GTM REPLAY 15/15 EXACT**.

## Goal

Capture one bounded OV13858 rear 4K GTM/TMC sequence and determine the actual rear request-time law behind 0x5A08 selector1.

The GTM131 transform and Titan680 packing are already clean-room closed. The remaining unknown was the rear live TMC/ADRC request state. E006c proves rear GTM changes between consecutive steady requests, so front's post-R6 constant-GTM shortcut cannot be reused for rear.

## Capture

The holder reused the gated E007g rear stream: Surface Camera Rear / Color / VideoRecord / NV12 3840x2160.

It waited at `WAIT_START`; camera streaming began only after CDB had both GTM hooks armed and `START.GO` was created.

For R4..R18, the debugger captured only GTM common input (0x7c), interpolated region (0x404), flags (4), aux (2), seven source-proven sparse TMC ranges, and the final 0x800 GTM output. No optical frame bytes were copied.

The prepared identity was consumed exactly once. The holder acquired 115 valid 3840x2160 handles. All 180 expected R4..R18 capture files exist at exact prepared sizes, with zero `E007J_FAIL` markers and one R18 completion marker.

The private Windows manifest SHA-256 is:

`6abed62438b00d1607349b97e71ea1ed093dd70c962ee2d8030000f2acb3d868`

Raw Windows capture bytes remain private and are not committed.

CDB emitted repeated `execution inside an event handler` command-file warnings while the target was running. Those warnings are not used as acceptance evidence; the independent byte-exact replay below is the acceptance gate.

## Clean GTM/TMC replay — PASS

After normal return to protected Golden Linux, the Windows volume was mounted read-only solely for offline analysis. `analyze-capture.py` reconstructed only the sparse TMC state consumed by the accepted clean GTM backend and regenerated the final 0x800-byte GTM payload byte-for-byte for **all 15 requests R4..R18**.

The observed request-time law is bounded:

- R4 is startup-unique;
- R5 and R6 are identical;
- R7, R8, R9 and R10 each advance to a new TMC/GTM state;
- R10 through R18 are identical in this sequence.

For R6..R18 there are five distinct TMC states and five distinct GTM outputs. `TMC_SRC`, `TMC_DST` and `TMC_COEF` evolve together through the settling sequence. `TMC_DOMAIN`, the interpolated GTM region, flags, aux and normalized common state remain stable. The GTM bank byte alternates 0/1 independently of the normalized semantic state.

This closes the captured rear GTM transform/wire behavior and localizes the remaining producer problem to the upstream TMC/ADRC transition law. It does **not** justify hard-coding the five captured states. E007k must source-lock and reproduce their producer.

## Return state

SP11 returned to Golden kernel `7.1.5-sp11-render-parity-v4+`, boot ID `26b5fd93-7eae-4842-ac34-c93c5e50940b`. GRUB `next_entry` is empty and the camera-overlap guard passes. The Windows volume was unmounted immediately after analysis.

No Linux camera runtime, module load, DMI submission or RT-CDM submission occurred.
