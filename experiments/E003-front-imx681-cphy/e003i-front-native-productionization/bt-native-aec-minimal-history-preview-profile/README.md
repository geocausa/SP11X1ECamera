# E003i BT — native AEC minimal-history preview profile

Status: **PASS (native/offline)**.

BT continues BS's ordinary front-preview API reduction by projecting the three temporal history snapshots onto only the fields that the proven convergence path actually reads.

The public request state is now:

- current target log: Short, Long, Safe;
- F-1: Short/Long/Safe retained linear exposures, DRC gain, previous convergence delta;
- F-2: Short/Long/Safe retained linear exposures and DRC gain;
- PipelineDelay/F-3: Safe retained linear exposure only.

Removed history state is F-1 S1..S4, F-2 S1..S4 and previous delta, plus F-3 Short/Long/S1..S4, DRC gain and previous delta.

## Consumption proof

BasicSafe reads F-1 Safe, F-2 Safe, delayed/F-3 Safe, and F-1 previous delta. DisableStretch's temporal filter also reads F-1 previous delta, although its pinned `tempWeight=1` makes the retained contribution zero. `GetExposureInfo` is called only for Short and Long; its adjusted-history helper therefore reads F-1/F-2 Short or Long plus the corresponding history DRC gain for Short. No other history fields reach the scoped convergence result.

BT keeps the full seven-lane Windows-style history carrier private, zero-initializes it, and materializes only those public fields. Its fail-closed check is correspondingly limited to the seven retained nonzero exposure qwords (F-1 Short/Long/Safe, F-2 Short/Long/Safe, F-3 Safe).

## Verification

`verify-bt.py` fresh-runs BS, compiles BS and BT with `-Wall -Wextra -Werror -fno-fast-math`, and checks 2048 deterministic states. For every state it constructs two BS requests with identical retained history but independently randomized removed history fields. Their complete outputs must be byte-identical, and BT's compact-history output must match them byte-for-byte.

No camera stream, module load, sensor write, MMIO, Windows boot, or reboot is used.
