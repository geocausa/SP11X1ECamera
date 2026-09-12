# E003i-HQ — fresh four-stream shadow R27 soak candidate

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HQ is the bounded HP soak candidate using the unchanged HN production package. It authorizes exactly four sequential 27-frame streams (108 frames total), post-G3 `shadow`, zero post-G3 native writes, and no same-stream or same-boot retry.

Each stream must start exported 3A/TLBG generation at 1, complete 24 producer generations / 23 R5..R27 live submissions, make exactly three startup native sensor writes, and finish with `STREAMOFF_OK`. The harness aborts after the first failure and never consumes later stream markers. Any result is archived immediately and followed by Golden reboot.

Prearm requires at least 8 GiB free. Archive ownership is normalized before manifest hashing. No HQ runtime has occurred.

## Attempt 1 result

**PASS.** HQ completed exactly four sequential 27-frame streams (108 frames) in one consumed candidate boot. Every stream restarted exported 3A/TLBG generation at 1, produced 24 native generations / 23 R5..R27 submissions, made exactly three startup sensor writes, kept post-G3 policy `shadow` with zero later native writes, and completed `STREAMOFF_OK`. Kernel health passed and the expected 16 sensor-control transactions including four bootstraps were observed.

No same-stream or same-boot retry occurred. SP11 returned to protected Golden, the HQ identity was retired, and the final archive manifest SHA256 is `a1358953c9dc545c5b5125f4ea4f71d35402391c00c52fe163f98d81822ef545`.

Archive: `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hq/attempt1-pass-four-stream-shadow-20260912T083456`.

This proves bounded **four-stream repeated-open lifecycle robustness** with shadow-only post-G3 control. It does not authorize changed post-G3 native feedback or claim indefinite soak/runtime parity.
