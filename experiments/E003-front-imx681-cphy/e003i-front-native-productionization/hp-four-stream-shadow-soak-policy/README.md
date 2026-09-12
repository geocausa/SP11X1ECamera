# E003i-HP — bounded four-stream shadow soak policy

Status: **PASS / offline only**.

HO proved two sequential production streams after the snapshot-generation reset fix. HP scales only one dimension: lifecycle repetition. The next bounded soak is exactly **4 sequential streams × 27 frames = 108 frames** in post-G3 `shadow` mode, with zero post-G3 native writes authorized.

Every stream must begin with fresh snapshot generation 1, complete the existing 24 producer generations / 23 R5..R27 submissions, perform exactly three startup sensor writes, and end with `STREAMOFF_OK`. The harness aborts on the first failure; no later stream, same-stream retry, or same-boot retry is permitted. Any result is archived immediately and followed by Golden reboot.

HO evidence is ~221 MiB per stream. HP requires at least 8 GiB free before arming; four-stream evidence is projected below 1 GiB using HO's measured per-stream size.
