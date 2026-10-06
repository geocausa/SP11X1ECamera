# E011IO — published enumeration buffer to 0x5F95AC frontier

PASS. E011IO reuses E011DV source authority for the runtime publication at `RVA 0x169FDF0`, executes the original `0x5F95A4` load, confirms the published pointer is nonzero, and proves the `0x5F95A8` zero branch is not taken. It stops before dereferencing published-buffer offset `0x4950`.

NEXT E011IP traces intervening writes from the E011DV zeroed-publication state before qualifying that field. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
