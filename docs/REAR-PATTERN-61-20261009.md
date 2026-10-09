# Rear pattern calibration run 61 (2026-10-09)

First screen-driven calibration capture. SP7 displayed a looped sequence
(sync flashes, 12 grey levels, primaries/secondaries, 2 s each) while the
SP11 rear camera captured 4,500 4K NV12 frames with AE off and a fixed
exposure/gain ladder (900 frames each). Per-frame 16x9 Y/U/V grid means,
per-frame raw IPA meter and wall-clock times were aligned to the SP7 player
log. Pixels and grid data stay on SP11; only scalars below are published.

Code: `src/native-rgb/rear-pattern61/` (capture, lib19 build, runner,
installer, analyser). Boot: rear60 kernel/modules, own one-shot GRUB entry,
systemd runner + 720 s watchdog. First attempt failed in 0.3 s on a capture
bug (both NV12 planes share one dma-buf); fixed; second attempt PASS and
returned to Golden automatically. Golden assets unchanged.

## Run facts

| item | value |
| --- | --- |
| frames | 4500 / 4500 |
| cadence | 15.0-15.5 fps |
| raw meter samples | 4500 |
| SP7/SP11 alignment | offset -0.06 s, correlation 0.968 |
| screen coverage | grid columns 0-12 of 16, all rows (57 cells r>=0.97) |

Phase 0 (800 lines, 1x) is not usable: values are not monotonic with the
displayed level, consistent with start-time controls not taking effect as
requested. Phases 1-4 (3206 lines = 33.25 ms) are consistent.

## Full-screen white and black (ROI means)

| gain | white raw meter | white Y (0-255) | black raw meter | black Y |
| --- | --- | --- | --- | --- |
| 1x | 2813 | 8.0 | 181 | 0.46 |
| 2x | 5350 | 13.3 | 205 | 0.56 |
| 4x | 10647 | 22.2 | 280 | 0.91 |
| 8x | 21510 | 36.8 | 419 | 1.45 |

* Raw meter doubles per gain step (x1.90, x1.99, x2.02): sensor gain is
  accurate and the raw path is linear and unclipped up to at least 21.5k.
* Grey ramp top-step ratio (224->255) is 1.18 at both 4x and 8x, i.e. the
  display response, not sensor saturation.
* Output Y follows raw meter^~0.73 and full-screen white at the longest
  exposure and 8x gain reaches only 36.8/255 (14%).

## Colour (8x gain)

| patch | Y | U | V |
| --- | --- | --- | --- |
| white | 36.8 | 128.2 | 127.7 |
| red | 12.0 | 123.8 | 136.8 |
| green | 26.0 | 123.8 | 123.1 |
| blue | 9.9 | 136.6 | 124.5 |
| cyan | 30.7 | 130.7 | 121.2 |
| magenta | 19.0 | 132.6 | 133.1 |
| yellow | 32.5 | 121.4 | 129.8 |

The display white point renders neutral (U/V within 0.4 of 128).

## Conclusion

The dark rear image is caused by the output side of the current private
ISP profile (gain/tone mapping from raw to NV12), not by sensor exposure,
AE or lack of light: the raw signal is linear and far from clipping while
the output stays near the bottom of its range. The replacement tuning must
set output gain and tone curve from measurement. Raw full-scale is still
undeclared; a Windows reference capture of the same pattern loop is next.

## Windows reference run 62 and matched comparison

SP11 booted Windows once (GRUB one-shot), captured the same SP7 loop through
the OEM Surface Camera Rear path (3840x2160 NV12) and returned to Linux.
Phase 0 used Windows automatic controls; phases 1-4 used manual exposure
33.25 ms with ISO 100/200/400/800, all accepted. 7,975 frames (26.4 fps
average, ~29 fps in manual phases). Windows clock was 4.4 s off after the
OS switch; alignment by luminance correlation 0.963. Comparison uses one
shared central ROI (13 grid cells, rows 2-6, cols 5-9). Values are Y (0-255).

| same exposure | white Linux | white Windows | grey128 Linux | grey128 Windows | black Linux | black Windows |
| --- | --- | --- | --- | --- | --- | --- |
| 1x / ISO100 | 22.2 | 59.0 | 9.2 | 23.9 | 0.2 | 1.3 |
| 2x / ISO200 | 35.8 | 89.7 | 16.2 | 40.8 | 0.3 | 1.4 |
| 4x / ISO400 | 57.7 | 126.1 | 27.5 | 69.3 | 0.6 | 1.7 |
| 8x / ISO800 | 91.5 | 165.7 | 45.4 | 103.4 | 1.0 | 2.1 |

Chroma distance from neutral (|U-128|+|V-128|), 8x / ISO800:

| patch | Linux | Windows |
| --- | --- | --- |
| red | 33 | 111 |
| green | 23 | 139 |
| blue | 31 | 99 |
| yellow | 19 | 61 |

Windows automatic mode settles full-screen white at Y 185 with a slightly
warm white (U 121, V 130).

At identical sensor exposure Windows output is 1.8-2.7x brighter with a
contrast (S-shaped) tone curve, and 3-6x more colour saturation. Linux
greys stay neutral but the output lacks the final tone curve and colour
correction that Windows applies. These matched pairs are the measurement
basis for an independently fitted tone curve and colour matrix.

## Measured tone curve and colour matrix (run 63)

From the matched 61/62 pairs the current Linux output path was inverted to
linear camera RGB and fitted to the Windows output: one monotone 12-bit tone
curve (257 samples, from 40 grey points) for the IFE Gamma1.5 LUT, and a
gamma-domain 3x3 colour matrix (rows sum to 1, greys stay neutral) folded
into CST12 as BT.601 x matrix. Values: `tuning/rear-ov13858-measured-v1.json`.
Module built from the rear60 sources with only those two changes
(`build-tone63.py`); capture run 63 repeated run 61 exactly. PASS, 4,500
frames, returned to Golden.

| vs Windows (same exposure) | run 61 (old) | run 63 (measured tuning) |
| --- | --- | --- |
| mean abs Y error (0-255) | 27.3 | 6.3 |
| mean chroma error | 19.7 | 9.0 |
| white level ratio 1x/2x/4x/8x | 0.38/0.40/0.46/0.55 | 0.92/0.93/0.91/0.94 |
| colour saturation ratio | 0.20 | 0.98 |

Remaining: saturated colours at high gain up to ~30 levels too bright;
Windows renders this white slightly warm while Linux keeps it neutral;
real-illuminant white balance/colour still to be measured.
