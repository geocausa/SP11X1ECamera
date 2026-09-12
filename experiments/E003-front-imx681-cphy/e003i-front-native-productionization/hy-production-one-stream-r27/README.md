# E003i-HY — current-Golden production one-stream R27 candidate

Status: **PASS / consumed / Golden-restored / retired**.

HY is the first production-stream candidate on the exact current-Golden camera DTB. It inherits the proven HW activation boot authority and the HX acceptance contract without broadening sensor-write authority.

Exactly one 27-frame stream is permitted. The launcher is invoked with explicit `shadow` post-G3 policy and a fresh non-existing output directory. The attempt is marked consumed immediately before the single launcher invocation. Expected acceptance is fresh G1 statistics, 24 producer generations / 23 R5..R27 submissions, startup sensor writes G1..G3 only, zero post-G3 native writes, exactly four hardware control transactions including bootstrap, exact QC10C/TLBG/STATS3A sizes, STREAMOFF and kernel health PASS.

There is no same-stream or same-boot retry. After the one attempt the machine must return to protected Golden, the candidate must be retired, and evidence archived. Attempt 1 has now completed under exactly that contract; Golden is restored and the HY candidate has been removed.

## Attempt 1 result

**PASS.** One fresh current-Golden/HV candidate boot executed exactly one 27-frame production stream with explicit `shadow` post-G3 policy. Statistics restarted at generation 1; producer output covered G1..G24 with 23 R5..R27 submissions. Sensor writes were limited to startup G1..G3, with zero post-G3 native writes and four hardware control transactions including bootstrap. All 27 QC10C/TLBG/STATS3A artifacts matched expected sizes, STREAMOFF passed and kernel health remained clean. No retry occurred.

Candidate boot ID: `7334effd-92e9-4cfc-a200-d047bdbabcb7`; Golden return boot ID: `56e2bbd9-e975-4e4e-86fe-b362288cbab9`. Archive: `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hy/attempt1-pass-production-one-stream-r27-20260912T094145`; final manifest SHA256 `e411c04ad30f9b4c9816aa6743ccf137e4a8e552dec4ef2f34a761755008ca63`. Candidate retired.

HY proves one production stream on the exact current-Golden merged camera DTB and activation path. It does **not** prove changed post-G3 native feedback; the stream intentionally remained shadow-only after G3.
