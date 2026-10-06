# E011KN — first descriptor payload to first nested string frontier

PASS. E011KN follows the nonzero 48-byte payload allocation, clears it exactly through `0x5B997C -> 0xF5E600`, publishes it at destination descriptor `+0x10`, preserves source count `2`, and source-qualifies the 48-byte two-element pointer array at RVA `0x16170D8`. The first element selects the NUL-terminated 23-byte span at RVA `0x1362948`; execution stops before `0x5B999C` reads its first byte.

NEXT E011KO scans that first nested string, derives 23 bytes including NUL, and stops before `0x5B99CC -> 0xCAE740`. No new camera Start, reboot, rear runtime, or kernel build is used.
