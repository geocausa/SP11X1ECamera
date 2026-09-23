# E004mv — fresh AArch64 rear 4K temporal opt-in one-shot

UNARMED until the independent fresh source, hardware, tests and Golden
overlap checks finish. This is a brand-new source-locked unique boot
identity: NEVER reuse consumed E004mu or E004mt. User explicitly
authorized continuing project experiments and accepting the risk of
another reboot requiring a physical power-on. Never assume the previous
failed firmware reboot handoff is fixed, or that automatic reboot to
protected Golden guarantees the physical firmware will restart. Never
lower the strict minimum 29fps source acceptance threshold.

Exact same front1080/rear4K ordinary UID1000 app and route, exact native
rear baseline+trial+restore control profile, same sparse native FULL10
source frame pairs, same rear opt-in tone gate and 4K 2x2 temporal luma
history/UV invariance as E004mu. ONLY change: rear temporal 2x2
operation is explicitly compiled using 16-lane AArch64 NEON. All
filtered Y pixels, all historical Y pixels, UV and scalar statistics
are proven byte-for-byte identical to the previous scalar algorithm
across moving/noisy/scene-cut/gap full4K synthetic fixtures.

E004mu filtered137 frames, mean filter CPU3.831ms and combined pipeline
23.695ms but rejected on real 28.8485 source fps; new SIMD camera-free
benchmark around1.1ms on SP11 synthetic fixture, NOT real camera
proof. New physical attempt must independently prove true rear 29fps,
zero source sequence gaps, exact supported sensor controls restored,
front->rear->off, no kernel GPU/display fault, private photo policy,
no native VBLANK/FPS/IR changes, and protected Golden return.
Optical original photos ONLY SP11 owner geoca dir0700/file0600;
NEVER export photo/RAW/thumbnail/image hashes. Failed experiment
consumes identity permanently and remains a FAIL despite CPU gain.
