# E008b — rear owner / consumed-IOVA / quiescence integration

Parent Git: `6055b2aa` (E008a BUS-stop + CSID/VFE IRQ-drain PASS).

Status: **BUILD-ONLY PASS / NO RUNTIME CALL SITE**.

## Goal

Compose the three previously independent rear safety contracts into one
fail-closed source-only boundary:

1. E005y shared CSID1/VFE1 REAR owner epoch;
2. E007z ten-WM exact last-consumed-IOVA ledger;
3. E008a CSID1 producer quiesce + VFE1 BUS-stop/IRQ-drain proof.

This checkpoint still does **not** authorize native rear ISP runtime.

## Completion snapshot

`e008b_rear_observe_snapshot()` accepts an already latched/ACKed CSID BUF_DONE
snapshot. For each still-pending WM whose source-pinned completion-group bit is
set, an independent last-consumed sample is mandatory and must match that WM's
Linux-owned programmed image IOVA through E007z.

Group 0 therefore cannot retire WM0/1/2/3 by implication, and group 4 cannot
retire WM11/12 by implication.

WM16/BF accounting is passed to E005y only after E007z accepts the exact WM16
consumed IOVA. Owner epoch is sampled both before and after observation.
Wrong/missing consumed identity, stale request generation, handoff or unsafe
owner state faults the frame and pins the shared owner.

## Quiescence integration

Only a frame with all ten WMs completed, no fault, and the same REAR
owner/request may enter `e008b_rear_quiesce_and_prove()`.

The accepted front normal-stop prefix establishes **CSID -> BUS/IFE -> RT-CDM**.
E008b therefore:

1. invokes E008a CSID1 reset/quiesce and IRQ-drain proof;
2. rechecks the same E005y REAR owner epoch;
3. invokes E008a VFE1 ten-WM BUS stop + VFE IRQ barrier;
4. rechecks the owner epoch again;
5. asks E007z to prove retireability with both independent predicates true.

Any failure faults the E007z frame and calls E005y's false-safe release path,
which pins ownership until reboot instead of allowing reuse.

## Deliberate stopping point

Even a successful E008b result does **not** release the E007z ledger or E005y
owner. RT-CDM stop/close and the complete outer sensor/CSIPHY/power teardown
must be composed next. There is no DMA free/unmap, VB2 completion, requeue,
module install/load or runtime authorization here.

The next checkpoint is the complete rear stop/rollback coordinator, preserving
the accepted CSID -> BUS/IFE -> RT-CDM prefix and proving when ledger/owner
release finally becomes legal.

## Build result — PASS

The combined E005y + E007z + E008a + E008b source compiled in a fresh isolated
CAMSS copy against the protected Golden-v4 headers.

- PiMaster verifier chain: PASS;
- independent Fabric verifier/hash/vermagic check: PASS;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,691,880 bytes;
- SHA-256: `d2fd5de085f8e8990966c63b2d811b1acd217754b0ca45c5ab09b06bae54badf`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- no install/load/camera/DMA release/RT-CDM submit/ledger release.

This proves the contracts compose at build time; it does not authorize a rear
hardware run.
