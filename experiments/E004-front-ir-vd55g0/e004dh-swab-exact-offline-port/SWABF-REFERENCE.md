# Exact SWABF scalar reference

The SWABF arithmetic has now been transcribed into `scaffold/sp11-swabf-reference.c` using the live Windows tuning above.

The shipping Windows trustlet uses the eight-connected neighborhood in this exact order:

`(+1,+1), (-1,+1), (0,+1), (+1,-1), (-1,-1), (0,-1), (+1,0), (-1,0)`.

For each neighbor it computes `diff = neighbor - center`. If `abs(diff) < 128`, the weight index is `min(15, abs(diff) >> 1)`, the weighted differences are accumulated, and the output byte is `center + arithmetic_shift_right(sum,14)` modulo one byte.

The edge path in the Windows binary is toroidal: `x=-1` wraps to `width-1`, `x=width` wraps to zero, and likewise for y. The scalar code applies the same rule uniformly, which is equivalent to Windows' separate interior/edge/corner implementation without reproducing its thread partitioning.

Host vectors pass. The same reference compiles for Hexagon v73 as a freestanding 588-byte `.text` object with zero undefined symbols. This is still offline-only; it is neither signed nor admitted to CPZ and no protected Linux runtime was used.

A future Windows execution fixture from the shipping trustlet remains desirable as a direct dynamic byte-output check. Until that is obtained, this scalar pass is considered an exact static transcription backed by authoritative live tuning, not a substitute for the Windows oracle.
