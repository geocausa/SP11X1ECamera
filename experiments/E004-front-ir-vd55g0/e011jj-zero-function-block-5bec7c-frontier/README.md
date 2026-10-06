# E011JJ — zero function block to 0x5BEC7C frontier

PASS. E011JJ reuses accepted E011DH initialization authority for global object `RVA 0x17A70D0`: all seven qword slots at `+0xA0..+0xD0` are zero. The selected-mode population block is bypassed on the accepted selector-zero path, so original loads remain zero and the first null check at `0x5BEA90` branches to `0x5BEC7C`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JK follows the null-block path only to its first new source dependency.
