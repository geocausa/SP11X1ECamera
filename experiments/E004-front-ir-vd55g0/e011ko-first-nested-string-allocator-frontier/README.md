# E011KO — first nested payload string to allocator frontier

PASS. E011KO executes the source-exact string scan beginning at `0x5B999C` over the source-qualified first nested payload name at RVA `0x1362948`, derives length 22 and exactly 23 bytes including NUL, and stops before `0x5B99CC -> 0xCAE740`.

NEXT E011KP executes the accepted process-heap allocator for those 23 bytes and stops before its result branch. No new camera Start, reboot, rear runtime, or kernel build is used.
