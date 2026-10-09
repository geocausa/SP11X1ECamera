# Compact fixed-mode rear AEC metadata prototype

QXA2 is an experimental versioned format, not an assigned upstream FourCC.
The96-byte little-endian identity header preserves stream/owner/generation,
sequence, driver-completion time and discontinuity checks. Payload length
slots are81920,0,0,0,0,0; mask namesWM11 only; bit4 identifies the normal32x32
AEC grid. The first four64-bit sum/count fields per80-byte region are admitted
with2205 samples/channel. Extra fields remain uninterpreted.

The producer validates all six original source DMA spans before any output.
Original exact-owner/completion/replacement and all-four-stop policies stay.
Only the active prefix is read/copied; absent planes are not manufactured.
Kernel and userspace use the identical algorithm. Guard-page tests prevent
hidden reads of the tail or absent planes; receiver rejects legacy QXR1.

build66.py creates a fresh source-only stage from hash-verified73 baseline
sources plus published measured63 tuning. It retains a local baseline profile
dependency; this is not yet a clean upstream source distribution.
build-lib66.py clones the pinned libcamera base and records all staged/output
hashes. install66.py verifies those and prepares an unarmed one-shot; never
reuse an installed/consumed identity. run66.py requires all native lifetime
proofs and keeps every pixel/statistics payload on SP11.
