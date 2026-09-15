# E004es: native IR RAW10, corrected receiver mapping

Fresh successor to the consumed and retired E004er. Same native sensor source,
firmware, CAMSS source, ordinary CSID0/VFE0 RDI0 route, and four-frame capture.

The DT now uses the E004v 8 KiB CSIPHY0 aperture already tested by E004w.
The independent validate_dtb.py preflight runs at build, install, arm and runtime.
Its regression test accepts E004v and rejects the stale E004o 4 KiB DT.

The command runner uses regular-file output and bounded child reaping, so an
oops-induced task stuck in kernel close cannot hold a pipe open indefinitely.
A timed-out camera ioctl is followed by evidence capture and Golden return,
without further camera ioctls or any same-boot retry.

Acceptance remains four RAW10 frames, sensor start/stop confirmation, disabled
GPIO outputs, clean kernel, runtime suspend, Golden return and retirement.
Protected runtime and illumination remain inactive. This is transport validation,
not complete camera/face-authentication readiness.
