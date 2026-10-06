# E011LL — value node and key storage frontier

PASS. The accepted insertion path allocates a 24-byte value node and 132 bytes of key storage, clears them, and copies 128 key bytes while leaving four zero tail bytes. It stops at 0x5E8578.

NEXT E011LM copies the four-byte value, links the node into bucket 280, updates counts, and returns to 0x5B8D54.
