# E012G — bounded rear exposure ladder optical one-shot

E012F proved the same SP7 screen geometry/scene reaches Linux correctly (coarse Windows-vs-Linux correlation ~0.91) but remains severely underexposed even at the previously tested fixed rear profile. E012G therefore tests a bounded standard-V4L2 exposure/gain ladder instead of more OEM archaeology.

The fresh candidate keeps exposure at 3200 lines (<= fixed 4K 30-fps max 3206) and digital gain at 2048 while stepping analogue gain only through 512, 1024 and 2048 after the exact baseline 1600/128/1024. Every tuple is checked against live advertised bounds. The candidate measures native product-loopback NV12 Y after each step, stops when p95 reaches at least 120 without clipping, backs down if p99>=230 or >=0.5% of Y clips, captures one root-private 4K render, restores the exact baseline, turns rear off and returns Golden. No VBLANK/FPS change, direct register write, IR/illumination, AI/effect, or long soak is permitted.

## Actual result

The fresh E012G ladder completed and returned protected Golden cleanly. Native product-loopback Y rose from baseline mean30.20/p99=31 to p1 34.61/55 and p2 39.79/80. Raising analogue gain again from 1024 to 2048 produced no material increase (p3 mean39.77/p99=80), with no clipping. The private p3 4K render visibly resolves the SP7 Windows desktop but remains substantially too dark (RGB-luma mean25.10/p95=58/p99=72) versus the same-night OEM Windows rear native NV12 mean56.99/p95=152/p99=160. Exact baseline controls were restored, rear selected off, service stopped, no soak started. This isolates the next bounded experiment to digital gain rather than more analogue gain or OEM metadata archaeology.
