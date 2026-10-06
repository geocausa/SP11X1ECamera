# E011LN — post-insert native-global branch frontier

PASS. Reusing already accepted same-boot Windows authority, RVA 0x160A218 is zero and RVA 0x1608858 is one. The bit-16 test falls through, the fallback nonzero branch is taken, logging is skipped, and execution reaches 0x5B8DAC.

NEXT E011LO closes the first descriptor iteration and advances to descriptor position 1 at 0x5B8BEC.
