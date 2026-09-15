# Native VD55G0 capture candidate

This is the maintained candidate for ordinary Linux RAW10 capture on the Surface
Pro 11 camera module. It builds independently of Windows packages. Its required
runtime firmware is st/vd55g0-sp11-cut1.bin (552 bytes), supplied separately and
verified by the local experiment builder. Firmware is not embedded or redistributed.

The initial mode is fixed at 644x604, RAW10, one D-PHY lane and a 420 MHz link.
The board power sequence and mode table come from verified same-machine evidence.
GPIO outputs are disabled; the driver provides no illumination control. Stream
start/stop uses the V4L2 subdevice stream API and runtime PM. No protected-memory
or DSP-service policy belongs in this sensor driver.

This is a board-specific candidate, not an upstream-ready submission yet. Remaining
upstream work includes consolidation with ST's sensor support, a reviewed binding,
firmware redistribution/provisioning policy, frame-duration control,
selection/orientation metadata, and compliance/lifecycle testing on hardware.
E004ew measured a 137.6 MHz timing clock and 16 consecutive frames through four
buffers. Pixel-rate metadata now reflects that measured fixed mode. The nominal
420 MHz link setting is unchanged; it is not a measurement of the physical link.

The historical bind-only driver remains frozen for existing reproducibility checks.
Do not load both drivers for the same sensor. E004es proved bounded RAW10 transport; E004et proved standard digital-gain readback.
Both captured only black-level pixels. E004ev proved four exact full-frame greyscale patterns after correcting dark-row
handling: bypass averaging, not the whole dark-calibration block.
Read-only status snapshots report actual clocks and applied controls for validation;
they are sequential observations rather than atomic per-frame metadata.
Digital gain is a standard V4L2 control. Test-pattern selection is locked during
streaming and uses the sensor firmware defaults when returning to normal capture.

Exposure (1–1891 lines, default 100) and analogue gain (code 0–24, default 0)
are standard V4L2 controls. Analogue multiplier is 32 / (32 - code). Idle
updates are cached, then replayed after initialization; powered writes are
checked by readback. E004ex validates a 1000-line exposure request.
