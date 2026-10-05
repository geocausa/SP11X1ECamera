# E011FR: current `0x6BD48` frame to `0xEDD0` frontier

Status: **PASS_6BD48_TO_EDD0_FRONTIER**.

E011FR executes the accepted `0x6BE08 -> 0x6BD48` call under the current formatter tuple. The original `0x6BD48` prologue enters at outer-SP-1696, allocates its 80-byte frame to outer-SP-1776, preserves the incoming frame/return pair, and performs the exact six argument saves.

Across four retained placements, all eight 8-byte local-save chunks are checked at their exact source sites and values. Execution reaches untouched `0x6BD6C -> 0xEDD0` and stops before `0xEDD0`; 2,184 current-path altered contracts plus the inherited 264 producer-API mutations are rejected.

No new camera Start, reboot, kernel build, or rear runtime was needed. NEXT **E011FS** executes the already source-pinned `0xEDD0` leaf under this current frame and qualifies its exact return/result at `0x6BD70`. Native rear runtime remains denied.
