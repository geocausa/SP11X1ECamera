# E003h 0055 — CAMNOC RT rate telemetry

Fresh bounded runtime derived byte-for-byte from the consumed 0054 camera assets. 0055 makes **no camera programming change**. Its sole new behavior is read-only sampling of the X1E CAM_CC CAMNOC RT RCG and branch through `/dev/mem` while the existing 0054 helper executes exactly once.

Windows same-machine KD established `CAM_CC + 0x138fc = 0x00000203` and `CAM_CC + 0x13910 = 0x00000001` during a successful stock front-camera stream, repeated identically. Linux `camcc-x1e80100.c` defines the corresponding legal rate as 300 MHz.

Gate: if Linux observes live `CFG=0x203` and branch enabled, close CAMNOC rate as noncausal. Otherwise freeze the concrete mismatch before any programming change.
