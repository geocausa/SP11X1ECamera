# DB static/offline proof

## Parent closures

DB requires corrected parent `c094198`.

- AQ/CH: active ordinary-preview T681 range is gain `1..92`, time `37,516..66,666,664 ns`, policy `0`.
- CQ: the corrected CH output domain converts bit-exactly to IMX681 FLL/VBLANK/exposure/analogue/digital controls.
- CV: generation-tagged STATS3A composes atomically through native AEC to CQ controls; Windows ownership is `request = generation + 3`; sensor pipeline delay is 2 and CamX history realign is 0.
- DA: combining Windows request ownership and CY's measured Linux write→effect delay requires release after completed `G+1`, first effect `G+3`.
- CW: the Linux four-control request is an atomic V4L2 cluster and is published under IMX681 group hold.

## Exact runtime ordering

The paired-stats thread is the sole owner of native AEC state and the DB schedule. The video thread publishes validated DQBUF completion using a C11 release-store; the stats thread reads it with acquire semantics.

For target generation 2..4 the stats thread calls `release_control_at_video_boundary()` **before** reading/processing the current target's STATS3A. The release routine:

1. waits until `video_completed_generation == target`;
2. fails without a write if the counter has already advanced past target;
3. releases the previously queued source `target-1` from the pure scheduler;
4. rechecks the exact completion generation;
5. issues the single four-control ioctl call site;
6. rechecks the completion generation after the ioctl and fails the remaining schedule if the next DQBUF arrived during the write.

Thus G1 is queued from stats G1, released at DQBUF G2, and expected at G4; similarly G2→G5 and G3→G6. G4..G6 are computed for observation/history but are never released in this bounded gate.

## Failure behavior

The pure scheduler separately models `queue` and `release`. Verification covers out-of-order queue, invalid control geometry, release without a queued source, duplicate release, explicit failure latching, post-failure queue rejection, and the corrected long-exposure sensor geometry. Any failure prevents later releases.

## Scope

DB applies sensor controls only. CQ's residual ISP gain is retained in the native output but is not written by DB. Full unrestricted/native image-pipeline AEC parity remains outside this checkpoint.
