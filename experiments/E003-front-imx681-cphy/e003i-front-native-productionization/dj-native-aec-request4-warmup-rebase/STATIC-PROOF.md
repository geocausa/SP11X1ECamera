# DJ static/runtime-evidence proof

- W: stats generation G owns logical Windows request G+3.
- CN: Windows has a distinct synthetic start record and a separate real history list; real history warms naturally.
- DC: ordinary post-convergence requests 1, 2 and 3 each expose all seven compact lanes as `0x01fc4ec4 = 33,312,452`.
- CH: T681 arbitration of 33,312,452 returns gain 1, time 33,312,452 and retained exposure 33,312,452 exactly.
- DI: read-only same-machine post-convergence capture pins `controller+0x14d68` PredGain to `0x3f800000` for requests 1, 2 and 3. DI ZIP SHA256 is `5155e355b08b8c65153d3548568c5223a230e1d88c85711b47f8eef7b11e27b0`.
- AB22: request 1 publishes Lux `0x4365b24a`; requests 2, 3 and 4 publish `0x4365acdd`. AB8/AB26 independently uses `0x4365acdd` as the first three correctly paired Algorithm001 history baselines.

The corrected reduced state starts local frame 0 at internal history frame 3. History frames 0..2 are preseeded as the three real warm-up requests, while `state.next_frame_id` remains local and begins at zero. This changes only the hidden history coordinate, not CU's generation identity.

The exact DB attempt2 G1/G2/G3 STATS3A hashes are pinned in `ORACLE-EVIDENCE.txt`. `verify-dj.py` feeds those bytes through CU→CR/CT→DJ→CV and requires all three to complete, including the prior G3 failure case.
