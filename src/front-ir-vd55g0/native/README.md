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
firmware redistribution/provisioning policy, standard exposure/gain and frame-duration
controls backed by evidence, selection/orientation metadata, and compliance/lifecycle
testing on hardware. Existing fixed pixel-rate/timing values preserve the historical
board authority and are not a newly verified frame-rate claim.

The historical bind-only driver remains frozen for existing reproducibility checks.
Do not load both drivers for the same sensor. E004es proved bounded RAW10 transport; E004et proved standard digital-gain readback.
Both captured only black-level pixels. E004eu tests an internal greyscale pattern.
Digital gain is a standard V4L2 control. Test-pattern selection is locked during
streaming and uses the sensor firmware defaults when returning to normal capture.
