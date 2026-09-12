# E003i-HQ — fresh four-stream shadow R27 soak candidate

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HQ is the bounded HP soak candidate using the unchanged HN production package. It authorizes exactly four sequential 27-frame streams (108 frames total), post-G3 `shadow`, zero post-G3 native writes, and no same-stream or same-boot retry.

Each stream must start exported 3A/TLBG generation at 1, complete 24 producer generations / 23 R5..R27 live submissions, make exactly three startup native sensor writes, and finish with `STREAMOFF_OK`. The harness aborts after the first failure and never consumes later stream markers. Any result is archived immediately and followed by Golden reboot.

Prearm requires at least 8 GiB free. Archive ownership is normalized before manifest hashing. No HQ runtime has occurred.
