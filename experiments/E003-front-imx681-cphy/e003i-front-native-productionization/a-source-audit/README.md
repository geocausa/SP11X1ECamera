# E003i-A — front native productionization source audit

Status: **accepted static source/oracle audit; no runtime and no production patch yet**.

This checkpoint turns the successful 0076 runtime into a source-integration boundary without pretending the accumulated E003h experiment tree is already production code.

## Canonical base

Use the true Golden v33 reproduction source at `/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src`. Reconstruct the accepted rear R3 source with its already-maintained five-patch series. Do not use `.golden-v33-delta-replay/src` or the mutable `sp11-camera-e002k-d-src` working tree as authority.

## Front source authorities

- `0074-golden-camss-oracle.patch` is an **oracle replay** of the exact 14 CAMSS source/header files that built the successful 0074/0076 CAMSS module. It is intentionally not the final maintained production series.
- IMX681 production input is the exact accepted 0054 source, SHA pinned in `SOURCE-AUDIT.json`.
- The 0074 front DT source no longer survives as a maintained source file, so the exact successful DTB plus accepted rear R3 DTB are the mechanical DT authorities. `DT-MERGE-CONTRACT.json` records the required dual-camera union.

## Production split

Keep the proven C-PHY/CSID/VFE/RT-CDM runner, V4L2 ownership/requeue and monotonic IQ-provider semantics. Remove the disposable module parameter, sysfs run-once control, fixed firmware seeding, one-shot latch and six-frame terminal assumption.

The normal VB2 `/dev/video*` path is already the correct capture lifecycle. The next source phase must connect a real per-request IQ producer to the provider FIFO rather than retaining fixed R4/R5/R6 firmware playback.

No hardware execution is authorized by E003i-A.
