# E004eu: native sensor test pattern

Hypothesis: a built-in horizontal greyscale pattern can validate the complete pixel
path independently of the very weak or absent optical signal in E004es/E004et.

Add standard V4L2_CID_TEST_PATTERN with Disabled / Horizontal greyscale. ST's
reference maps horizontal greyscale to PATGEN_CTRL 0x0201, DARKCAL_CTRL 0 and
DUSTER_CTRL 0. Read back all three. Normal capture restores the firmware's actual
processing defaults captured after initialization, rather than guessing them.
The control is cached until start and grabbed during streaming.

One four-frame capture. Unity digital gain, fixed exposure 100, GPIO outputs
disabled, corrected E004v DT and ordinary CSID0/VFE0 RDI0 route unchanged.
Require full buffers, gain/pattern readback, clean kernel, start/stop, autosuspend,
Golden return and retirement. Then analyze spatial pattern in active Y10P pixels.
No scene-image or long-running readiness claim follows from a synthetic pattern.

Result: one full buffer followed by a select timeout. No kernel fault, confirmed stop and autosuspend; Golden restored and candidate retired. Rows 8–603 exactly equal column indices 0–643; rows 0–7 are dark/reference-like data around 457. This validates 383824 pattern pixels and RAW10 decoding, but fails four-frame streaming. Additional dark rows suggest a changed frame height; this remains an inference. Next E004ev uses documented DARKCAL_CTRL=2 (bypass averaging) instead of full bypass 0.
