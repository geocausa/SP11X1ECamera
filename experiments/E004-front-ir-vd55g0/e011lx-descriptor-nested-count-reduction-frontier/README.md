# E011LX — descriptor nested-count reduction

PASS. The original caller reduces the accepted 231-descriptor registry table to exactly **519 nested metadata elements**, stores that count at caller object RVA `0x1733E20 + 0x12C8`, and takes the `<1200` path to the second `0x5B80A8` registry-helper call at `0x5DE948`. Existing caller counts are 282 and 239, so the eventual combined total is 1040.

NEXT E011LY reuses the already-closed registry-helper return authority and verifies the caller's exact 519-entry vendor-tag flattening loop.
