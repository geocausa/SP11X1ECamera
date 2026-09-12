# E003i-GY — consumed minimal changed post-G3 sentinel PASS

Status: **ATTEMPT1 CONSUMED / PASS / Golden return PASS / candidate retired.**

GY executed exactly one fresh 27-frame stream and proved one real changed sensor transaction after G3 while keeping every later source shadow-only.

Results:

- 27/27 frames and continuous scheduler release ownership through G26;
- native G1..G3 physical control path unchanged;
- native G4 was still bit-identical to G3, satisfying the sentinel precondition;
- exactly one G4 sentinel changed digital gain `1471 -> 1472` (+1 register LSB, +0.06798%) after completed G5 for expected effect G7;
- kernel evidence contains exactly five sensor transactions total: bootstrap + G1..G3 + the G4 sentinel;
- post-stream hardware controls retained digital gain 1472, proving no hidden later sensor write;
- G5..G26 were exactly 22 shadow releases;
- clean STREAMOFF and kernel-health PASS;
- producer/IQ R5..R27 PASS, max pipeline 29.180471 ms;
- no same-boot retry;
- protected Golden return PASS and candidate retired.

This closes the **transport/lifecycle** question for a changed post-G3 sensor update. The sentinel is synthetic, not a production AEC decision. Its tiny +0.06798% gain perturbation did **not** cause any later native AEC control tuple to move: G5..G27 remained equal to the saturated G3 tuple. Therefore production native changed-feedback behavior remains the next frontier; GY must not be cited as proof of it.
