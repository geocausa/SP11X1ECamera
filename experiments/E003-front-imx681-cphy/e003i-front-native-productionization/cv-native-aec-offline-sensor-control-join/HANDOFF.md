# CV handoff

CV joins the accepted raw-stat native AEC chain to CQ's exact IMX681 control arithmetic, still with **zero device I/O**.

Accepted mapping:

- CU cold sequence: `generation == source_seq == aec_sequence_frame + 1`;
- Windows request/stat ownership: `request_frame = source_generation + 3` (W 104/104; AP live G2->R5/G3->R6);
- IMX681 sensor pipeline depth: 2 frames for linecount/gain/FLL;
- CamX per-field history realignment: 0 because each field delay equals maxPipeline=2;
- optical latch/effect frame: intentionally unclaimed.

CV uses a shadow CP state and commits only after CU and CQ both succeed.

## Next checkpoint

Build an offline CV -> AM transport join. Reuse AM's already-live-proven group-held register transaction and V4L2 control topology, but do not open the device yet. Prove:

1. each CV tuple maps exactly to AM's cached VBLANK/exposure/analogue/digital control values;
2. the resulting group-held register byte sequence matches AJ/AM;
3. stats-owned request identity remains `G+3`;
4. the two-frame sensor pipeline remains separate from final optical latch labeling;
5. all rejection paths are no-write and recurrence-atomic.

Only after that transport/latch boundary is mechanically closed should a new bounded Linux camera runtime be considered.
