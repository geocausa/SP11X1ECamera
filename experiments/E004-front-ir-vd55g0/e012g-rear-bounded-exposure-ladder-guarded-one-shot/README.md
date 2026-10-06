# E012G — bounded rear exposure ladder optical one-shot

E012F proved the same SP7 screen geometry/scene reaches Linux correctly (coarse Windows-vs-Linux correlation ~0.91) but remains severely underexposed even at the previously tested fixed rear profile. E012G therefore tests a bounded standard-V4L2 exposure/gain ladder instead of more OEM archaeology.

The fresh candidate keeps exposure at 3200 lines (<= fixed 4K 30-fps max 3206) and digital gain at 2048 while stepping analogue gain only through 512, 1024 and 2048 after the exact baseline 1600/128/1024. Every tuple is checked against live advertised bounds. The candidate measures native product-loopback NV12 Y after each step, stops when p95 reaches at least 120 without clipping, backs down if p99>=230 or >=0.5% of Y clips, captures one root-private 4K render, restores the exact baseline, turns rear off and returns Golden. No VBLANK/FPS change, direct register write, IR/illumination, AI/effect, or long soak is permitted.
