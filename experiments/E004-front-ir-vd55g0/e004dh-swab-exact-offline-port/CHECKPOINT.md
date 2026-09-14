# E004dh checkpoint — exact SWABF/SWASF offline port

Status: **CLOSED OFFLINE — Windows-authoritative SWABF/SWASF full-frame pixel parity is byte-exact; protected runtime remains unauthorized.**

## Exact Windows transfer branch

For later requests (`request_id >= 10`), E004cf proved the trusted worker executes:

`SWABF(source -> scratch) -> SWASF(scratch -> destination) -> 0x80 tail`

E004dg intentionally returns `SP11_WORKER_ESWAB_PENDING` for this branch until the transform is reproduced without approximation.

## Static contract recovered in E004dh

### SecureISP KMD tuning ABI

The exact `qccamsecureisp8380.sys` dispatch sends:

- blob type `0x1c` / SWABF through trustlet opcode `9`, payload size `0x22`;
- blob type `0x1d` / SWASF through trustlet opcode `10`, payload size `0x804`.

The same dispatcher calls the exact task-send function already dynamically identified in E004AQ (`FUN_140004a90`). This gives a clean Windows oracle point: when `x0 == 9` or `x0 == 10`, `x2` is the final tuning payload and `x3` is the exact payload length.

### DeviceMFT output packing

`CamX::IFENode::UpdateSWABFData` packages:

- 16 signed 16-bit values;
- one final signed 16-bit value;
- total `0x22` bytes.

`CamX::IFENode::UpdateSWASFData` packages:

- first 256-entry 32-bit table (`0x400` bytes);
- second 256-entry 32-bit table (`0x400` bytes);
- one final 32-bit value;
- total `0x804` bytes.

### SWASF interpolation/scaling

`CamX::IQInterface::GetSWASF101Data` constructs the two 256-entry output tables from two 64-entry floating-point source curves, linearly interpolating four substeps between adjacent control points. The recovered exact constants are:

- first-table scale: `32.0f`;
- second-table inverted scale: `256.0`.

Each result is rounded by the Windows `+/- 0.5` rule and saturated to 8-bit (`0..255`) before being written as a 32-bit table element.

### Exact Surface tuning source exists locally

The shipped Surface auxiliary-camera Chromatix binaries contain both module identities:

- `mod_swabf10_trigger_data` / `swabf10_sw_v2`;
- `mod_swasf10_trigger_data` / `swasf10_sw_v2`.

Relevant exact VD55G0 files include:

- `com.surface.tuned.aux_vd55g0_MSHW0472.bin`;
- `com.surface.tuned.aux_vd55g0_MSHW0492.bin`.

So E004dh is not relying on generic Qualcomm tuning.

## Why use Windows once more

The binary Chromatix container is self-describing but the exact runtime interpolation point depends on the live request/tuning selectors. Rather than guess the selected region from file layout, the safest parity oracle is to capture the final `0x22` and `0x804` payloads at the already-proven KMD task-send boundary during one normal Windows FaceAuth IR stream.

The oracle is read-only. It does not patch the driver, trustlet, tuning or protected memory.

## Safety

Current Linux remains Golden FullIO v19c. No Linux SecureISP runtime, CPZ runtime, CB9 enable, protected ownership transition, camera runtime or firmware modification has occurred in E004dh.

## 2026-09-14 authoritative Windows oracle update

The planned one-shot Windows oracle was executed and returned cleanly to Golden. The live Windows Camera Frame Server closed the tuning ambiguity: SWABF threshold/weights and the complete SWASF 0x804 payload are now preserved under `oracle/windows-live/`. `WINDOWS-ORACLE.md` is the normative summary.

The SecureISP static reverse was then extended to the real SWASF worker entry `FUN_18001d2a0` and its helper graph. This is explanatory reverse engineering only; it is being used to reproduce the live Windows transform, never to override it.

A scalar SWABF transcription now passes deterministic host vectors and builds freestanding for Hexagon v73 with zero undefined symbols. SWASF pixel arithmetic remains the only algorithmic portion preventing replacement of `SP11_WORKER_ESWAB_PENDING`.

## 2026-09-14 CD90 randomized Windows closure

The final SWASF combine (`FUN_18001cd90`) is now closed for the shipping Windows path. A normal SWASF init/proc established live runtime tables; a self-consistent debugger capture proved the real argument/tuning contract; then a deterministic direct Windows oracle generated 4,096 CD90 records / 32,768 lanes. `verify_cd90_random_vectors.py` compares every lane with `scaffold/sp11-swasf-cd90.c` and reports byte-exact parity.

Authoritative vector set SHA-256: `86b1851e1023d4659a50b89ff8f9ace26fe5ec344ee434066e2c5d9887702785`.

E004dh is still deliberately partial: the independently Windows-proven SWABF, C3E8 and CD90 pieces have not yet been integrated into the complete offline SWASF/full-frame path, and `SP11_WORKER_ESWAB_PENDING` must remain fail-closed until that final integrated Windows differential passes.
## 2026-09-14 full SWASF / E004dg integration closure

E004dh is now **closed for offline pixel parity**. The independently Windows-proven SWABF, helper/C3E8/C230, and CD90 stages were composed with the root-worker glue recovered from the shipping `QcISPTrustlet8380.dll`. The resulting scalar SWASF produces **0 differing bytes across the full 388,976-byte 644x604 luma plane** against the synchronized stable Windows fixture.

The root glue is now proved, not guessed: byte input is promoted by `<<2`; a clamped separable `[1,4,6,4,1]` 5x5 binomial prefilter produces the smoothed plane; raw/smoothed extrema feed the exact helper combination; C078 uses the smoothed center and live scale `253`; active p11/p12 init planes are `0x100`; the already-closed C3E8/C230 and CD90 stages consume the exact 513-dword live SWASF tuning.

The complete raw-input E004dg worker chain also passes: `SWABF -> SWASF` luma differs from the stable Windows oracle by 0 bytes, and its independently proven transfer-tail fill differs from `0x80` by 0 bytes. Complete worker-output SHA-256: `731aa107edadded21f368c01f38ad8df77c8c51a86446aacb7db105795ddcab0`.

The full SWASF scalar partial-links freestanding/non-PIC for Hexagon v73 with zero unresolved symbols (`.text=5956`, SHA-256 `4503cf8322213ca6dab12b52848bce23d8b608c43fde545d37651864dd19b37e`). The complete E004dg worker bundle also has zero unresolved symbols (`.text=7812`, SHA-256 `120f534cdfaa70b4a2e461a39a07cc6f6987846ed9741242214b10ad33c0e4fa`).

`SP11_WORKER_ESWAB_PENDING` was removed only after the full-frame chain passed. No Linux SecureISP, CPZ, protected ownership transition, camera runtime, or Windows reboot was used for this integration closure.
