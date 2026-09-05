# E003i-AA — AEC/AWB trigger reconstruction oracle

Status: **prepared; Windows oracle not yet executed**.

Z proved live Linux AEC_BE/BHist/AWB_BG transport, paired exactly to TL_BG source identity. AA closes the semantic boundary needed by the front IMX681 tuning selector: `AECLuxIndex` and CCT.

Static analysis of the same SHA-pinned Surface `QcDeviceMFT8380.dll` establishes low-noise boundaries. Titan680 AEC single-IFE parsing consumes `x1` in `0x50`-byte records and writes the parsed object at `x3`. BHist's high-level parser directly consumes the raw pointer at `qword[x1+0x10]`, 1024 32-bit bins. Titan680 AWB single-IFE parsing consumes raw `x2` in `0x50`-byte records and writes through parsed object `x1`.

The downstream publishers provide request labels independently of parser-count assumptions: AEC frame-control publication carries request ID at `x0+0x6008` and LuxIndex at `float[x2+0x48]`; the AWB frame-control publication observation point carries request ID at `x23+8` and CCT at `uint32[x20+0x0c]` with RGB gains at `x20+0/+4/+8`.

The Windows oracle uses at most two ARM64 execute breakpoints at once and may run several short gated camera cycles in a single direct-Windows boot. It will dump only the exact camera statistics/parsed buffers needed for replay, hash them on SP7, and return SP11 to persistent Golden. Linux dynamic R5/R6 LSC substitution remains blocked until clean replay reproduces the request-labelled Lux/CCT fixtures.
