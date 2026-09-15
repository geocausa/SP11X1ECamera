# E004ey: installed libcamera discovery

Use the exact E004ex sensor implementation, unchanged DT/CAMSS and firmware.
On a fresh one-shot boot, load the IR-only graph and run the installed cam
application once to list cameras, stream formats, controls and properties.
Enable diagnostic logs, bound the command to 20 seconds, and request no frames
through libcamera. Record the package versions and enumeration outcome separately
from capture health. Discovery is not evidence that applications can stream.

Then replay the E004ex request (1000-line exposure, analogue code 0, digital
code 256, no pattern), explicitly configure the V4L2 route, and perform one
16-frame capture through four buffers. Require the same applied status, byte
counts, sequences, clean kernel, stop and autosuspend. Preserve Golden and
retire the one-shot identity on return. No same-boot retry.

Hypothesis: the now-complete mandatory control set lets stock libcamera discover
the native IR sensor. Logs will identify remaining selection, sensor-helper,
format or pipeline requirements without inventing a replacement camera service.
