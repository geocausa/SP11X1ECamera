# E011LK — zero bucket-chain lookup frontier

PASS. The newly published bucket node has a null chain head; the original `0x5E8740` lookup returns null, caller `x24` becomes zero, and execution stops at `0x5E84B0` before value-node allocation.

NEXT E011LL allocates the value node and key storage, copies the normalized key, and stops before `0x5E8584 -> 0x5E8830`.
