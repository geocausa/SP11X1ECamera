# E003i-GT — limited redundant-write authority

Status: **PASS OFFLINE policy / no camera runtime / no changed post-G3 controls authorized.**

GS proved live scheduler ownership at every R27 release while suppressing all post-G3 sensor ioctls. GT defines the first deliberately tiny physical-write expansion:

- G1..G3: existing proven startup writes;
- G4..G6: a physical write is allowed **only** when the complete control tuple is bit-identical to the last actually applied tuple;
- any changed G4..G6 tuple: no write, shadow-only;
- G7 and later: shadow-only regardless of equality.

This separates repeated-ioctl/lifecycle proof from changed-exposure feedback. The policy compares the complete control structure including ISP gain bits, so the redundant-write gate is intentionally stricter than the physical V4L2 register set.

The GS evidence used here has G3..G27 control tuples identical, so G4/G5/G6 satisfy the redundant gate in that consumed run. A future scene is not assumed to do so; the candidate must decide at runtime and remain no-write on any difference.
