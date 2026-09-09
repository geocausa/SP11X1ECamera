# E003i CS — Windows AEC BHist BrightRatio ownership

Status: **PASS (static/offline)**.

CS closes the remaining ownership question behind ordinary DefaultSequence `Bank4:6` without inventing the upstream histogram value axis.  The SHA-pinned IMX681 tuning contains four fixed metering calculators before the 55 configurable calculators.  Fixed calculator 4 is `BrightRatio`, API 5 on `BhistY`, with outputs `Bank4:5..6` and range trigger `[255,256]`.  The Bank4 dictionary names those two outputs `SaturateStatsAvg` and `SaturateStatsRatio`, therefore ordinary `Bank4:6` is exactly the second BrightRatio output.

## Fixed calculator map

| ID | description | API | channel | Bank4 output |
|---:|---|---:|---|---|
| 1 | AvgLumaBE16x16 | 1 | LumaBE16x16 | 1 |
| 2 | FrameLuma | 1 | LumaBE16x16 | 2 |
| 3 | DarkRatio | 5 | BhistY | 3..4, range `[0,1]` |
| 4 | BrightRatio | 5 | BhistY | 5..6, range `[255,256]` |

`statsCalculators[55]` begins at calculator ID 11, so these four are genuinely fixed calculators rather than omitted entries from the configurable sequence.

## Runtime publication

`CCalculator::RunCalculator` reads `outputStart/outputEnd` from descriptor `+0x3c/+0x40`, reads result lane `i` from calculator storage `+0x90+i*4`, and materializes the complete 16-byte Bank4 record at `bank-manager + 0x3e88 + dataID*16`.  The Bank4 getter reads the scalar from `bank-manager + 0x3e80 + dataID*16 + 0x0c`.

API 5 calls the common histogram range kernel in two-output mode.  For BrightRatio the serialized range is exact float32 `[255,256]`.  The kernel consumes raw `uint32` counts through stats-record `+0x38`, a supplied float32 value/luma coordinate axis through `+0x40`, and emits `(weighted-average value, normalized interval mass)`.  Thus `Bank4:6` is the normalized mass/ratio for BrightRatio's `[255,256]` interval.

## BHist count and CDF ownership

The already accepted Y raw-authority proof pins front Titan680 BHist to 1024 32-bit words (`0x1000` bytes).  The pinned Windows BHist parser copies each raw word after masking to 25 bits (`0x01ffffff`); its dual-source path masks both words and adds the counts.

`CAECXStatsHistProcessor::PreprocessCoreStats` consumes the `uint32` count array and builds a per-source float32 cumulative array at `+0x148`.  It accumulates in float32 program order, selects denominator `max(1.0f, final cumulative count)`, then normalizes the CDF.  The vectorized body uses ARM64 reciprocal-estimate/Newton refinement while scalar leftovers use `FDIV`; CS therefore proves the Windows semantic/data path but does **not** claim a new bit-exact native CDF implementation.

## Deliberate boundary

The float32 per-bin value/luma axis at stats-record `+0x40` is a **proven consumer input but its upstream producer is not yet proven**.  The raw BHist parser itself produces counts, not this axis.  CS therefore does not assume a linear 0..256 mapping and does not reduce `[255,256]` to a particular raw bin.  Axis provenance is the next CT problem if it remains necessary after ordinary AEC integration.

No Linux camera module load, STREAMON, sensor write, MMIO, reboot, or new Windows oracle is performed by CS.

Run `./verify-cs.py`; acceptance requires the pinned hashes, fresh CR/Y proof chain, exact tuning records, bounded disassembly anchors, and explicit value-axis deferral.
