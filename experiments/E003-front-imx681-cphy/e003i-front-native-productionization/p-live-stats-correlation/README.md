# E003i-P live Tintless statistics correlation — 2026-09-05

Status: **producer/consumer correlation PASS; numerical request-delay mapping remains open**.

## Authorization and scope

The user explicitly authorized needed tool downloads/installation, Linux/Windows reboots, KD, ETW/ETL, Ghidra, static/dynamic analysis, and discretionary Git checkpoints on 2026-09-05. Scope remains SP11, SP7 and PiMaster. Golden protection and evidence discipline remain in force.

## Experiment

The existing two-cycle gated Windows helper was run from a one-shot direct-Windows EFI boot. At the cycle-2 gate, the live Camera FrameServer and `QcDeviceMFT8380.dll` base were re-resolved, an on-disk KD log was opened on SP7, and global ARM64 execute breakpoints were placed on:

- `CamX::TitanStatsParser::ParseTintlessBGStats`, RVA `0x5f09d0`
- the active Tintless wrapper, RVA `0xc95fd0`

The breakpoints recorded parser raw/output pointers, process/thread identity and the Tintless X2 statistics pointer. Global execute breakpoints were used so service bookkeeping could not silently invalidate a process-scoped breakpoint. The raw debugger log remains on the SP7 lab disk and is intentionally not committed.

## Result

The accepted raw log is `E003I-P-CORRELATION2-20260905_1908_2026-09-05_01-42-24-701.log`, 85,407 bytes, SHA256 `00e1ed5aa588f9fc1d3723ada477ccdda92c8558419a8ef2637ceffc0573a789`.

Fail-closed extraction gives:

- Titan680 parser hits: **153**
- Tintless calls: **150**
- Tintless calls whose X2 pointer exactly equals the immediately preceding parser output: **150/150**
- same-process pairs: **150/150**
- same-thread pairs: **150/150**
- parser generations superseded before any Tintless consumption: **82, 84, 104**
- first Tintless call observed at parser count **1**, not after four parser outputs

Therefore the direct parser-output → Tintless-input handoff is dynamically closed. The parser hit counter is **not** a request identifier and the trace does not establish a fixed numerical request delay. The old inferred four-request mapping remains fail-closed and must not be used as authority.

The important production consequence is positive: Linux should expose TL_BG as a **generation-tagged latest completed snapshot**, not as an unlabeled buffer and not as a parser-count FIFO. A consumer must observe the explicit generation and tolerate/detect skipped generations. This matches the Windows behavior in which three parser outputs were superseded before a Tintless call.

`analyze-live-stats-correlation.py` refuses any raw log whose SHA differs from the accepted log and mechanically verifies all 150 pointer/process/thread pairs plus the exact three superseded generations.

## Safety / return

Breakpoints were cleared, the KD log was closed, SP11 was rebooted through the unchanged default boot path, and Golden Linux `7.1.5-sp11-render-parity-v4+` returned with `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, hardened `clk_ignore_unused pd_ignore_unused`, and camera modules unloaded.

## Next gate

Implement a bounded Linux read-only TL_BG snapshot on the existing front PIX V4L2 surface. Copy exactly `0x25800` bytes only after the corresponding TL_BG completion generation is observed and while the owning aux slot is still pinned, then publish explicit snapshot/source generations. Do not claim request-number mapping from this checkpoint.
