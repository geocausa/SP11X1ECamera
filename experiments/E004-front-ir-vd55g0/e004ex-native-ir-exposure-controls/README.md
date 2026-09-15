# E004ex: standard native IR exposure controls

Add standard V4L2 exposure (1–1891 lines, default 100) and analogue gain
(code 0–24, default 0). Idle values are cached and replayed after firmware
initialization; powered writes are checked by register readback. Gain code maps
to 32 / (32 - code), not decibels. Exposure uses the existing manual context.

Correct fixed-mode pixel-rate metadata from 84 MHz to the 137.6 MHz observed
in E004ew. Keep all transport registers, nominal link frequency, DT and power
sequencing unchanged. This is a measured mode constant, not a generic clock rule.

One fresh one-shot boot and one 16-frame stream through four buffers. Request
1000-line exposure (approximately 8.72 ms), analogue code 0, digital code 256,
and disabled test pattern while idle. Require correct published control ranges,
cached readback, applied before-stop status, consecutive complete buffers, clean
kernel, stop/autosuspend, Golden return and retirement. Do not retry this identity.
The key question is whether a standard Linux exposure request reaches the sensor.
Brightness statistics alone cannot establish image quality or scene visibility.

The 64-line exposure margin and gain encoding follow ST's reference driver and
UM2829. Firmware remains a separately provisioned local dependency; GPIO outputs
remain disabled. No protected runtime or illumination changes.

References:
- https://github.com/STMicroelectronics/vd55g0-linux-driver
- https://www.st.com/resource/en/user_manual/um2829-how-to-integrate-and-configure-the-vd55g0-device-from-a-hardware-and-software-perspective-stmicroelectronics.pdf
- https://docs.libcamera.org/master/sensor_driver_requirements.html

## Result

PASS: V4L2 exposed the expected ranges and cached the idle request. Before-stop
status confirmed 1000 lines, analogue code 0 and digital code 256 at 137.6 MHz.
Sixteen full consecutive frames passed through four buffers. Kernel health,
stop and autosuspend passed; Golden restored and candidate retired. Immediate
start status had zero exposure before the first completed frame, so it must not
be interpreted as frame-associated metadata. Pixels remain 60–69 near black;
useful scene imagery is still unproven despite the longer applied exposure.
