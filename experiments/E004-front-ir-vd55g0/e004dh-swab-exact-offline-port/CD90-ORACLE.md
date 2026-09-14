# E004dh — Windows `FUN_18001cd90` final-combine reconstruction

Windows remains normative. A debugger was attached to the shipping `QcISPTrustlet8380.dll` while the normal standalone SWASF processor was paused immediately before its real CD90 call. All 13 arguments were dumped at function entry, and the 8-byte destination was dumped again at the exact return address.

The capture is self-consistent: `p13.bin` is byte-identical to the authoritative live Windows 0x804 SWASF tuning payload (SHA-256 `6cc727315a8d640ab40211f031efdfe28f12e8f2be90f8c8a3a785bb63ccfc0c`). The observed destination transition was:

`5a5a5a5a5a5a5a5a -> 00000518293b4c5f`.

The same Windows run also re-dumped CD90's post-processing globals and LUTs after a successful SWASF frame. This proves the active shipping path has `DAT_18003d238..23c == 0`, first-half auxiliary tables `T0=0`, `T1=1`, `T2=0`, and the exact fixed 256-entry small/large LUTs preserved in the oracle directory.

Under that proven runtime state, the active CD90 path reduces cleanly to a lane-local scalar combine:

1. derive the tuning index from `p3 * p11 / 256` with Windows rounding;
2. compute an activity magnitude from `abs(p8)-4`;
3. scale/clamp it using the two SWASF tuning curves and `p12`;
4. select the p4/p5 bound according to the sign of `p8`;
5. derive the blend gain from `abs((p4+p5)-(p6+p7))/4`, the shipping LUTs, and `p9`;
6. blend the bounded and activity values;
7. transfer the sign of `p8`, clamp correction to `[-116,+60]`;
8. add to p1, clamp to `[0,1023]`, and emit `value >> 2`.

`p10` is multiplied by `DAT_18003d239-DAT_18003d23c`, which is zero in the shipping runtime and was independently observed to have no effect in the Windows basis oracle.

`scaffold/sp11-swasf-cd90.c` reproduces the exact self-consistent Windows invocation and builds freestanding for Hexagon v73 with zero unresolved symbols (`420` bytes `.text`). This is still a candidate until the direct randomized shipping-Windows differential passes; `cd90_final_combine_exact` therefore remains false.

## Randomized shipping-Windows closure

A deterministic Windows oracle generated 4,096 initialized CD90 records (32,768 lanes) by calling the shipping `QcISPTrustlet8380.dll` final-combine function directly after normal SWASF initialization. The complete Windows vector set has SHA-256:

`86b1851e1023d4659a50b89ff8f9ace26fe5ec344ee434066e2c5d9887702785`

`verify_cd90_random_vectors.py` feeds every recorded input through `scaffold/sp11-swasf-cd90.c`. Result: **4096/4096 cases, 32768/32768 lanes byte-exact**.

Together with the self-consistent real invocation and active post-processing state capture, this closes `FUN_18001cd90` for the shipping Windows path. The remaining E004dh work is integration of the already-proven SWABF/C3E8/CD90 stages and a full-frame Windows differential; it is no longer reverse engineering of an unknown CD90 transform.
