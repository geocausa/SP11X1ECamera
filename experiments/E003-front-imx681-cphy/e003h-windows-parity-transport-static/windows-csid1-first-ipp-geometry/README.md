# Windows CSID1 first-IPP geometry checkpoint — 2026-08-31

Purpose: freeze the same-machine Windows observation that CSID1 IPP's first **complete** measured frame is already 3840x2160 at the first Epoch-bearing IRQ, while separately re-proving the current installed IMX681 mode0 timing from the exact sensor-module blob.

## Proven local bytes

- Current installed `com.surface.sensormodule.ffc_imx681.bin`: SHA-256 `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`.
- The existing clean-room `extract-mode0.py` accepts that blob and emits `CURRENT-WINDOWS-IMX681-MODE0-SUMMARY.json` with mode0 3840x2640, line length 6752, frame length 3554 and pixel rate 548570000 Hz.
- The proprietary blob itself is **not committed**.

## First-IRQ handoff observation

The completed Windows KD trace was handed off under intended filename `E003H_CSID1_FIRST_IPP_IRQ_GEOMETRY_20260831.log`, reported SHA-256 `0f69735727efd5fb37fb04fe561d1948279d343624f3305259e23e5f400e4932`.

Reported ordered events:

1. pre-active IRQ: expected/actual geometry still zero;
2. IRQ status `0x00811dd0`: `CFG1=0x7241`, crop `0x0eff0000/0x086f0000`, expected 3840x2160; actual width initialized while height is not yet complete;
3. IRQ status `0x00600228`: Epoch0/1 present and actual becomes `0x08700f00` = 3840x2160;
4. subsequent measured frames remain 3840x2160 and bit14 is never observed in the bounded trace.

This closes the conceptual ambiguity: Windows does not first measure one 3840x2640 IPP frame and crop later. Linux 0049's error-time `0x0a500f00` (3840x2640) is a crop-activation failure boundary, not normal first-frame behavior.

## Fail-closed provenance boundary

During the 2026-08-31 preservation pass the named raw KD log could not be found anywhere on the mounted Windows filesystem or retained PiSlave command-output store. `E003H_FIRST_IPP_GEOMETRY_CHECKPOINT_20260831.txt` records that discovery and the expected hash. Do **not** reconstruct a fake raw log from this README or the handoff text.

`inspect_windows_first_ipp_geometry.py` therefore requires the exact raw file and exact SHA-256 before it can return PASS. Until those bytes are recovered, the local raw-trace oracle intentionally fails closed even though the derived sensor timing evidence is reproducible and green.
