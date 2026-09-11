# E003i-GV — consumed redundant-ioctl dedupe R27 PASS

Status: **ATTEMPT1 CONSUMED / corrected verifier PASS / Golden return PASS / candidate retired.**

GV executed exactly one fresh 27-frame stream. The continuous scheduler released G1..G26 at the correct boundaries. G1..G3 used changed control tuples and produced the expected sensor-driver transactions. G4..G6 were exact-equal to the already-current G3 tuple, so their successful `VIDIOC_S_EXT_CTRLS` calls were correctly deduplicated by the Linux V4L2 control core before the IMX681 driver's `.s_ctrl`; G7..G26 remained scheduler shadow releases.

Results:

- 27/27 frames and continuous release ownership through G26;
- six successful userspace control-ioctl path calls (G1..G6);
- only three streaming sensor hardware transactions (G1..G3), plus one bootstrap transaction;
- three exact-equal redundant ioctls G4..G6 safely deduplicated before driver `.s_ctrl`;
- zero new post-G3 sensor hardware writes;
- twenty G7..G26 bounded shadow releases;
- producer/IQ path R5..R27 PASS, max pipeline 29.517331 ms;
- clean STREAMOFF and kernel-health PASS;
- no same-boot retry;
- protected Golden return PASS and candidate retired.

The original post-run verifier expected every successful control ioctl to emit a hardware transaction and therefore stopped on a count assertion. That premise contradicted the V4L2 core's `cluster_changed()` behavior. It was corrected **offline after Golden return**, and the immutable evidence then passed. See `ADJUDICATION.md`.

GV proves repeated control-ioctl lifecycle and unchanged-cluster dedupe. It does **not** prove changed post-G3 feedback. The next safe frontier is offline authority for one deliberately bounded, minimally changed post-G3 tuple before any new one-shot.
