# E004dh — Windows `FUN_18001c3e8` basis oracle

The shipping Windows `QcISPTrustlet8380.dll` is authoritative.  `SWASF-C3E8-BASIS-ORACLE.ps1` calls `FUN_18001c3e8` directly after the module's normal SWASF init and captures its three scratch outputs for controlled 16×16 signed-16 input images.

The call is intentionally offline: it does not invoke camera hardware, SecureISP runtime capture, or any Linux protected path.

## Captured scratch geometry

The write extents close the scratch layouts for a 16×16 tile:

- `o11`: 544 bytes = **17 × 16 signed-16 values**.
- `o12`: 136 bytes = **17 × 8 unsigned-byte values**.
- `o13`: 256 bytes = **16 × 16 unsigned-byte values**.

The final 17th `o11/o12` row contains edge/tail material; it must not be interpreted as another image row without following the exact caller layout.

## Windows basis behavior

Four input families were captured: constant 512, +256 center impulse, -256 center impulse, and a 256→768 horizontal step.

For the constant input the useful `o11` region is zero while `o12` is 128 and `o13` alternates the little-endian bytes of 0x0200.  Positive and negative impulses produce equal-and-opposite signed responses in the useful `o11` lanes and small symmetric excursions around 128 in `o12`; `o13` remains identical to constant for both isolated impulses.  A horizontal step changes all three products.

This constrains `FUN_18001c3e8` to a fixed separable/intermediate-filter stage rather than the final SWASF nonlinear combine.  Its nested helper `FUN_18001c230` is the arithmetic core and has now been given its own direct Windows basis oracle so that the remaining scalar port can be solved from the shipping implementation rather than guessed from the large vectorized decompile.
