# E003i-HB — native cap-release helper integration

Status: **PASS OFFLINE compile/integration / no camera runtime / no live candidate yet.**

HB integrates HA's production-native cap-release policy into the consumed GS continuous scheduler helper without changing the scheduler itself.

At each exact DQBUF release boundary:

- G1..G3 use the already-proven native physical write path;
- G4..G26 consult the exact stored native AEC output for that source generation;
- if Short convergence is still cap-censored, or the native tuple is unchanged, the source is shadow-only;
- once, and only once, a below-cap changed native tuple may use the real sensor ioctl;
- after that one later write, every remaining source is shadow-only;
- G27 remains pending at the bounded stop.

HB carries no synthetic control delta. The tuple passed to the sensor is exactly the native AEC/CQ tuple already queued by GQ. `last_applied_controls` updates only after a successful ioctl, and the one-write latch sets only after a successful post-G3 ioctl.

Final accounting requires exactly the three startup ioctls plus at most one later native ioctl, and exactly 23 total post-G3 release decisions across G4..G26. The existing pre-write and post-write exact-boundary timing checks are preserved.

This closes helper integration only. A fresh live candidate still requires a separate bounded observation strategy capable of seeing a natural/controlled cap release; GZ explicitly forbids guessing a larger synthetic gain step.
