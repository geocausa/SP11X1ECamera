# E012H — bounded rear digital-gain ladder optical one-shot

E012G established that analogue gain plateaus: raising OV13858 analogue gain from 1024 to 2048 at exposure 3200 / digital gain 2048 produced essentially no output change. The same SP7 desktop remains geometrically correct but too dark versus the same-night Windows OEM rear baseline.

E012H is a fresh single-use product candidate that holds the accepted 4K 30-fps timing fixed, holds exposure at 3200 and analogue gain at 1024, then steps only the standard V4L2 digital gain through 2048, 4096, 8192 and 16384 after measuring the exact baseline 1600/128/1024. Every tuple is checked against live advertised bounds. It stops once p95 reaches at least 120 without clipping, or backs down one step if p99>=230 or >=0.5% of Y clips. One root-private 4K render is captured, the exact baseline is restored, rear is turned off, and protected Golden is restored.

No VBLANK/FPS change, raw register write, IR/illumination, AI/effect, direct tone transform or soak is permitted. If digital gain also plateaus below the Windows target, the next work item becomes Windows-oracle ISP/tone/colour extraction rather than more sensor-gain brute force.
