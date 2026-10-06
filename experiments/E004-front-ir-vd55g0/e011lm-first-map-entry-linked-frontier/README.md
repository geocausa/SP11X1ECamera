# E011LM — first map entry linked frontier

PASS. The four-byte value is copied into key-storage+128, the key-storage pointer is published into the 24-byte value node, that node becomes both head and tail of bucket 280, bucket count and map entry count advance to one, and the insertion helper returns zero to caller 0x5B8D54.

NEXT E011LN resolves the caller runtime globals at 0x160A218/0x1608858 and qualifies the post-insert branch without guessing.
