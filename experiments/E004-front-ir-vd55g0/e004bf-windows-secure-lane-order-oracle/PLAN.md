# E004bf — Windows secure-lane ordering oracle

Question: at the exact Windows protected-IR lane transition, is CSIPHY0 already physically programmed?

Windows-first method:
- one bounded Windows boot;
- reuse the accepted Windows Hello / source-controller trigger;
- observe the protected-lane transition read-only;
- sample the same CSIPHY0 receiver registers immediately before lane protection and immediately after it, before the protected worker start continues;
- stop/teardown cleanly and return directly to Golden.

Purpose: determine the correct placement of the Linux parity hook from Windows behavior, not from Linux assumptions.

No Linux secure-camera runtime is part of this experiment.
