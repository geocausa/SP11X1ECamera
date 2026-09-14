# E004dp — unified RGB + IR bind / receiver-only coexistence one-shot

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

Parent E004do proves that the accepted rear/front RGB graph and native VD55G0 IR graph coexist in one DTB without changing accepted RGB sensor/endpoint semantics. E004dp is the first bounded runtime gate on that combined tree.

This is deliberately **not a camera-streaming test**. One fresh one-shot candidate may:

- bind accepted OV13858 rear RGB, IMX681 front RGB and native VD55G0 IR simultaneously;
- leave all rear/front mutable route links neutral;
- leave the VD55G0 in its proven Windows-state `SW_STBY`, runtime-suspended state;
- arm only the already-proven E004j CSIPHY0 D-PHY receiver parity parameter;
- run only the E004t receiver harness, which powers/programs CSIPHY0, reads the 96 Windows-authoritative receiver registers, powers CSIPHY0 off and checks VD55G0 PM did not change.

It may **not** start any rear/front/IR sensor stream, mutate RGB media links, call IR illumination, start CSID/VFE capture, use Linux SecureISP, enable secure CB9, migrate CPZ/protected ownership, or invoke the protected worker.

## Runtime CAMSS provenance

The accepted RGB runtime module `7afe6ed0...` initially failed to reproduce after the kernel header wrapper was repointed on 14 September from the historical source pathname `sp11-camera-e002k-d-src` to `.golden-v33-delta-replay/src`. The underlying headers are byte-identical. Rebuilding through the historical wrapper pathname and the exact historical work-layout reproduces accepted `7afe6ed0...` **byte-for-byte** from the current accepted CAMSS Git tree.

Applying only the SHA-pinned E004k patch (`1fc0f918...`) to that exact lineage produces E004dp CAMSS SHA `862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7`. The gate remains false by default and is scoped to X1E80100 + CSIPHY0 + D-PHY.

The E004dp build script refuses to package this candidate unless the unpatched baseline first equals `7afe6ed0...` exactly, and it restores the modern kernel build wrapper afterward.

## Other pinned runtime artifacts

- three-camera DTB: `3d56fd6f...` (E004do);
- native VD55G0: `4839415e...` (exact E004l accepted build);
- receiver harness: `6475d453...` (exact E004t accepted build);
- IMX681: `ef57ed06...`;
- OV13858: `13a8ad95...`.

## Acceptance

One attempt only. All three sensor entities and immutable sensor→CSIPHY links must be present simultaneously. The rear/front route classifier must remain neutral. All three sensors must be runtime-suspended before the receiver harness. E004t must report Windows receiver readback `96/96`, no mismatch, receiver off, sensor still suspended, and zero sensor/CSID/VFE stream callbacks. Any failure returns immediately to protected Golden; no same-boot retry.
