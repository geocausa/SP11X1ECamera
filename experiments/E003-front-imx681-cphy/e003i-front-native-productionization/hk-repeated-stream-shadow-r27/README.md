# E003i-HK — fresh repeated-stream shadow R27 candidate

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HK is the first runtime candidate built from the reproducible HJ package rather than the experiment transform chain. It has a fresh GRUB/boot identity and authorizes exactly **two sequential 27-frame streams** in one candidate boot. Both launcher invocations are pinned to `shadow`; **zero post-G3 native physical writes are authorized**. Each stream still uses the already-proven bootstrap plus G1..G3 startup sensor-control sequence.

The purpose is lifecycle validation only: prove STREAMON/OFF can complete twice with the same loaded production modules and staged install image, with dynamic media discovery on each launch. It does not resume the brighter-scene native-feedback gate.

No same-stream retry is allowed. If either stream fails, archive immediately and return to Golden. On two-stream success, archive, reboot directly to Golden, verify rollback, retire the candidate identity and finalize the archive.

## Attempt 1 result

The one-shot boot was consumed, but **no camera stream started**. `invoke-twice.sh` failed before creating either per-stream consumed marker because Bash expanded `$n` in a same-line `local` declaration before assigning `n` while `set -u` was active. There was no STREAMON/STREAMOFF, producer pass, sensor-control transaction, or 27-frame completion evidence. No same-boot retry was performed. Evidence was archived, the machine returned cleanly to Golden, and the HK boot identity was retired.

HK must never be reused. The successor must fix the harness under a fresh identity and add an offline regression proving both marker creation and command dispatch reachability without touching camera devices.
