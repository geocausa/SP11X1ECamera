# E003i-HY — current-Golden production one-stream R27 candidate

Status: **installed / unarmed / no runtime**.

HY is the first production-stream candidate on the exact current-Golden camera DTB. It inherits the proven HW activation boot authority and the HX acceptance contract without broadening sensor-write authority.

Exactly one 27-frame stream is permitted. The launcher is invoked with explicit `shadow` post-G3 policy and a fresh non-existing output directory. The attempt is marked consumed immediately before the single launcher invocation. Expected acceptance is fresh G1 statistics, 24 producer generations / 23 R5..R27 submissions, startup sensor writes G1..G3 only, zero post-G3 native writes, exactly four hardware control transactions including bootstrap, exact QC10C/TLBG/STATS3A sizes, STREAMOFF and kernel health PASS.

There is no same-stream or same-boot retry. After the one attempt the machine must return to protected Golden, the candidate must be retired, and evidence archived. The exact candidate is now installed under `/boot/sp11-7.1.5-camera-e003i-hy-prod-stream-r27` but remains unarmed (`next_entry` empty); no runtime has occurred.
