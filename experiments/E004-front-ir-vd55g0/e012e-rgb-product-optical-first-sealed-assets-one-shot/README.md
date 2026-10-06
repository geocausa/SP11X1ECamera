# E012E — sealed-asset RGB product optical-first one-shot

E012E is the fresh single-use optical retry after E012D correctly failed before daemon admission. The product installer now removes Python bytecode caches and runtime lock/output state before sealing `PRODUCT-ASSETS.sha256`, and the root daemon runs with `PYTHONDONTWRITEBYTECODE=1` so immutable code assets stay immutable across product admission.

It retains the E012C colorimetry correction: the publishers independently re-read V4L2 output format and validate effective BT.601 semantics, including V4L2 DEFAULT optional fields only when they map to SMPTE170M / 601 / limited / 709.

The first live gate is still optical, not soak: capture one root-private 1920x1080 front render and one root-private 3840x2160 rear render through the actual product service. No repeated switching or long-duration run is allowed until both images have been visually inspected.
