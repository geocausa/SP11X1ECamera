# BT proof boundary

BT is a native request-state projection over the already-verified BS convergence implementation.

Exact reads in the scoped kernel are:

- BasicSafe: F-1 Safe, F-2 Safe, F-3 Safe, F-1 previous delta;
- DisableStretch filtering: F-1 previous delta;
- `adjusted_history_lane()` through `GetExposureInfo(t=Short|Long)`: F-1/F-2 Short or Long and DRC gain (DRC gain affects Short only);
- `GetExposureInfo`: F-1 Safe in addition to the lane-specific values above.

There are no reads of F-1/F-2 S1..S4, F-2 previous delta, or any F-3 field except Safe. The old all-seven-lanes nonzero validation was only a generic carrier guard; BT replaces it with validation of precisely the exposure fields that are actually consumed.

The differential proof varies every removed BS history field while holding all retained fields fixed, then compares the entire output struct against BT for 2048 states. Equality is byte-for-byte, not tolerance-based.

This does not change or project locked/HDR/multi-exposure modes.
