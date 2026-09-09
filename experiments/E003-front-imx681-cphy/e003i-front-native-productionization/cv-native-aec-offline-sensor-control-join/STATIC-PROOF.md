# CV static/offline proof

## Parent closures

- CU (`8c660bf`) closes generation-tagged STATS3A through measured luma, CT Bank4, CR analyzers and CP recurrence.
- CQ closes CP/CH Short T681 into exact IMX681 FLL/VBLANK/coarse/analogue/digital/ISP controls against Windows and AJ.
- W proves 104/104 request/statistics matches obey `request_frame = source_generation + 3`.
- AP live-corroborates `R5<-G2` and `R6<-G3`.
- AV proves linecount/gain/FLL delay `2`, `maxPipeline=2`, `frameSkip=0`, and zero CamX history realignment.

## Composition

`e003i_raw_request_to_imx681_controls()` copies CP state to `shadow`, calls CU on the shadow, maps stats ownership by `generation + 3`, calls CQ on `raw.request.short_arbitration`, and commits `shadow` only after every step succeeds.

This preserves CP's canonical ordinary single-exposure lane rule already consumed by CQ. It adds no new exposure arithmetic.

## Delay semantics

CV exports:

- `stats_owned_request_frame = stats_generation + 3`;
- `sensor_pipeline_delay_frames = 2`;
- `camx_history_realign_frames = 0`.

It intentionally does not export an optical-effect frame. The two-frame sensor delay is a pipeline-depth fact; the exact optical latch/frame label remains for the group-held frame-boundary join.

## No-I/O proof

The CV source/header are scanned for device/I/O primitives and contain no `open`, `ioctl`, `VIDIOC`, `cci_write`, I2C path or `/dev/` reference. All inputs are memory buffers and all outputs are plain structures.

## Differential acceptance

The verifier compiles CV+CU+CQ and all native AEC dependencies using `-fno-fast-math -ffp-contract=off`. Four generated STATS3A frames are processed twice:

1. through CV;
2. through CU then CQ manually on an independent state.

For every frame the complete CU raw output, CQ control structure and recurrence state must be byte-identical. The wrapper must also emit G1->R4, G2->R5, G3->R6, G4->R7 and AV's `2/0` sensor-delay/history-realignment pair.

A bad-size input is additionally required to leave caller recurrence state byte-exact.
