# E011LD — enumeration-global producer to first element call

PASS. Original source at `0x5BEBA8` constructs the writable enumeration-global pair at RVA `0x1766540`: it allocates one 16-byte entry, validates all 62 source descriptors named by static pair RVA `0x1618498`, and publishes source table RVA `0x1617B40`, count 62, with global entry count 1. Replaying the accepted `0x5BA850` method therefore produces caller `SP+0x50/+0x58` with one owned entry. The zero status and nonzero-count branches are qualified and execution stops before `0x5B8778 -> 0x5B9C80`.

NEXT E011LE merges that 62-entry source block into the accepted 169-entry table, closes the one-entry loop, and stops at `0x5B87F8`. No new camera Start, reboot, rear runtime, or kernel build is used.
