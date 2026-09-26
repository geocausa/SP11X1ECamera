# E007n — rear TMC141 unfiltered call-site input oracle

Parent: E007m consumed/inconclusive plus the E007k static TMC141 contract.

Status: **WINDOWS ORACLE PASS / CONSUMED / INPUT-ONLY**.

E007m proved the two source-locked BL breakpoints resolve and the rear 4K holder streams, but its inherited request/mode early-exit logic prevented every dump. E007n therefore made no request-ID or mode assumption.

It broke at `QcDeviceMFT8380+0x9241C0` and `+0x924258`, incremented a private hit index, logged candidate request/site/mode metadata, and captured the first 40 call-site input states. The only target-resume command was one final `gc` after all dump commands had been considered.

## Live result

The one-shot completed and returned to Golden Linux.

- 71 TMC141 solver calls were observed.
- All 71 observed calls used callsite 2 and runtime mode `0x60800`.
- H01..H40 are complete: 400 bounded private capture files.
- Rear holder stopped cleanly after 116 valid 3840x2160 handles.
- No optical pixel buffer was copied.
- Private raw capture bytes remain outside Git.

Safe private-manifest SHA-256: `77e3f294e1c3cd94caa406c0d0ccd4ed4479b0ea706603f9b03efc4474b47ba6`.

## Safe offline conclusions

For the useful H01..H19 settling window:

- TUNE, descriptor, processed histogram and COMMON are constant.
- FACE count is zero.
- `runtime_p7` is null.
- curve order is 5.
- the family-2 seven-knot blend weights are all zero.
- the histogram-refinement helper is therefore not exercised on this rear path.
- runtime state, rather than scene histogram changes, carries the observed settling.
- raw ARM64 inspection corrected a Ghidra artifact: the scale-index helper uses `FRINTA` followed by `FCVTZU`, so the 1.03-step index is rounded to an integral float before unsigned conversion, not simply truncated.

The clean seven-point port now reproduces the destination-knot progression much more closely/exactly across the accepted states, while family-2 source knots 1/2 still expose one unresolved distinction between immediate solver output and later GTM-facing state.

## Next

E007o is a fresh post-return discriminator. It captures family-2 SRC/DST/COEF immediately after `CalculateAnchorKneePoints` returns for the first 20 calls. That will distinguish missing solver arithmetic from downstream publication/marshalling.

Captured-state replay is not accepted as a Linux producer.
