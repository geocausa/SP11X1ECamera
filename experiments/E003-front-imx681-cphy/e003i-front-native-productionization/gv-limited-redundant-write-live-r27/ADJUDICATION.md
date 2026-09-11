# GV Attempt 1 adjudication — verifier expectation corrected

The single GV hardware stream itself completed successfully (`HELPER_RC=0`, 27/27 frames, continuous G1..G26 releases, clean STREAMOFF). The first post-run verifier nevertheless stopped on its hardware-transaction-count assertion.

That assertion was wrong, not the captured run. The helper log name `DB_SENSOR_WRITE_OK` means the userspace `VIDIOC_S_EXT_CTRLS` call returned success. It does **not** guarantee the sensor driver's `.s_ctrl` callback ran. Linux V4L2 `try_or_set_cluster()` explicitly returns before `.s_ctrl` when `cluster_changed(master)` is false.

GV deliberately allowed G4..G6 only when their complete control tuples were identical to the last applied tuple. In this run G3..G27 were identical. Therefore the expected behavior was:

- bootstrap: one sensor hardware transaction;
- G1..G3: three changed streaming control transactions;
- G4..G6: three successful userspace control ioctls, deduplicated by V4L2 before driver `.s_ctrl` because the cluster was unchanged;
- G7..G26: twenty scheduler shadow releases;
- post-G3 sensor hardware transactions: **zero**.

Evidence matches that model exactly. The G4..G6 ioctl calls took 0.013593 ms, 0.008906 ms and 0.009895 ms, versus millisecond-scale changed transactions, and the driver emitted only four `AM request controls` records total (bootstrap + G1..G3).

The verifier was corrected offline after protected Golden return. **No second stream and no same-boot retry occurred.** The corrected verifier passes the immutable captured evidence as `PASS_CAPTURE_GV_REDUNDANT_IOCTL_DEDUPE_R27`.

GV therefore proves the repeated userspace ioctl/lifecycle path and V4L2 unchanged-cluster dedupe. It does **not** prove a new post-G3 sensor hardware write. Any next experiment seeking that proof must use a changed control tuple under a new, separately bounded authority.
