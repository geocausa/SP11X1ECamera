# E003i-HL — fresh repeated-stream shadow R27 candidate

Status: **PREPARED / NOT INSTALLED / UNARMED / no camera runtime.**

HL is the fresh successor to consumed HK. The camera/package policy is unchanged: HJ production artifacts, exactly two sequential 27-frame streams, explicit `shadow` post-G3 policy, zero post-G3 physical writes authorized, and no same-stream retry.

The only intended harness repair is the pre-stream Bash bug found in HK: stream-number assignment now occurs before any expansion that references it. `invoke-twice.sh` is sourceable without executing `main`; an offline self-test overrides only the launcher function and exercises the exact live marker/variable/grep path for streams 1 and 2, including fail-closed marker reuse. ShellCheck and Bash syntax are also mandatory before prearm.

HL uses a new GRUB/cmdline/boot identity and must never reuse HK evidence or boot artifacts.

## Attempt 1 result

HL proved the first full lifecycle leg: stream 1 completed all 27 frames with producer PASS, `shadow` policy, zero post-G3 native writes, clean `STREAMOFF_OK`, and dynamic discovery of `imx681 5-0010`. Stream 2 then exposed a real repeat-stream reset defect. Its producer immediately observed 3A generation **28** while expecting generation **1**; after three completed buffers (sequence 0,1,2), loop 3 received sequence 0 instead of 3 and the helper pinned for reboot. Stream 2 never reached STREAMOFF.

No same-boot retry was performed. The candidate was archived, Golden restored, and the HL identity retired. Final archive manifest SHA256: `ecd96ac7390a8bb873f57555bcdefb70dce92773ff4eaadb0dd954c4b85aebb5`.

The next work is offline reset-ownership analysis, not another live candidate.
