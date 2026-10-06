# E011KL — first descriptor name copy to payload allocator frontier

PASS. E011KL executes the exact bounded `0x5B9940 -> 0xCAE7C0` copy, places all 42 bytes of the accepted NUL-terminated descriptor-0 name into the owned string buffer, returns `0`, and publishes that buffer at destination descriptor `+0x0`. It then reads source count `2`, applies the source element width `0x18`, derives exactly `0x30` (48) bytes, and stops before `0x5B9968 -> 0xCAE740`.

NEXT E011KM executes the accepted process-heap allocation for those 48 bytes and stops before its result branch. No new camera Start, reboot, rear runtime, or kernel build is used.
