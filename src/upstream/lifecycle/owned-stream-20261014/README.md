# Owned standard CAMSS RDI lifecycle — candidate28

This ports the implemented retained native acquired-stage/reverse-unwind and safe-release/PM-retention contract to standard CAMSS/VB2. Prior implementation, history and validation scope were checked first: docs/UPSTREAM-LIFECYCLE-PRIOR-SOLUTION-AUDIT-20261014.json. Normal stop order is CSID, VFE, then PHY/sensor. Failed starts unwind successful acquisitions in reverse and preserve the original error.

VB2 cancels its queue even when a driver cannot prove hardware shutdown. Each allocator-owned MMAP plane is exported internally through the existing DMA-SG API; its private export reference retains the original pages and DMA mapping after VB2 drops its reference. No exported descriptor or sharing interface is introduced. On a propagated shutdown error, IRQ buffer bookkeeping is detached; graph, power, module and exposed allocation references are retained. A CAMSS-wide permanent fault refuses further starts until reboot. Clean shutdown releases ownership and allows restart.

Scope: one X1E RDI image owner, allocator-owned MMAP. Imported DMA-BUF and PIX admission are rejected in this prototype. Other platforms retain their existing callbacks; CPU metadata queues do not acquire DMA holds. This is not a final upstream interface decision.

## Qualification

Evidence: docs/UPSTREAM-OWNED-LIFECYCLE-VALIDATION-20261014.json.

- Actual lifecycle header: GCC and Clang, 1,137 cases each, ASan/UBSan.
- Actual CAMSS/VFE flush/VB2 DMA-SG function bodies in a deterministic kernel API model: 47 cases per compiler. Partial starts, propagated stop failures, forced queue cancellation, active/pending IRQ pointer detachment, independent mapping lifetime, allocation/export rollback, unsupported nodes, malformed graph, PM/module failures, admission limits and three clean restarts.
- Five unsafe mutations compile and are rejected at runtime.
- Preparation-template and patch replay match all five built files exactly.
- Scoped ARM64 module: W=1/-Werror, zero warnings/errors; DMA_BUF namespace and kernel26 vermagic checked. Parent source pins preserved.
- Checkpatch: zero errors, warnings or checks.

These model tests do not prove electrical signals, real interrupts, scheduling races, reset completion, measured 2.406 timing or every private native PIX startup input. Candidate28 streaming/DMA hardware remains unqualified.

## Remaining callback compatibility hurdle

No usable standalone PHY fail-closed shutdown port was found in the retained source/history searched. CAMSS csiphy_stream_off discards phy_power_off's result. The standalone provider also ignores OPP/runtime-PM/regulator release errors and returns zero. A wrapper cannot quarantine errors its callbacks hide. Resolve and qualify this gap before hardware STREAMON.

Failed-start callbacks must unwind their own partial resources. The inspected single RDI VFE output has no failing return after DMA-enable writes; sensor/PHY cleanup needs explicit error qualification. Sensor standby-write errors propagate, but its runtime-PM put still runs. Root manual unbind/device removal after a latched fault is outside this prototype's qualification. The supported fault exit is machine reboot.

These tools do not install or arm candidate28. Hardware work requires a fresh guarded identity. No camera firmware/vendor calibration/tuning, image export or OS suspend/hibernate tests.

## Reproduction

Run on SP11 in the existing project. prepare.py creates the fixed fresh candidate28 workspace and refuses an occupied identity. Use a newly named workspace for later iterations. build-worker.py uses the qualified kernel26 ABI and Module.symvers; MO keeps output outside hardlinked source.

Run test-integration.py SOURCE NEW_OUTPUT, test-replay.py PARENT SOURCE NEW_OUTPUT, and test-mutations.py INTEGRATION_OUTPUT NEW_OUTPUT. Every output must be a fresh directory. Tests extract actual pinned kernel bodies; the surrounding C file is scaffolding, not a driver copy.

The patch applies to candidate27, retaining its TPG fix, and changes five CAMSS files. Registers, sensor mode, wiring and native calibration are unchanged.
