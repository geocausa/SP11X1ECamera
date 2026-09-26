# E006v — Titan680 RSStats14 semantic startup packer

Parent Git: 12f48d0e (E006u rear BHist16 compile PASS).

Status: **STAGED / COMPILE PENDING**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Close the four RSStats14 startup-only words from adjusted semantic AFD/RS state:

- 0xBE60
- 0xBE68
- 0xBE6C
- 0xBE70

Captured Windows register values are validation only and are not embedded.

## Exact Titan680 packing

Pinned Surface QcDeviceMFT8380.dll source-locks IFERSStats14Titan680:

- CreateCmdList writes 0xBE60 count 1 and 0xBE68 count 3.
- PackIQRegisterSetting forces enable bit 0, places color-conversion state at bit 4 and shift at bits 8..11.
- 0xBE68 packs 13-bit horizontal and 14-bit vertical offsets.
- 0xBE6C packs H_NUM-1 in 4 bits and V_NUM-1 in 10 bits.
- 0xBE70 packs region width-1 in 13 bits and region height-1 in 4 bits.

## Modern semantic producer boundary

Direct decompilation of the current RSStats14::AdjustROI path, rather than assuming the older open-source implementation is identical, closes the adjusted-state constraints:

- H regions 1..16.
- V regions 1..1024.
- region width 2..8192.
- region height 2..16 and even.
- vertical offset is even.
- shift = max(bit_length(region_width * region_height) - 4, 0), with 12-bit input and 16-bit row-sum output.

The packer consumes that adjusted state. AFD policy, stripe decisions and generation of the requested RS geometry remain upstream producer concerns; this checkpoint does not freeze one captured AFD configuration.

An earlier hidden/incomplete draft had allowed region width 1. The direct modern AdjustROI trace corrected that boundary to a minimum of 2 before staging.

## Startup topology and private validation

The safe E006k symbolic recipe proves startup1, startup2 and startup3 each emit the exact RS two-range shape; startup4 omits RSStats14 entirely.

The retained private E006a oracle was decoded locally only for validation. In all three emitted startup phases, inversion to semantic state followed by the clean packer reproduces all four words exactly, including the modern shift rule; startup4 has no RS block. No raw register values or packet bytes are committed.

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**. Upstream Linux AFD/RS state production must eventually supply these semantic inputs for full parity.
