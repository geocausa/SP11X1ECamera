# E011KT — second nested string allocator frontier

PASS. E011KT consumes the second 24-byte nested source element, source-qualifies its NUL-terminated name at RVA `0x1362938`, measures length 15, derives the exact 16-byte allocation request, and stops before `0x5B99CC -> 0xCAE740`.

NEXT E011KU executes the accepted allocator chain for those 16 bytes and stops before the result branch. No new camera Start, reboot, rear runtime, or kernel build is used.
