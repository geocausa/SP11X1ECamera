# E003i-HX — production one-stream acceptance policy

Status: **PASS / offline only**.

HW proved that the exact current-Golden/HV boot authority can bind the stable production modules and discover the accepted front route without streaming. HQ already proved the unchanged production capture path across four sequential R27 streams. HX combines those authorities into a deliberately narrow first-stream policy for the **current-Golden merged DTB**.

A future candidate may execute exactly one 27-frame production stream. It must use a fresh output directory, default `shadow` post-G3 policy, fresh statistics generation 1, 24 producer generations / 23 R5..R27 submissions, exactly three startup sensor writes (G1..G3), zero post-G3 native sensor writes, and exactly four hardware control transactions including bootstrap. All 27 QC10C, TLBG and STATS3A files must have the HQ-proven sizes; STREAMOFF and kernel health must pass.

No same-stream or same-boot retry is authorized. The candidate must return to protected Golden and be retired after the single attempt whether it passes or fails. This stage does not create or arm a live candidate.
