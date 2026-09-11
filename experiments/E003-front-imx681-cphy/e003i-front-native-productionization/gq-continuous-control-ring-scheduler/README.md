# E003i-GQ — continuous delayed-control ring scheduler

Status: **PASS OFFLINE / generic scheduler core / no camera runtime / not live-authorized.**

GQ replaces the old fixed `pending[G1..G3]` concept with a two-slot fail-closed ring suitable for indefinite sequential generations. The operating order remains the proven GO order: compute and queue current G, then at the exact completed-video boundary G release the previous source G-1. The released source owns logical request/effect G+2, i.e. source+3.

Two slots are sufficient because a correct caller has at most two pending controls immediately before a release and one immediately after it. If a caller misses a release, the next ring collision fails instead of overwriting an unapplied control.

The verifier replays all 27 native GO control tuples through this core, proves exact source/request/effect mapping across all captured boundaries, stress-tests 100,000 synthetic generations, and exercises fail-closed cases. Effects for sources G25/G26 fall beyond the R27 evidence window and are treated as scheduler algebra only, not as live camera proof.
