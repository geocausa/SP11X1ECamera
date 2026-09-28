# E009f — exact crop-width ratio hypothesis for first AF zoom

Status: **INDEPENDENT GEOMETRY MATCH; UPSTREAM PRODUCER UNPROVEN; NO RUNTIME**.
Parent E009e `b1c7ae47d4b4efcbc7392f0eaad5662f4f3d03d3`.

The E009e first-normal AF zoom bit pattern 0x3F7F3F0F equals the
single-precision result of **4064 / 4076** exactly. The numerator is
the independently accepted rear CAMIF/ISP crop width, and the denominator
is the independently proven OV13858 full RAW sensor width. This is a
strong geometric explanation for the one-call transient, with settled
zoom 1.0 after the crop is established. It is **not yet proof** that
CamX calculates the zoom by this expression: the upstream writer of
AF parameter case 0x15 and its request timing still need source tracing
or a direct pre-AF producer observation.

`initial-zoom-candidate.h` is a small fail-closed, offline width-ratio
candidate. `compile-check.c` verifies its exact float32 bits and rejects
invalid geometries. `audit-private.py` uses the ratio as the first-normal
input to E009e's source-forward AF/BAF/BF composer and compares only safe
aggregate counts against the original private DMI: startup0–3 plus one
sampled steady are each 300/300 bytes. No captured ROI byte or coordinate
is used as generator input. Neither this helper nor E009e has a kernel
runtime call site.

Next: trace the writer of `af_core_set_param` case 0x15 into AF state
+0x1A4D8 and the initial sensor/crop metadata stage. Verify both operands
and transition to 1.0 at the producer before promoting the ratio to
Linux request policy. The other first-frame 3A seed families and native
VFE1 BF/WM16 IRQ/DMA lifetime remain independent runtime gates.
