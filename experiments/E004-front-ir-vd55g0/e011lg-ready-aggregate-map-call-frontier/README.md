# E011LG — ready descriptor aggregate to map-helper call

PASS. Starting from the accepted ready=1 231-descriptor state, E011LG executes the exact tail/count scan. Exactly 147 descriptors have tail `0xFFFFFFFF`; their nested counts sum to 350. The caller materializes the exact 24-byte input at `SP+0x80` with aggregate 350, tag `0x8000000000`, stride 4 and zero tail, sets `x0=SP+0x80`, and stops before `0x5B8BC4 -> 0x5E81B8`.

NEXT E011LH executes that helper, qualifies its 0x40-byte object and 2800-byte entry array, stores the returned object at caller `+0x30`, and stops at `0x5B8BCC`. No new camera Start, reboot, rear runtime, or kernel build is used.
