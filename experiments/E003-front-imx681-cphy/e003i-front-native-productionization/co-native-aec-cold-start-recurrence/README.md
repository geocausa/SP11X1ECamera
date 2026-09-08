# E003i CO — native cold-start AEC recurrence

Status: **PASS (native/offline)**.

CO removes CM's final caller-supplied exposure-history warm-up seam. CN proves the ordinary Windows cold-start history contract: a synthetic frame-0 record exists before real history, all seven retained exposure lanes are exactly `33,333,332`, and offset lookups transition from that start record to the oldest available real record until the requested F-1/F-2/F-3 depth exists.

The native request loop now owns that contract internally. `e003i_request_loop_init()` installs the exact synthetic retained exposure state and starts at request frame 0. The public `seed_history()` API is gone. Requests must be sequential; rejected/out-of-order requests do not mutate recurrence state.

Warm-up selection is therefore:

- F0: F-1/F-2/F-3 -> START / START / START
- F1: F0 / F0 / F0
- F2: F1 / F0 / F0
- F3: F2 / F1 / F0
- F4 onward: normal F-1 / F-2 / F-3 as available.

The synthetic record's DRC history is represented as the CN-proven zero/identity state. Current output is committed only after final-target production, convergence, four-lane T681 retention, and Algorithm001 Lux update all succeed.

The verifier compares the compiled CO implementation against an independent CN history selector plus the previously verified FrameSA/CF/CG/CH primitives across 192 deterministic cold-start sequences / 2,304 requests. Complete target publication, convergence output, and four T681 results are byte-exact.

Remaining initialization seams after CO are the initial Lux trigger and Algorithm001 blend coefficient. No Linux camera module load, stream, sensor write, MMIO, reboot, or Windows mutation is used by CO.
