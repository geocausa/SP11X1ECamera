# E003h 0073 — live IFELSC411 Tintless-only input boundary

Status: **accepted live-capture/static-analysis checkpoint**. The Windows capture was read-only producer observation; all boundary reconstruction is offline. No Linux camera runtime, MMIO, sensor operation, or Linux request6 submission is performed or authorized by this checkpoint.

## Live branch closure

The 2026-09-02 Windows producer session narrows the remaining LSC adaptive path substantially. Across captured requests 4, 5 and 6:

- Tintless is enabled (`common+0xc0 == 1`);
- the Tintless stats pointer at `common+0xa0` is non-null and request-local;
- the Tintless interface at `common+0xb0` is non-null and stable;
- ALSC/AWB-BG input `common+0xa8` is null;
- ALSC interface `common+0xb8` is null;
- ALSC enable `common+0x10c` is zero, with the captured ALSC state fields also zero.

Therefore this live Surface path is **Tintless-only**. ALSC/AWB-BG statistics are not a missing input for these requests.

## Exact Tintless stats contract

Two independent consumers in the SHA-pinned DeviceMFT prove the same layout. `TintlessAlgorithmWrapper::Process` at RVA `0xc95fd0` saves the request-local stats pointer, wraps it with the record count from `stats+4`, and calls the embedded core at `0xca01b0`. The preprocessing helper at `0xc9f438` and the embedded core then independently enforce/iterate the same 768-record object.

The exact fail-closed capture contract is:

1. Read `u32(stats+4)` and require **`0x300` = 768 records**.
2. Read the first stats dword and inspect **bit 1**.
3. Bit 1 clear selects **0x32-byte (50-byte) records**; bit 1 set selects **0x64-byte (100-byte) records**.
4. Both exact readers cover record indices **0..767** and their highest per-record access ends at **+0x50**.

Thus the exact maximum read from the stats base is:

- ordinary layout: `767 * 0x32 + 0x50 = ` **`0x961e` bytes (38,430)**;
- bit1/saturated layout: `767 * 0x64 + 0x50 = ` **`0x12bec` bytes (76,780)**.

Anything that fails the `0x300` record-count check or uses a different selector/layout must fail closed rather than be treated as this Surface Tintless input.

## Exact geometry in the same capture

The LSC common input is invariant across requests4/5/6:

- full sensor/calculator domain: **4048×3152**;
- crop offset: **(104, 496)**;
- output: **3840×2160**;
- scale: **1**.

This closes the request-local geometry previously left unresolved by the static mode proof.

## State-preserving replay boundary

Tintless remains stateful. The exact wrapper interface comes from `common+0xb0`; `poi(interface+0x18)` is its `0x1090`-byte wrapper context, and `poi(wrapper_context+0x128)` is the lazily allocated `0x126e8`-byte core state. The wrapper contains the already-proven `0xdf0` previous-mesh history.

The wrapper-entry capture ABI is now exact too. At `TintlessAlgorithmWrapper::Process` RVA `0xc95fd0`, `x1` is bounded to **0x130 bytes** of configuration, `x2` is the validated conditional stats object above, and `x3`/`x4` are **0x28-byte** mesh descriptors. Each descriptor carries four mesh pointers at `+0x08/+0x10/+0x18/+0x20`; each mesh is 221 float32 values = `0x374` bytes, so the input and output mesh payloads are each exactly **0xdf0 bytes**. This gives a narrow atomic capture point that isolates Tintless from the earlier Chromatix/calibration interpolation.

The preferred parity capture is therefore sequential: in one Windows stream, validate and capture each request-local Tintless stats object from stream creation through the target request using the conditional `0x961e/0x12bec` bound, while capturing the same stream's LSC wire outputs. A pre-request wrapper/core snapshot is acceptable only as a validation shortcut; the final Linux model must evolve state itself.

The four captured request4 correction-table buffers are each exactly `0x374` bytes and are SHA-pinned in the oracle. Their pointers remain stable across requests4/5/6, but pointer stability alone does not prove the contents stay constant, so replay must not assume that without same-stream evidence.

## Revised parity gate

The independent GTM transform is already closed byte-for-byte on this same live producer session. The remaining harder transform for an atomic parity capsule is now LSC only: **calibration/config + exact geometry + sequential Tintless stats/state → LSC0/LSC1**. Once those two LUTs match, wire GIC follows automatically from the proven LSC alias.

Linux request6 remains forbidden until one chosen atomic Windows producer/output stream is reproduced offline byte-for-byte and a separate runtime authorization review passes.

Proof artifacts: `prove-lsc-live-tintless-boundary.py` and `lsc-live-tintless-boundary-oracle.json`. Raw Windows capture bytes remain local/untracked.
