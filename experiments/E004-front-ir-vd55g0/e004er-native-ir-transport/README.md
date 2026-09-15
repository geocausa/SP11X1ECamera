# E004er: native Linux IR transport

The user selected native Linux development as the primary route and authorized
implementation and bounded hardware tests on SP11/SP7 using PiMaster.
Windows remains the authority for board behavior and an image-quality reference.
This experiment intentionally uses ordinary Linux memory and does not claim
Windows Hello ESS security parity. Protected-runtime work remains inactive.

## Hypothesis

The verified VD55G0/CSIPHY0 sensor can feed the existing CAMSS CSID0 RDI0 and
VFE0 RDI0 pipeline when Linux owns the ordinary route. The existing driver
already negotiates Y10P. This route is not the protected Windows IR route.

## Implementation

`src/front-ir-vd55g0/native` retains the verified board power/mode sequence,
loads the separately supplied sensor firmware using request_firmware(), disables
the GPIO1 strobe selector with ST's documented input-mode value, and verifies
all four GPIO selectors before streaming. The V4L2 stream API holds a runtime
PM reference across capture, polls start/stop completion, and asserts reset
on command failure. No secure ownership calls or protected apertures are used.
The canonical RGB and protected-worker source trees are unchanged.

## Candidate

`build.py` creates a fresh output and records source/artifact SHA256 values.
`candidate.py install` copies Golden kernel/initrd into a separate boot directory
with the already tested IR-only DT. It adds a unique GRUB entry and installs
only the separately extracted 552-byte sensor firmware. No module is installed
into Golden's module tree. `arm` requires the exact candidate to be pushed and
uses grub-reboot, preserving the saved Golden default.

`capture` consumes its identity before module loading, arms a 120-second Golden
return timer, discovers media/subdevice nodes, and attempts exactly one four-frame
Y10P/644x604 stream with a 20-second userspace timeout. All strobe outputs remain
disabled. No camera application, authentication service or illuminator is enabled.
Raw frames stay local. `retire` removes only hash-matching candidate files after
Golden has returned. A failure is evidence, never permission for a same-boot retry.

## Acceptance

Four complete ordinary-memory RAW10 frames, nonzero payload, confirmed sensor
start and software-standby stop, no kernel warning/fault, sensor runtime suspend,
Golden return, and candidate retirement. This establishes bounded transport only.
Exposure control, sustained/repeated capture, image quality, libcamera processing,
app integration, illumination, face authentication, and suspend/resume are still
separate acceptance milestones.

## Validation before runtime

Native module and unchanged CAMSS compile with W=1; native C/header pass strict
checkpatch with zero errors/warnings/checks. Existing E004eo readiness verification
passed before this work. See evidence/BUILD-MANIFEST.json for exact source and
module/firmware/DT hashes. Golden kernel/initrd hashes are recorded at installation.

## Sources

- Same-machine board authority: E004a, E004i, E004w and E004y.
- ST GPIO and stream protocol: vendored public driver at a05627b0f6d8775aa54b6fa306e91f425f2cbf9e.
- https://github.com/STMicroelectronics/vd55g0-linux-driver
- https://docs.kernel.org/driver-api/media/camera-sensor.html
- https://docs.libcamera.org/master/libcamera_architecture.html
