# E003i CC — native AEC ADRC / dark-boost tail

Status: **PASS (native/offline)**.

CC transcribes CB's ordinary/default Windows AEC arithmetic tail into a small native C primitive. The caller supplies the already-published Lux, Safe adjustment ratio, Short target and Long target; the primitive emits the exact intermediate/final float publications needed immediately before convergence target SI construction.

The native sequence is:

- `ADRC cap = Windows method-2 Lux curve`;
- `AdjRatioShort (3:66) = SafeAdjRatio (3:9) / ShortTarget (3:10)`;
- `ADRCGain (3:67) = MIN(Windows short method-2 ramp, ADRC cap)`;
- `Short AdjRatio (3:11) = SafeAdjRatio / ADRCGain`;
- `DRCGainRemainder (3:157) = 8 / ADRCGain`;
- `AdjRatioLong (3:68) = LongTarget (3:12) / SafeAdjRatio`;
- `DarkBoostGain (3:69) = MIN(Windows Long primary method-2 branch, Windows remainder method-2 branch)`;
- `Long AdjRatio (3:13) = SafeAdjRatio * DarkBoostGain`.

The Long remainder branch is implemented in full even though CB proves it cannot win under uninterrupted ordinary DefaultSequence. This keeps the primitive faithful to the Windows expression rather than baking in that dominance proof as a shortcut.

The implementation also deliberately retains two counter-intuitive float32 behaviors. A Short nominal identity-ramp input `0x3fbe7879` publishes `0x3fbe787a`, and a Long equal-child outer-gap interpolation publishes `0x3f8ccccc` when the child itself is `0x3f8ccccd`. Direct clamp/identity/equal-endpoint simplifications are therefore forbidden.

The verifier fresh-runs CB, compiles the native source with `-fno-fast-math -ffp-contract=off`, checks fail-closed inputs, covers 4,536 boundary combinations and 16,384 deterministic finite-positive differential cases against an independent instruction-ordered float32 model. Two complete runs are byte-identical.

No camera module load, stream, sensor write, MMIO, Windows boot, or reboot is used.
