# E004dg — source-controlled parity worker, offline compile/test

## Result

**PASS / CLOSED OFFLINE: the source-controlled parity worker now reproduces all three Windows transfer branches, including the later `request_id >= 10` `SWABF -> SWASF` path. The authoritative 644x604 synchronized Windows stable fixture is byte-exact across all 388,976 luma bytes, the worker's explicit `0x80` NV12 tail contract is exact, and the complete freestanding Hexagon-v73 bundle partial-links with zero unresolved symbols.**

This remains an offline engineering artifact. It is not signed, admitted, installed, or loaded into CPZ, and Linux SecureISP runtime was not used.

## Worker ABI and memory boundary

The request preserves the already-proven Windows/Linux transfer contract: source and destination pointers/extents, geometry, request ID, payload offset, captured/serialized extents, synthetic selector, plus a caller-owned work buffer used only by the later SWAB path. The worker performs no allocation, syscall, FastRPC operation, ownership change, or secure-runtime action.

The work buffer contains the SWABF luma scratch and two signed-16 SWASF planes. Its alignment and exact required extent are checked before the later branch touches it.

## Exact Windows branches

The worker now implements:

1. synthetic: `Y=100`, tail=`0x80`;
2. `request_id < 10`: copy luma, tail=`0x80`;
3. `request_id >= 10`: `SWABF(source -> scratch) -> SWASF(scratch -> destination) -> 0x80 tail`.

The third branch composes the Windows-proven SWABF scalar with the E004dh full SWASF scalar, which itself composes the Windows-proven local-extrema/activity helpers, C3E8/C230 stage, CD90 final combine, exact live 513-dword SWASF tuning, and exact worker glue.

`SP11_WORKER_ESWAB_PENDING` is no longer part of the worker ABI because the complete two-stage path passed the Windows full-frame differential before that pending state was removed.

## 644x604 Windows differential

Input: `e004dh-swab-exact-offline-port/oracle/windows-sync-oracle/input-644x604-nv12.bin`.

Primary deterministic target: the luma plane of `windows-trustlet-sync-swasf-644x604-stable.bin`.

Result:

- luma bytes compared: 388,976;
- luma differences: **0**;
- stable Windows SWASF luma SHA-256: `591a706fcb1710b8aa152f4f672c5954e181fa783a09e3d9d4be038b3c6202f7`;
- worker neutral-tail differences: **0**;
- complete worker-output SHA-256: `731aa107edadded21f368c01f38ad8df77c8c51a86446aacb7db105795ddcab0`.

The synchronized standalone trustlet fixture preserves the input UV bytes, whereas the separately reversed transfer worker explicitly overwrites its tail with `0x80`. Therefore the correct integrated differential is stable Windows SWASF luma plus the independently proven worker neutral-tail contract; replacing the tail with the standalone fixture UV would contradict the Windows transfer dispatcher.

## Preserved Windows race behavior

The deterministic scalar result matches the stable fixture exactly. The two preserved Windows race captures remain documentary evidence of Windows' own eight-worker scheduling nondeterminism:

- race A: 34 luma bytes on rows 320 and 560;
- race B: 1 luma byte on row 243;
- UV differences: 0 in both.

Those race bytes are not normalized into the scalar algorithm.

## Hexagon-v73 closure

All constituent sources are compiled freestanding and non-PIC for Hexagon v73, then partial-linked into one relocatable bundle.

- ELF32 Qualcomm Hexagon relocatable;
- `.text = 7,812` bytes;
- zero unresolved symbols;
- bundle SHA-256: `120f534cdfaa70b4a2e461a39a07cc6f6987846ed9741242214b10ad33c0e4fa`;
- exported worker plus SWABF/SWASF/C3E8/CD90 symbols are present.

The explicit non-PIC build avoids a toolchain-generated `_GLOBAL_OFFSET_TABLE_` dependency and is the correct freestanding form for this offline bundle.

## Safety boundary

No protected buffer, dma-heap runtime allocation, FastRPC ioctl, CPZ process, secure CB9 enable, ownership transition, camera runtime, Windows reboot, or Linux SecureISP runtime action occurred during this integration closure.

## Next gate

Offline image-algorithm parity is closed. The remaining camera work returns to protected-worker delivery/admission/signing and the already-defined protected-memory ownership path. Signature verification must not be bypassed, and Linux SecureISP runtime remains unauthorized until explicitly approved.
