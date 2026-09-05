# E003i-Z — paired live TL_BG + 3A bounded runtime

Status: **prepared/unarmed**.

This one-shot is the runtime validation for public Stage Y commit `9ec9ae4`. It preserves the already-proven U six-frame front path, R4-before-STREAMON timing, same-fd live R5/R6 submission, accepted IMX681/front-only DT, hardened Golden-derived kernel command line, one helper invocation, no same-boot retry and mandatory Golden return.

The only functional addition is observation of the new read-only 3A V4L2 control (`USER_BASE+0x1242`) supplied by CAMSS module SHA256 `42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b`.

After every DQBUF the helper reads both controls and requires exact identity equality:

- TL_BG snapshot: `0xF020` bytes (`32 + 0xF000`).
- 3A snapshot: `0x51040` bytes (`64 + 0x51000`).
- expected generations/source sequences: `1,2,3,4,5,6`.
- expected slots: `0,1,0,1,0,1`.
- each 3A `(generation, source_seq, slot)` must exactly equal the TL_BG tuple from the same completed frame.

The 3A header additionally validates exact payload layout: AEC_BE `0x14000`, BHist `0x1000`, AWB_BG `0x3c000`.

Runtime success is not claimed by this package. After one invocation, archive all evidence and return to persistent Golden before offline content analysis. No Lux/CCT algorithm or live-LSC substitution is executed here.
