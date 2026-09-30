# E011AO — rear AWB initialization algorithm observation

Status: LIVE SELECTOR12 ORIGIN EXCLUDED / WRAPPER IDENTIFIED; exact earlier writer and numeric policy OPEN.
Fresh attempt E011AO-20260930-1250A is consumed. Preparation commit 7907e75c; source parent 4bfea598.

One Windows rear Color VideoRecord NV12 3840x2160 capture completed 859 valid frame handles, one Start and clean Stop. The atomic CreateNew holder entry was consumed once and the manual-only scheduled task was removed. Both user-mode CDB sessions explicitly detached and exited 0. No kernel debugging, BCD changes, Linux camera activation, optical-pixel saving or kernel build occurred.

The original helper entry source field was 0. Before initialization GetParam selector12 at RVA 0x831964, the same source path already carried quad 1. The verified return at 0x831968 had result 0 on the same thread and processor; the entire 92-byte BG record was unchanged. Thus selector12 is a consumer/preserver in this invocation and is excluded as this value's origin. This is a narrowing result, not a closed startup rule.

The call target is the same original QcDeviceMFT8380.dll at RVA 0x681B00, source-identified as CamX::AWBGetParam. All 128 captured target bytes match the pinned unchanged original image. The wrapper dispatches through an underlying object pointer at wrapper+0x28 and its GetParam slot+0x10. The 32-byte captured wrapper header does NOT contain that underlying object pointer; its live identity remains open.

Usecase AWBStatsControl publication0x831E00 was checked at property0x5000001D, size0x80, before its call. The valid published record contains quad 1 at+0x4C. Four AWB consumer records for request IDs1/1/2/3 all contain 1, including the first cold request. Their geometry replacement remains governed by established E011B/E011R evidence.

Nine events produced 14 private records/1,324 bytes. One auxiliary PUBLISH01_BG.bin read used the publication node at x0 rather than AWB IO; it has no source authority and is excluded. The remaining 13 records/1,232 bytes support this result. No full publication-IO byte identity is claimed.

Execution-control caveats:
- FrameServer switched process during WinRT initialization, before camera Start. The obsolete owner had zero probe events and was detached. The actual loaded DeviceMFT owner then had all five probes resolved before Start.
- Conditional before/return/publication handling unexpectedly stopped at those sites. The pair and publication were completed under direct control after checking the exact RVAs, descriptor, thread and processor. Entry/consumer probes continued automatically. This is NOT a successful unattended observer qualification; future generators need a fresh controlled rehearsal.
- The obsolete owner's module-load gate had a no-runnable-debuggees diagnostic. A queued informational CONSUMER_SITE query ran after Stop unloaded the DLL and could not resolve its symbol. Neither produced a source record. The validator explicitly checks and preserves those diagnostics.
- No camera retry occurred and the identity must never be reused.

Validation on SP11: python3 experiments/E004-front-ir-vd55g0/e011ao-rear-awb-init-algorithm-observer/validate-private.py
It checks holder multiplicity, task/debugger outcomes, event order, same-thread/object return, exact file set/sizes, private descriptor identities, target image identity, source-script copies, and the excluded record. Original payloads, raw logs, pointers and the private hash manifest remain on SP11.

Next: observe the earlier SetParam call0x83180C and GetParam selector2 call0x831920, together with the AWBGetParam wrapper delegate. Selector2's top-level output list alone does not rule out writes through its nested expected-output input descriptors. Do not hardcode quad 1 from the consumer observation. AEC cold-weight policy, normal RS/AFD counts, whole-frame offset authority, inactive cold gamma, deterministic bootstrap and independent WM16 IRQ/DMA/IOMMU retirement remain OPEN. Prior E011AM/E011AN offline zero differences are conditional on verified input records; native rear runtime stays DENIED.

Normal Windows reboot returned Golden Linux7.1.5-sp11-render-parity-v4+, boot 68454cbe-a55e-430c-8699-206bf84435bb, saved FullIOv19c, empty next_entry, no camera nodes/modules/processes. Read-only NTFS recovery was unmounted.
